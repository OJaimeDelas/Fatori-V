# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/fault_injection.py
# -----------------------------------------------------------------------------
# Fault Injection controller (console + timing + area profiles).
#
# Behavior
#   • Driven mode (campaign active): profiles own scheduling; UART TX is a
#     hot path. RX is consumed by a single background thread that timestamps
#     lines and prints them (printing may lag). Logging uses the EventLogger’s
#     deferred storage and is not written to disk until session close.
#   • Manual mode: console is fully interactive. The '>' prompt is printed
#     only after a short quiet window to keep it below incoming SEM lines.
#
# Design
#   • Single RX consumer: the background printer is the only reader of the
#     transport queue during campaigns. Any prompt-synced operations (preflight
#     'S', initial 'I'/'O') temporarily gate the printer to avoid double reads.
#   • Time profiles send with TX-first semantics (no per-shot waits). An
#     optional ack-gated mode can be enabled by a time profile; the RX printer
#     detects completion (SC 00) and signals an event the profile may wait on.
#     Timing profiles themselves do not read from RX.
#   • Logging stays in memory (deferred) and flushes on close.
#
# Presentation controls
#   • Header style and help-section visibility are configurable via CLI flags.
#   • When orchestrated (fatori-v.py), the simple header can be requested and
#     help-heavy sections suppressed.
#
# Additions in this revision
#   • Printing of Area/Time profile arguments is filtered to only display
#     user-facing knobs from the YAML. Internal/derived keys are hidden
#     (e.g., ebd_file, board, run_name, session_label).
#   • --on-end {manual|exit}: on profile finish or arming failure, either
#     switch to manual (default) or auto-exit the process cleanly.
#   • Auto-exit implementation no longer uses SIGINT (which caused a visible
#     KeyboardInterrupt traceback). Instead, an internal event is signaled and
#     the main loop polls it without blocking on input(), ensuring graceful
#     shutdown with exit code 0 and proper log/transport close.
# =============================================================================

from __future__ import annotations

import argparse
import sys
import threading
import time
import importlib
import secrets
import re
import collections
import os
import select
from typing import Optional, Dict, Deque, Callable, Tuple, List

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol
from fi.log import EventLogger
from fi.core.injector import ensure_idle, go_observe, status as status_query
from fi.console import console_settings as cs


# ---------- console echo helpers --------------------------------------------
def _info(msg: str) -> None:
    """
    Print an INFO-class line using console styles.
    The prefix is provided by console_settings to keep the visual identity
    consistent with the rest of the console output.
    """
    print(cs.colorize(f"{cs.PREFIX_INFO}{msg}", cs.TAG_INFO))

def _error(msg: str) -> None:
    """
    Print an ERROR-class line using console styles.
    """
    style = getattr(cs, "TAG_ERROR", cs.SECTION_HEADER_STYLE)
    prefix = getattr(cs, "PREFIX_ERROR", "[ERROR] ")
    print(cs.colorize(f"{prefix}{msg}", style))

def _tx_echo(cmd: str) -> None:
    """
    Echo a TX line (command sent to SEM) on the console with the TX tag style.
    """
    print(cs.colorize(f"{cs.PREFIX_TX}{cmd}", cs.TAG_SEND))

def _rx_echo(line: str) -> None:
    """
    Echo an RX line (SEM reply) on the console with the RX tag style.
    """
    print(cs.colorize(f"{cs.PREFIX_RX}{line}", cs.TAG_RECV))

def _rule(ch: str, n: int) -> str:
    return ch * n

def _print_rule_big(style: str | None = None) -> None:
    """
    Print a full-width rule for major section transitions.
    """
    print(cs.colorize(_rule(cs.BIG_LINE_CHAR, cs.LINE_WIDTH), style or cs.BIG_LINE_STYLE))

def _print_rule_small(style: str | None = None) -> None:
    """
    Print a thin rule for minor separations.
    """
    print(cs.colorize(_rule(cs.SMALL_LINE_CHAR, cs.LINE_WIDTH), style or cs.SMALL_LINE_STYLE))

def _center(text: str, width: int) -> str:
    """
    Center a text within a given width for banner titles.
    """
    if len(text) >= width: return text
    pad = (width - len(text)) // 2
    return " " * pad + text


# ---------- RX activity tracker for manual prompt gating ---------------------
class _RxState:
    """
    Tracks time since last RX line. Manual prompt waits for a quiet gap so
    it does not interleave with bursts of SEM replies.
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last = time.monotonic()
    def bump(self) -> None:
        with self._lock:
            self._last = time.monotonic()
    def millis_since_rx(self) -> float:
        with self._lock:
            return (time.monotonic() - self._last) * 1000.0


# ---------- TX activity tracker for manual prompt gating ---------------------
class _TxState:
    """
    Tracks time since last *manual* TX. This is optionally included in the
    quiet-window condition when printing the manual prompt.
    """
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last = time.monotonic()
    def bump(self) -> None:
        with self._lock:
            self._last = time.monotonic()
    def millis_since_tx(self) -> float:
        with self._lock:
            return (time.monotonic() - self._last) * 1000.0


def _wait_quiet_then_prompt(rx_state: _RxState, quiet_ms: int, max_wait_ms: int,
                            tx_state: Optional[_TxState] = None) -> None:
    """
    Print '>' after a brief quiet window. Quiet condition:
      • RX silent for >= quiet_ms; and
      • if tx_state is provided, TX also silent for >= MANUAL_PROMPT_TX_QUIET_MS.
    This keeps prompt placement visually below any reply bursts.
    """
    try:
        tx_quiet_ms = int(getattr(cs, "MANUAL_PROMPT_TX_QUIET_MS", quiet_ms))
    except Exception:
        tx_quiet_ms = quiet_ms

    t0 = time.monotonic()
    while True:
        rx_ok = (rx_state.millis_since_rx() >= quiet_ms)
        tx_ok = True if tx_state is None else (tx_state.millis_since_tx() >= tx_quiet_ms)
        if rx_ok and tx_ok: break
        if (time.monotonic() - t0) * 1000.0 > max_wait_ms: break
        time.sleep(0.02)
    print(cs.PROMPT_MANUAL, end="", flush=True)


# ---------- ACK tracker (fed by RX printer; waited by profiles) -------------
class _AckTracker:
    """
    Detect completion for an injection based on status code:
      SC 00 -> completed
    The RX printer feeds on_rx(); a time profile may call start() then wait().
    """
    _RE_SC = re.compile(r'^SC\s+([0-9A-Fa-f]{2})$')

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._pending = False
        self._event = threading.Event()

    def start(self) -> None:
        with self._lock:
            self._pending = True
            self._event.clear()

    def on_rx(self, line: str) -> bool:
        """
        Feed a received line to the tracker.
        Returns True only when a pending injection is confirmed completed by SC 00.
        """
        with self._lock:
            if not self._pending:
                return False
            m = self._RE_SC.match(line)
            if not m:
                return False
            try:
                val = int(m.group(1), 16)
            except ValueError:
                return False
            if val == 0x00:
                self._pending = False
                self._event.set()
                return True
            return False

    def wait(self, timeout_s: float) -> bool:
        """
        Block until SC 00 for a pending injection or timeout.
        """
        return self._event.wait(timeout_s)


# ---------- TX echo gate for injections (presentation-only) ------------------
class _TxEchoGate:
    """
    Organizes *printing* (not sending) of TX echoes for injections to keep
    console sequence readable per injection without changing real TX pacing.

    When enabled, the '[SEND]' echo for an injection is printed after the
    matching 'SC 00' is observed. This keeps interleaving readable.
    """
    def __init__(self, print_func: Callable[[str], None]) -> None:
        self._print = print_func
        self._lock = threading.Lock()
        self._queue: Deque[str] = collections.deque()
        self._printed = 0
        self._completed = 0

    def send_echo(self, text: str) -> None:
        with self._lock:
            if self._printed <= self._completed:
                self._print(text); self._printed += 1
            else:
                self._queue.append(text)

    def on_sc00(self) -> None:
        with self._lock:
            self._completed += 1
            if self._queue and self._printed <= self._completed:
                self._print(self._queue.popleft()); self._printed += 1


# ---------- parse helpers ----------------------------------------------------
def _parse_kwargs(csv: Optional[str]) -> Dict[str, str]:
    """
    Parse a CSV-form key=value list into a dict. Bare flags are interpreted
    as 'true' strings for convenience in CLI usage.
    """
    if not csv: return {}
    out: Dict[str, str] = {}
    for part in csv.split(","):
        part = part.strip()
        if not part: continue
        if "=" in part:
            k, v = part.split("=", 1)
            out[k.strip()] = v.strip()
        else:
            out[part] = "true"
    return out


# ---------- dynamic loaders --------------------------------------------------
def _load_area(name: str, kwargs: Dict[str, str]):
    """
    Dynamically import fi.area.<name> and instantiate its Profile with kwargs.
    """
    mod = importlib.import_module(f"fi.area.{name}")
    cls = getattr(mod, "Profile")
    return cls(**kwargs)

def _load_time(name: str, *, proto, log, area, pause_evt, stop_evt, tx_echo, ack_tracker, kwargs: Dict[str, str]):
    """
    Dynamically import fi.time.<name> and instantiate its Profile with the
    shared wiring (protocol, logger, area, control events, tx echo function,
    ack tracker) plus profile-specific kwargs.
    """
    mod = importlib.import_module(f"fi.time.{name}")
    cls = getattr(mod, "Profile")
    return cls(proto=proto, log=log, area=area,
               pause_evt=pause_evt, stop_evt=stop_evt,
               tx_echo=tx_echo, ack_tracker=ack_tracker, **kwargs)


# ---------- header/help (console-style banner) -------------------------------
def _print_console_header_and_help(*, start_mode_label: str,
                                   header_style: str,
                                   show_console_cmds: bool,
                                   show_sem_cheatsheet: bool,
                                   show_start_mode: bool) -> None:
    """
    Print the console header using the theme and visibility controls.
    Two styles are supported:
      • 'fancy'  : original centered banner + optional help sections.
      • 'simple' : thin rules and a left-aligned "SEM Console" title only.
    """
    style = (header_style or getattr(cs, "HEADER_STYLE_DEFAULT", "fancy")).lower()

    if style == getattr(cs, "HEADER_STYLE_SIMPLE", "simple"):
        # Minimal banner for orchestrated runs.
        _print_rule_small()
        print(cs.colorize("SEM Console", cs.HEADER_TITLE_STYLE))
        _print_rule_small()
        return

    # Fancy banner (original behavior, gated by visibility toggles)
    _print_rule_big()
    title = _center("FATORI-V — SEM Console", cs.LINE_WIDTH)
    print(cs.colorize(title, cs.HEADER_TITLE_STYLE))
    _print_rule_big()

    if show_console_cmds:
        print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
        print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
        _print_rule_small()

    if show_sem_cheatsheet:
        print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
        print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
        _print_rule_big()

    if show_start_mode:
        print(cs.colorize("Start mode:", cs.SECTION_HEADER_STYLE), start_mode_label)
        print(cs.colorize("  • In driven mode only: help, sem, status, watch, manual, exit.", cs.HELP_BODY_STYLE))
        print(cs.colorize("  • For raw SEM commands, type 'manual'. To return, type 'resume'.", cs.HELP_BODY_STYLE))
        print(cs.colorize("  • Type 'help' anytime for the command list; 'sem' prints the SEM cheatsheet.", cs.HELP_BODY_STYLE))
        _print_rule_big()


# ---------- PT timestamp (YYYY-MM-DD HH:MM) ----------------------------------
def _now_pt_str_minutes() -> str:
    """
    Format current local time (Europe/Lisbon) to minutes resolution for banner.
    """
    try:
        from zoneinfo import ZoneInfo
        import datetime
        tz = ZoneInfo("Europe/Lisbon")
        return datetime.datetime.now(tz).strftime("%Y-%m-%d %H:%M")
    except Exception:
        import datetime
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")


# ---------- status helper ----------------------------------------------------
def _do_status(proto: SemProtocol, log: EventLogger) -> bool:
    """
    One-shot status query ('S') with echo and logging of parsed counters.
    Returns True if any counters were seen.
    """
    log.log_tx("S"); _tx_echo("S")
    s = status_query(proto, log)
    if not s:
        print("<no counters seen>")
        return False
    for k, v in s.items():
        pair = f"{k} {v}"
        log.log_rx(pair); _rx_echo(pair)
    return True


# ---------- rate utilities (cap computation + reconciliation) ----------------
def _compute_platform_max_rate_hz() -> float:
    """
    Compute platform-dependent max injection rate from settings:
      • SEM_ICAP_FMAX_HZ, SEM_FREQ_HZ, SEM_INJECT_LATENCY_US_AT_FMAX,
        INJECTION_RATE_SAFETY_DERATE, INJECTION_RATE_UART_CAP_HZ.
    """
    icap_fmax = float(getattr(settings, "SEM_ICAP_FMAX_HZ", 200_000_000))
    sem_clk   = float(getattr(settings, "SEM_FREQ_HZ", 100_000_000))
    lat_us    = float(getattr(settings, "SEM_INJECT_LATENCY_US_AT_FMAX", 50.0))
    derate    = float(getattr(settings, "INJECTION_RATE_SAFETY_DERATE", 1.0))
    uart_cap  = float(getattr(settings, "INJECTION_RATE_UART_CAP_HZ", 0.0))

    lat_s_at_fmax = max(1e-9, lat_us / 1e6)
    scale = icap_fmax / max(1.0, sem_clk)
    lat_actual_s = lat_s_at_fmax * scale

    max_rate = (1.0 / lat_actual_s) * max(0.0, min(1.0, derate))
    if uart_cap > 0.0:
        max_rate = min(max_rate, uart_cap)
    return max(0.0, max_rate)

def _resolve_requested_rate_hz(time_kwargs: Dict[str, str]) -> Tuple[Optional[float], str]:
    """
    Resolve requested cadence from kwargs (rate_hz preferred; else 1/period_s).
    Returns (rate_hz or None, source_key).
    """
    if "rate_hz" in time_kwargs:
        try:
            return float(time_kwargs["rate_hz"]), "rate_hz"
        except Exception:
            pass
    if "period_s" in time_kwargs:
        try:
            p = float(time_kwargs["period_s"])
            if p > 0:
                return (1.0 / p), "period_s"
        except Exception:
            pass
    return None, "none"

def _reconcile_and_cap_time_kwargs(time_kwargs: Dict[str, str]) -> Tuple[Dict[str, str], Optional[float], Optional[float], Optional[str]]:
    """
    Compare requested cadence to platform cap. Return:
      (new_kwargs, req_rate_hz, cap_rate_hz, cap_info_msg)
    new_kwargs carries consistent rate_hz/period_s values.
    """
    req_rate_hz, _ = _resolve_requested_rate_hz(time_kwargs)
    cap_rate_hz = _compute_platform_max_rate_hz()

    if req_rate_hz is None:
        return dict(time_kwargs), None, cap_rate_hz, None

    eff_rate = min(req_rate_hz, cap_rate_hz) if cap_rate_hz > 0 else req_rate_hz

    cap_info_msg: Optional[str] = None
    if cap_rate_hz > 0 and req_rate_hz > cap_rate_hz:
        eff_period = 1.0 / eff_rate if eff_rate > 0 else 0.0
        cap_info_msg = (f"Requested time rate ({req_rate_hz:.6g} Hz) exceeds platform cap "
                        f"({cap_rate_hz:.6g} Hz). Capping to {eff_rate:.6g} Hz "
                        f"(period {eff_period:.6g} s).")

    new_kwargs = dict(time_kwargs)
    if eff_rate > 0:
        new_kwargs["rate_hz"]  = f"{eff_rate:.12g}"
        new_kwargs["period_s"] = f"{(1.0/eff_rate):.12g}"
    return new_kwargs, req_rate_hz, cap_rate_hz, cap_info_msg


# ---------- preflight connectivity -------------------------------------------
def _preflight_sem(proto: SemProtocol, log: EventLogger,
                   rx_enabled: threading.Event,
                   attempts: int, interval_s: float) -> bool:
    """
    Verify device responsiveness before arming any profiles.
    Sends 'S' repeatedly; succeeds on the first attempt that returns counters.
    The RX printer is temporarily gated off to avoid double-reading.
    """
    ok = False
    for _ in range(max(1, attempts)):
        rx_enabled.clear()
        try:
            ok = _do_status(proto, log)
        finally:
            rx_enabled.set()
        if ok:
            break
        time.sleep(max(0.05, interval_s))
    return ok


# ---------- CLI parsing helpers ----------------------------------------------
def _parse_bool(s: str, default: bool) -> bool:
    """
    Parse a human-friendly boolean from string; fallback to default on errors.
    Accepts: true/false/on/off/yes/no/1/0 (case-insensitive).
    """
    if s is None:
        return default
    v = str(s).strip().lower()
    if v in ("1", "true", "yes", "on"):
        return True
    if v in ("0", "false", "no", "off"):
        return False
    return default


# ---------- display helpers (filter which kwargs are printed) -----------------
def _kvpairs_filtered_area(area_name: str, kwargs: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Return ordered (k,v) pairs to display for the selected area profile, hiding
    internal/derived keys. Only show user-facing YAML knobs.
    """
    name = (area_name or "").strip().lower()
    pairs: List[Tuple[str, str]] = []

    # Generic hidden keys across area profiles
    hidden = {"ebd_file", "board", "run_name", "session_label"}

    def pick(keys: List[str]) -> None:
        for k in keys:
            if k in kwargs and k not in hidden and str(kwargs[k]).strip() not in ("", "None", "null"):
                pairs.append((k, str(kwargs[k])))

    if name == "address_list":
        pick(["path", "mode", "seed"])
    elif name == "device":
        pick(["mode", "seed"])
    elif name in ("module", "modules"):
        # labels may be comma-separated; show it verbatim
        pick(["labels", "root", "mode", "seed"])
    else:
        # Fallback: show only non-hidden keys
        for k in sorted(kwargs.keys()):
            if k not in hidden and str(kwargs[k]).strip() not in ("", "None", "null"):
                pairs.append((k, str(kwargs[k])))
    return pairs


def _kvpairs_filtered_time(time_name: str, kwargs: Dict[str, str]) -> List[Tuple[str, str]]:
    """
    Return ordered (k,v) pairs to display for the selected time profile. Hide
    irrelevant keys (e.g., ack_timeout_s when ack is false).
    """
    name = (time_name or "").strip().lower()
    pairs: List[Tuple[str, str]] = []

    def add(k: str) -> None:
        if k in kwargs and str(kwargs[k]).strip() not in ("", "None", "null"):
            pairs.append((k, str(kwargs[k])))

    if name == "uniform":
        # Prefer to show rate_hz; if not present show period_s.
        if "rate_hz" in kwargs:
            add("rate_hz")
        elif "period_s" in kwargs:
            add("period_s")
        add("duration_s")
        add("max_shots")
        add("startup_delay_ms")
        if "ack" in kwargs:
            add("ack")
            try:
                ack_on = str(kwargs["ack"]).strip().lower() in ("1", "true", "yes", "on")
            except Exception:
                ack_on = False
            if ack_on:
                add("ack_timeout_s")
    elif name == "ramp":
        for k in ("start_hz", "end_hz", "duration_s", "step_hz", "step_every_s", "hold_at_top", "continue_at_top", "startup_delay_ms"):
            add(k)
    elif name == "poisson":
        for k in ("lambda_hz", "duration_s", "startup_delay_ms"):
            add(k)
    else:
        # Fallback: show all simple keys
        for k in sorted(kwargs.keys()):
            add(k)
    return pairs


# ---------- main --------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Fault Injection Controller (console + timing + area profiles).")
    ap.add_argument("--dev", default=settings.DEFAULT_SEM_DEVICE, help="Serial device path")
    ap.add_argument("--baud", type=int, default=settings.BAUDRATE, help="Serial baud rate")
    ap.add_argument("--run-name", default=settings.DEFAULT_RUN_NAME, help="Run name for results/<run_name>/...")
    ap.add_argument("--session", default=settings.DEFAULT_SESSION_LABEL, help="Session/benchmark label")

    ap.add_argument("--area", default="address_list", help="Area profile under fi.area (e.g., address_list)")
    ap.add_argument("--area-args", default="", help="CSV key=val for area profile (e.g., path=...,mode=random,seed=1234)")
    ap.add_argument("--time", default="uniform", help="Time profile under fi.time (e.g., uniform)")
    ap.add_argument("--time-args", default="", help="CSV key=val for time profile (e.g., rate_hz=1.0,ack=true,ack_timeout_s=1.5,startup_delay_ms=80)")

    ap.add_argument("--seed", type=int, default=None, help="Global seed (default: random)")
    ap.add_argument("--preflight-attempts", type=int,
                    default=getattr(settings, "PREFLIGHT_STATUS_ATTEMPTS", 3))
    ap.add_argument("--preflight-interval", type=float,
                    default=getattr(settings, "PREFLIGHT_STATUS_INTERVAL_S", 0.5))

    # --- Presentation controls (defaults come from console_settings) ----------
    ap.add_argument("--header-style",
                    choices=[getattr(cs, "HEADER_STYLE_FANCY", "fancy"),
                             getattr(cs, "HEADER_STYLE_SIMPLE", "simple")],
                    default=getattr(cs, "HEADER_STYLE_DEFAULT", "fancy"),
                    help="Header style: 'fancy' for full banner and help; 'simple' for minimal title.")
    ap.add_argument("--show-console-commands",
                    default=str(getattr(cs, "SHOW_CONSOLE_COMMANDS_DEFAULT", True)).lower(),
                    help="Show the 'Console commands' section (true/false).")
    ap.add_argument("--show-sem-cheatsheet",
                    default=str(getattr(cs, "SHOW_SEM_CHEATSHEET_DEFAULT", True)).lower(),
                    help="Show the 'SEM IP commands' cheatsheet (true/false).")
    ap.add_argument("--show-start-mode",
                    default=str(getattr(cs, "SHOW_START_MODE_DEFAULT", True)).lower(),
                    help="Show the 'Start mode' section (true/false).")

    # --- End-of-campaign behavior --------------------------------------------
    ap.add_argument("--on-end", choices=["manual", "exit"], default="manual",
                    help="What to do when a campaign ends or arming fails.")

    args = ap.parse_args(argv)

    # Normalize booleans after parsing
    header_style = (args.header_style or getattr(cs, "HEADER_STYLE_DEFAULT", "fancy")).lower()
    show_console_cmds = _parse_bool(args.show_console_commands, getattr(cs, "SHOW_CONSOLE_COMMANDS_DEFAULT", True))
    show_sem_cheatsheet = _parse_bool(args.show_sem_cheatsheet, getattr(cs, "SHOW_SEM_CHEATSHEET_DEFAULT", True))
    show_start_mode = _parse_bool(args.show_start_mode, getattr(cs, "SHOW_START_MODE_DEFAULT", True))

    # ----- Global seed determination -----
    global_seed = args.seed if args.seed is not None else secrets.randbits(64)

    # Logger + transport (EventLogger stores entries in-memory until close)
    log = EventLogger(run_name=args.run_name, session_label=args.session,
                      defer=settings.DEFER_LOG_WRITE)

    cfg = SerialConfig(device=args.dev, baud=args.baud)
    tr = SemTransport(cfg)

    try:
        tr.open()
    except Exception as e:
        _error(str(e))
        return 1

    start_reader = getattr(tr, "start_reader", None)
    if callable(start_reader): start_reader()
    log.set_header(device=cfg.device, baud=cfg.baud, sem_freq_hz=settings.SEM_FREQ_HZ)

    proto = SemProtocol(tr);  proto.sync_prompt()

    # ACK tracker fed by RX printer; used only if a time profile asks for ACK gating.
    ack_tracker = _AckTracker()

    # Background RX echo/log (single consumer) + ACK detection
    stop_evt = threading.Event()
    rx_enabled = threading.Event(); rx_enabled.set()
    rx_state = _RxState()
    tx_state = _TxState()

    # Auto-exit event (signaled by arming failure or profile end when requested)
    auto_exit_evt = threading.Event()

    # Injection TX echo gate — presentation-only; can be disabled in settings.
    inj_tx_gate = _TxEchoGate(print_func=lambda text: print(text)) if bool(getattr(cs, "INJECTION_ECHO_GATE_ENABLED", True)) else None

    def _inj_tx_echo(cmd: str) -> None:
        """
        TX echo used by time profiles for injections. If the gate is enabled,
        [SEND] echoes are sequenced after SC 00 for the previous shot.
        """
        if inj_tx_gate is not None:
            inj_tx_gate.send_echo(cs.colorize(f"{cs.PREFIX_TX}{cmd}", cs.TAG_SEND))
        else:
            print(cs.colorize(f"{cs.PREFIX_TX}{cmd}", cs.TAG_SEND))

    def _rx_printer(tr_local: SemTransport, log_local: EventLogger,
                    enabled_evt: threading.Event, stop_flag: threading.Event,
                    rxst: _RxState) -> None:
        """
        Single RX consumer for campaigns. Reads short bursts, feeds ACK tracker,
        logs each line (deferred), and echoes to console. If an SC 00 that
        finalizes an injection is seen and the presentation gate is enabled,
        it releases the next queued [SEND] echo.
        A guard is used so that SC 00 lines unrelated to injections (e.g., from
        status commands) do not trigger [SEND] releases.
        """
        poll_timeout = max(0.02, getattr(cs, "RX_PRINTER_POLL_S", 0.03))
        _RE_SC = re.compile(r'^SC\s+([0-9A-Fa-f]{2})$')
        _RE_I_N = re.compile(r'^\s*I>\s+N\b')  # recognizes "I> N ..." injection echo
        in_inject_context = False              # True after "I> N ..." until the matching SC 00

        while not stop_flag.is_set():
            if not enabled_evt.is_set():
                time.sleep(poll_timeout)
                continue
            lines = tr_local.read_lines(timeout_s=poll_timeout)
            if not lines:
                continue
            for ln in lines:
                # Context tracking for injection completion association
                if _RE_I_N.match(ln):
                    in_inject_context = True

                # Ack tracker returns True only when a pending inject completes
                sc00_from_pending = ack_tracker.on_rx(ln)

                # Detect SC 00 from the monitor
                is_sc00 = False
                m = _RE_SC.match(ln)
                if m:
                    try:
                        is_sc00 = (int(m.group(1), 16) == 0x00)
                    except ValueError:
                        is_sc00 = False

                # Log and echo the RX line
                log_local.log_rx(ln)
                _rx_echo(ln)
                rxst.bump()

                # Release one queued [SEND] only if we are in an injection context
                # and this SC 00 corresponds to the end of that injection.
                if inj_tx_gate is not None and is_sc00 and (in_inject_context or sc00_from_pending):
                    inj_tx_gate.on_sc00()
                    in_inject_context = False

    threading.Thread(
        target=_rx_printer,
        args=(tr, log, rx_enabled, stop_evt, rx_state),
        daemon=True
    ).start()

    # Helper: non-blocking/user-input with auto-exit polling
    def _readline_with_poll(prompt_empty: bool = True) -> Optional[str]:
        """
        Read a line from stdin. If --on-end=exit, poll for auto_exit_evt and
        avoid blocking indefinitely. Returns None if auto-exit is requested
        or on EOF.
        """
        if getattr(args, "on_end", "manual") != "exit":
            # Traditional blocking input
            try:
                return input("")
            except EOFError:
                return None
        # Polling input (POSIX select); checks auto-exit every 100 ms
        if prompt_empty:
            pass  # intentional: driven branch historically used empty prompt
        while True:
            if auto_exit_evt.is_set():
                return None
            r, _, _ = select.select([sys.stdin], [], [], 0.1)
            if r:
                line = sys.stdin.readline()
                if line == "":
                    return None
                return line

    # Banner + help (console-style)
    _print_console_header_and_help(
        start_mode_label="driven",
        header_style=header_style,
        show_console_cmds=show_console_cmds,
        show_sem_cheatsheet=show_sem_cheatsheet,
        show_start_mode=show_start_mode
    )

    # Current run bullets (immutable facts + profile args)
    print(cs.colorize("Currently Running:", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(f"  • run         : {args.run_name}", cs.HELP_BODY_STYLE))
    print(cs.colorize(f"  • session     : {args.session}", cs.HELP_BODY_STYLE))
    print(cs.colorize(f"  • started     : {_now_pt_str_minutes()}", cs.HELP_BODY_STYLE))
    print(cs.colorize(f"  • sem_freq    : {settings.SEM_FREQ_HZ} Hz", cs.HELP_BODY_STYLE))
    print(cs.colorize(f"  • baud/device : {cfg.baud} @ {cfg.device}", cs.HELP_BODY_STYLE))
    print(cs.colorize(f"  • seed (global): {global_seed}", cs.HELP_BODY_STYLE))
    _print_rule_small()

    # Parse profile args; inherit global seed if area has none
    area_kwargs = _parse_kwargs(args.area_args)
    time_kwargs = _parse_kwargs(args.time_args)
    if "seed" not in area_kwargs:
        area_kwargs["seed"] = str(global_seed)

    # Pass run/session for area profiles that want to write artifacts under results/
    area_kwargs.setdefault("run_name", args.run_name)
    area_kwargs.setdefault("session_label", args.session)

    # ----- Platform-aware rate reconciliation & capping (before printing) -----
    time_kwargs, req_rate_hz, cap_rate_hz, cap_info_msg = _reconcile_and_cap_time_kwargs(time_kwargs)

    # Provide full profile context to the logger header (Area/Time before tag list)
    log.set_header(
        area_profile=args.area, area_kwargs=area_kwargs,
        time_profile=args.time, time_kwargs=time_kwargs,
    )

    # If we capped: draw a rule box and log the INFO first
    if cap_info_msg:
        _print_rule_big(cs.SWITCH_RULE_STYLE)
        _info(cap_info_msg)
        _print_rule_big(cs.SWITCH_RULE_STYLE)
        log.log_info(cap_info_msg)

    # Styled profile lines (labels styled; values in green for quick scan)
    label_style = getattr(cs, "SECTION_HEADER_STYLE", None)
    green_style = cs.mkstyle("br_green")
    print(cs.colorize("  • Area Profile: ", label_style) + cs.colorize(f"{args.area}", green_style))
    for k, v in _kvpairs_filtered_area(args.area, area_kwargs):
        print(cs.colorize(f"      {k:<12}: {v}", cs.HELP_BODY_STYLE))
    print(cs.colorize("  • Time Profile: ", label_style) + cs.colorize(f"{args.time}", green_style))
    for k, v in _kvpairs_filtered_time(args.time, time_kwargs):
        print(cs.colorize(f"      {k:<12}: {v}", cs.HELP_BODY_STYLE))
    _print_rule_small()

    # Initial state + optional status on start (this is the only 'S' used here)
    try:
        rx_enabled.clear()

        # Connectivity pre-check (single informational line)
        _info("Sending test messages to verify conection with the board.")

        if cs.START_MODE.lower() == "idle":
            log.log_tx("I"); _tx_echo("I")
            [log.log_rx(ln) or _rx_echo(ln) for ln in ensure_idle(proto, log)]
        else:
            log.log_tx("O"); _tx_echo("O")
            [log.log_rx(ln) or _rx_echo(ln) for ln in go_observe(proto, log)]

        s_verified = True
        if cs.SEND_STATUS_ON_START:
            s_verified = _do_status(proto, log)

        # Visual confirmation block
        dash_cyan = cs.colorize("-" * cs.LINE_WIDTH, cs.mkstyle("br_cyan"))
        dash_red  = cs.colorize("-" * cs.LINE_WIDTH, cs.mkstyle("br_red"))
        msg_white = lambda t: cs.colorize(t, cs.mkstyle("white"))
        msg_green = lambda t: cs.colorize(t, cs.mkstyle("br_green"))
        msg_red   = lambda t: cs.colorize(t, cs.mkstyle("br_red"))

        if s_verified:
            print(dash_cyan)
            print(msg_white("Conection confirmed"))
            print(msg_green(_center("Session Ready to Start", cs.LINE_WIDTH)))
            print(dash_cyan)
        else:
            print(dash_red)
            print(msg_white("Conection with the board was not confirmed"))
            print(msg_red(_center("Session Aborted", cs.LINE_WIDTH)))
            print(dash_red)
            log.log_error("Preflight connectivity check failed: status not confirmed.")
            if getattr(args, "on_end", "manual") == "exit":
                auto_exit_evt.set()
                # Graceful fast-path exit
                stop_evt.set()
                try: tr.close()
                finally: log.close()
                return 2
            return 2

    finally:
        rx_enabled.set()

    # ------- Fill device defaults that area profiles may require --------------
    # These are not printed (hidden by _kvpairs_filtered_area) but ensure that
    # profiles like fi.area.device receive required keys even if the orchestrator
    # did not pass them explicitly.
    if args.area.strip().lower() == "device":
        area_kwargs.setdefault("board", getattr(settings, "ACME_DEFAULT_BOARD", "xcku040"))
        area_kwargs.setdefault("ebd_file", getattr(settings, "EBD_DEFAULT_PATH", "fi/build/acme/design.ebd"))

    # Arm/load profiles
    driven = True
    pause_evt = threading.Event()

    def _switch_to_end_due_to_error(errmsg: str) -> None:
        """
        Handle arming/runtime error based on --on-end policy.
        • manual: print error and switch to manual with quiet-gated prompt.
        • exit  : set auto-exit flag and return to unwind the main loop.
        """
        _print_rule_big(cs.SWITCH_RULE_STYLE)
        _error(errmsg)
        log.log_error(errmsg)
        pause_evt.set()

        if getattr(args, "on_end", "manual") == "exit":
            auto_exit_evt.set()
        else:
            _info("Campaign paused. Fix the issue and type 'resume' to retry arming.")
            nonlocal driven
            driven = False  # set before prompt gating to avoid race
            _wait_quiet_then_prompt(
                rx_state,
                int(cs.MANUAL_PROMPT_QUIET_MS),
                int(cs.MANUAL_PROMPT_MAXWAIT_MS),
                tx_state=tx_state if getattr(cs, "MANUAL_PROMPT_CONSIDER_TX", True) else None,
            )

    try:
        area = _load_area(args.area, area_kwargs)
        time_profile = _load_time(
            args.time,
            proto=proto, log=log, area=area,
            pause_evt=pause_evt, stop_evt=stop_evt,
            tx_echo=_inj_tx_echo, ack_tracker=ack_tracker,
            kwargs=time_kwargs,
        )
        # Profile lifecycle logging is split from INFO
        area_desc = area.describe() if hasattr(area, "describe") else ""
        log.log_prof_area(f"start — {area_desc}")
        _info(f"PROF AREA [{getattr(area,'name','AREA')}] start — {area_desc}")

        # Time-profile start message augmented with visible knobs only.
        # If the time profile offers describe(), use it; otherwise render from filtered kwargs.
        try:
            tp_desc = time_profile.describe() if hasattr(time_profile, "describe") else ""
        except Exception:
            tp_desc = ""
        if not tp_desc:
            try:
                kvs = _kvpairs_filtered_time(args.time, time_kwargs)
                if kvs:
                    tp_desc = ", ".join(f"{k}={v}" for k, v in kvs)
            except Exception:
                tp_desc = ""
        if tp_desc:
            log.log_prof_time(f"start — {tp_desc}")
            _info(f"PROF TIME [{getattr(time_profile,'name','TIME')}] start — {tp_desc}")
        else:
            log.log_prof_time("start")
            _info(f"PROF TIME [{getattr(time_profile,'name','TIME')}] start")

        # Campaign starts immediately.
        time_profile.start()

    except Exception as e:
        _switch_to_end_due_to_error(
            f"Failed to load campaign (area='{args.area}', time='{args.time}'): {e}"
        )
        area = None
        time_profile = None

    # Watcher: when the time profile ends, either switch to manual or auto-exit.
    watcher_fired = threading.Event()
    def _profile_watcher():
        """
        On profile end, switch behavior according to --on-end.
        Additionally, this routine asks the finished profile for a profile-owned
        end-condition message via a standard method:
            end_condition_prompt(reason: str) -> str
        """
        nonlocal driven
        while not stop_evt.is_set():
            tp = time_profile
            if tp is not None and hasattr(tp, "is_alive") and not tp.is_alive():
                if not watcher_fired.is_set():
                    watcher_fired.set()
                    reason = getattr(tp, "finished_reason", None)

                    _print_rule_big(cs.SWITCH_RULE_STYLE)

                    # ----------- Area exhaustion: ask the *area* profile -------------
                    if reason == "area_exhausted":
                        suffix = ""
                        try:
                            if hasattr(area, "end_condition_prompt"):
                                msg = area.end_condition_prompt("exhausted")
                                if isinstance(msg, str) and msg.strip():
                                    suffix = f" {msg.strip()}"
                        except Exception:
                            suffix = ""
                        if not suffix:
                            suffix = " (address list exhausted)"
                        log.log_prof_area("finished")
                        _info(f"Area profile [{getattr(area,'name','AREA')}] finished.{suffix}")

                    # ----------- Time profile completion: ask the *time* profile -------
                    else:
                        suffix = ""
                        try:
                            if hasattr(tp, "end_condition_prompt") and reason:
                                msg = tp.end_condition_prompt(str(reason))
                                if isinstance(msg, str) and msg.strip():
                                    suffix = f" {msg.strip()}"
                        except Exception:
                            suffix = ""

                        if reason:
                            log.log_prof_time(f"finished ({reason})")
                        else:
                            log.log_prof_time("finished")

                        _info(f"Time profile [{getattr(tp,'name','TIME')}] finished.{suffix}")

                    # Manual vs. exit policy
                    if getattr(args, "on_end", "manual") == "exit":
                        auto_exit_evt.set()
                    else:
                        pause_evt.set()
                        log.log_info("Switched to manual mode because the profile finished.")
                        _info("Switched to manual mode because the profile finished.")
                        driven = False  # set before prompt gating
                        _wait_quiet_then_prompt(
                            rx_state,
                            int(cs.MANUAL_PROMPT_QUIET_MS),
                            int(cs.MANUAL_PROMPT_MAXWAIT_MS),
                            tx_state=tx_state if getattr(cs, "MANUAL_PROMPT_CONSIDER_TX", True) else None,
                        )
                break
            time.sleep(0.1)
    threading.Thread(target=_profile_watcher, daemon=True).start()

    # Main interactive loop
    try:
        while True:
            # Auto-exit path: if requested, unwind cleanly without waiting for input.
            if auto_exit_evt.is_set():
                break
            try:
                if driven:
                    cmd = _readline_with_poll(prompt_empty=True)
                    if cmd is None:
                        # EOF or auto-exit request
                        break
                    cmd = cmd.strip()
                    if not cmd:
                        continue

                    # If switched to manual while typing, treat this as manual input.
                    if not driven:
                        if cmd == "exit":
                            return 0
                        if cmd == "help":
                            _print_rule_small()
                            print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
                            print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
                            _print_rule_small()
                            print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                            print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                            _print_rule_small()
                            continue
                        if cmd == "sem":
                            _print_rule_small()
                            print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                            print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                            _print_rule_small()
                            continue
                        if cmd == "resume":
                            _info("Use 'resume' from manual prompt.")
                            continue
                        try:
                            log.log_tx(cmd)
                            _tx_echo(cmd)
                            tx_state.bump()
                            tr.write_line(cmd)
                        except Exception as e:
                            _error(str(e))
                        continue

                    if cmd == "exit":
                        try:
                            stop_evt.set()
                            if 'time_profile' in locals() and time_profile and hasattr(time_profile, "stop"):
                                time_profile.stop()
                        except Exception:
                            pass
                        break
                    if cmd == "help":
                        _print_rule_small()
                        print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small()
                        print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small();  continue
                    if cmd == "sem":
                        _print_rule_small()
                        print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small();  continue
                    if cmd == "status":
                        rx_enabled.clear()
                        try:
                            _do_status(proto, log)
                        finally:
                            rx_enabled.set()
                        continue
                    if cmd == "watch":
                        _info("watch: Ctrl+C to stop")
                        try:
                            while True:
                                if auto_exit_evt.is_set():
                                    break
                                rx_enabled.clear()
                                try:
                                    _do_status(proto, log)
                                finally:
                                    rx_enabled.set()
                                time.sleep(cs.DEFAULT_WATCH_INTERVAL_S)
                        except KeyboardInterrupt:
                            print(); _info("watch: stopped")
                        continue
                    if cmd == "manual":
                        _print_rule_big(cs.SWITCH_RULE_STYLE)
                        _info("Switched to manual mode. Profiles paused. Type raw SEM; 'resume' to return.")
                        driven = False  # set before prompt gating to avoid race
                        _wait_quiet_then_prompt(
                            rx_state,
                            int(cs.MANUAL_PROMPT_QUIET_MS),
                            int(cs.MANUAL_PROMPT_MAXWAIT_MS),
                            tx_state=tx_state if getattr(cs, "MANUAL_PROMPT_CONSIDER_TX", True) else None,
                        )
                        continue
                    _info("Command disabled in driven mode. Type 'manual' to gain control.")
                else:
                    # Manual mode: quiet prompt gating
                    _wait_quiet_then_prompt(
                        rx_state,
                        int(cs.MANUAL_PROMPT_QUIET_MS),
                        int(cs.MANUAL_PROMPT_MAXWAIT_MS),
                        tx_state=tx_state if getattr(cs, "MANUAL_PROMPT_CONSIDER_TX", True) else None,
                    )
                    raw = _readline_with_poll(prompt_empty=False)
                    if raw is None:
                        break
                    raw = raw.strip()
                    if not raw: continue

                    if raw == "resume":
                        if not _preflight_sem(proto, log, rx_enabled,
                                              attempts=max(1, int(args.preflight_attempts)),
                                              interval_s=max(0.05, float(args.preflight_interval))):
                            _error("Device not responding yet. Resolve and 'resume' again.")
                            continue
                        try:
                            if time_profile is None or not getattr(time_profile, "is_alive", lambda: False)():
                                area = _load_area(args.area, area_kwargs)
                                time_profile = _load_time(
                                    args.time,
                                    proto=proto, log=log, area=area,
                                    pause_evt=pause_evt, stop_evt=stop_evt,
                                    tx_echo=_inj_tx_echo, ack_tracker=_AckTracker(),
                                    kwargs=time_kwargs,
                                )
                                area_desc = area.describe() if hasattr(area, "describe") else ""
                                log.log_prof_area(f"start — {area_desc}")
                                _info(f"PROF AREA [{getattr(area,'name','AREA')}] start — {area_desc}")
                                # Time-profile start message augmented with visible knobs only.
                                # If the time profile offers describe(), use it; otherwise render from filtered kwargs.
                                try:
                                    tp_desc = time_profile.describe() if hasattr(time_profile, "describe") else ""
                                except Exception:
                                    tp_desc = ""
                                if not tp_desc:
                                    try:
                                        kvs = _kvpairs_filtered_time(args.time, time_kwargs)
                                        if kvs:
                                            tp_desc = ", ".join(f"{k}={v}" for k, v in kvs)
                                    except Exception:
                                        tp_desc = ""
                                if tp_desc:
                                    log.log_prof_time(f"start — {tp_desc}")
                                    _info(f"PROF TIME [{getattr(time_profile,'name','TIME')}] start — {tp_desc}")
                                else:
                                    log.log_prof_time("start")
                                    _info(f"PROF TIME [{getattr(time_profile,'name','TIME')}] start")
                                time_profile.start()
                            _print_rule_big(cs.SWITCH_RULE_STYLE)
                            _info("Resumed driven mode. Campaign continues.")
                            driven = True
                        except Exception as e:
                            _print_rule_big(cs.SWITCH_RULE_STYLE)
                            _error(f"Failed to arm on resume: {e}")
                        continue

                    if raw == "help":
                        _print_rule_small()
                        print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small()
                        print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small();  continue

                    if raw == "sem":
                        _print_rule_small()
                        print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
                        print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
                        _print_rule_small();  continue

                    if raw == "exit":
                        try:
                            stop_evt.set()
                            if 'time_profile' in locals() and time_profile and hasattr(time_profile, "stop"):
                                time_profile.stop()
                        except Exception:
                            pass
                        break

                    # Raw SEM command in manual mode
                    try:
                        log.log_tx(raw)
                        _tx_echo(raw)
                        tx_state.bump()
                        tr.write_line(raw)
                    except Exception as e:
                        _error(str(e))

            except (EOFError, KeyboardInterrupt):
                break
    finally:
        stop_evt.set()
        time.sleep(0.1)
        try: tr.close()
        finally: log.close()   # writes deferred events now
    return 0


if __name__ == "__main__":
    sys.exit(main())
