# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/console/sem_console.py
# -----------------------------------------------------------------------------
# SEM interactive console with driven and manual modes.
#
# Driven mode:
#   - Only non-invasive commands are accepted: help, sem, status, watch, manual, exit.
#   - State-changing commands (idle/observe/inject/assist/raw SEM) are disabled.
#
# Manual mode:
#   - Raw SEM commands at the prompt.
#   - The '>' appears only after a quiet RX window to avoid stray prompts.
#
# Header:
#   - Title centered and bold, Portugal time "YYYY-MM-DD HH:MM".
#   - Run / Session / Started values shown in green (configurable).
# =============================================================================

from __future__ import annotations

import argparse
import sys
import threading
import time
import datetime
from contextlib import contextmanager

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol
from fi.log import EventLogger

from fi.core.injector import (
    ensure_idle,
    go_observe,
    inject_once,
    status as status_query,
    assist_until_fc,
)

from fi.console import console_settings as cs

# Portugal time zone
try:
    from zoneinfo import ZoneInfo
    _PT_TZ = ZoneInfo("Europe/Lisbon")
except Exception:
    _PT_TZ = None


# ---------- terminal helpers -------------------------------------------------
def _info(msg: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_INFO}{msg}", cs.TAG_INFO))

def _tx_echo(cmd: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_TX}{cmd}", cs.TAG_SEND))

def _rx_echo(line: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_RX}{line}", cs.TAG_RECV))


# ---------- rules / centering -------------------------------------------------
def _rule(char: str, width: int) -> str:
    return char * width

def _print_rule_big(style: str | None = None) -> None:
    print(cs.colorize(_rule(cs.BIG_LINE_CHAR, cs.LINE_WIDTH), style or cs.BIG_LINE_STYLE))

def _print_rule_small(style: str | None = None) -> None:
    print(cs.colorize(_rule(cs.SMALL_LINE_CHAR, cs.LINE_WIDTH), style or cs.SMALL_LINE_STYLE))

def _center(text: str, width: int) -> str:
    if len(text) >= width:
        return text
    pad = (width - len(text)) // 2
    return " " * pad + text


# ---------- pause gate for RX printer ----------------------------------------
@contextmanager
def _pause_rx(rx_event: threading.Event):
    was_enabled = rx_event.is_set()
    if was_enabled:
        rx_event.clear()
        time.sleep(0.01)
    try:
        yield
    finally:
        if was_enabled:
            rx_event.set()


# ---------- RX activity tracker for manual prompt gating ---------------------
class _RxState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.last_rx = time.monotonic()

    def bump(self) -> None:
        with self.lock:
            self.last_rx = time.monotonic()

    def millis_since_rx(self) -> float:
        with self.lock:
            return (time.monotonic() - self.last_rx) * 1000.0


# ---------- header / help ----------------------------------------------------
def _now_pt_str_minutes() -> str:
    dt = datetime.datetime.now(_PT_TZ) if _PT_TZ else datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")

def _print_header(run_name: str, session: str, device: str, baud: int, start_mode_label: str) -> None:
    _print_rule_big()
    title = _center("FATORI-V — SEM Console", cs.LINE_WIDTH)
    print(cs.colorize(title, cs.HEADER_TITLE_STYLE))
    _print_rule_big()

    print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()

    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))

    _print_rule_big()

    print(cs.colorize("Start mode:", cs.SECTION_HEADER_STYLE), start_mode_label)
    print(cs.colorize("  • In driven mode only: help, sem, status, watch, manual, exit.", cs.HELP_BODY_STYLE))
    print(cs.colorize("  • For raw SEM commands, type 'manual'. To return, type 'resume'.", cs.HELP_BODY_STYLE))
    print(cs.colorize("  • Type 'help' anytime for the command list; 'sem' prints the SEM cheatsheet.", cs.HELP_BODY_STYLE))

    _print_rule_big()

    print(
        f"{cs.colorize('Run:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(run_name, cs.HEADER_RUN_VALUE_STYLE)}    "
        f"{cs.colorize('Session:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(session, cs.HEADER_SESSION_VALUE_STYLE)}"
    )
    print(
        f"{cs.colorize('Device:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(f'{device} @ {baud}', cs.HEADER_VALUE_STYLE)}    "
        f"{cs.colorize('Started:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(_now_pt_str_minutes(), cs.HEADER_TIME_VALUE_STYLE)}"
    )
    _print_rule_small()


def _print_help_all() -> None:
    _print_rule_small()
    print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()
    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()


def _print_help_sem_only() -> None:
    _print_rule_small()
    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()


# ---------- RX printer -------------------------------------------------------
def _rx_printer(tr: SemTransport, log: EventLogger, enabled_evt: threading.Event, stop_evt: threading.Event, rx_state: _RxState) -> None:
    poll = cs.RX_PRINTER_POLL_S
    while not stop_evt.is_set():
        if not enabled_evt.is_set():
            time.sleep(poll)
            continue
        lines = tr.read_lines()
        if lines:
            for ln in lines:
                log.log_rx(ln)
                _rx_echo(ln)
                rx_state.bump()
        else:
            time.sleep(poll)


# ---------- driven-mode helpers ----------------------------------------------
def _do_status(proto: SemProtocol, log: EventLogger, rx_gate: threading.Event) -> None:
    with _pause_rx(rx_gate):
        _tx_echo("S")
        s = status_query(proto, log)
        if not s:
            print("<no counters seen>")
        else:
            for k, v in s.items():
                pair = f"{k} {v}"
                log.log_rx(pair)
                _rx_echo(pair)


# ---------- manual prompt gating ---------------------------------------------
def _wait_quiet_then_prompt(rx_state: _RxState, quiet_ms: int = None, max_wait_ms: int = None) -> None:
    """
    Wait until no RX activity for ~quiet_ms, then print the manual prompt.
    A max bound avoids permanent silence if the device spams output.
    """
    if quiet_ms is None:
        quiet_ms = int(cs.MANUAL_PROMPT_QUIET_MS)
    if max_wait_ms is None:
        max_wait_ms = int(cs.MANUAL_PROMPT_MAXWAIT_MS)

    t0 = time.monotonic()
    while True:
        if rx_state.millis_since_rx() >= quiet_ms:
            break
        if (time.monotonic() - t0) * 1000.0 > max_wait_ms:
            break
        time.sleep(0.02)
    print(cs.PROMPT_MANUAL, end="", flush=True)


# ---------- main --------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Interactive SEM console (driven + manual modes).")
    ap.add_argument("--manual", action="store_true", help="Start in manual mode")
    ap.add_argument("--dev", default=settings.DEFAULT_SEM_DEVICE, help="Serial device path")
    ap.add_argument("--baud", type=int, default=settings.BAUDRATE, help="Serial baud rate")
    ap.add_argument("--run-name", default=settings.DEFAULT_RUN_NAME, help="Run name for results/<run_name>/...")
    ap.add_argument("--session", default=settings.DEFAULT_SESSION_LABEL, help="Session/benchmark label")
    args = ap.parse_args(argv)

    cfg = SerialConfig(device=args.dev, baud=args.baud)
    log = EventLogger(run_name=args.run_name, session_label=args.session, defer=settings.DEFER_LOG_WRITE)
    tr = SemTransport(cfg)

    rx_print_enabled = threading.Event()
    stop_evt = threading.Event()
    rx_state = _RxState()

    try:
        tr.open()
        start_reader = getattr(tr, "start_reader", None)
        if callable(start_reader):
            start_reader()

        log.set_header(device=cfg.device, baud=cfg.baud, sem_freq_hz=settings.SEM_FREQ_HZ)

        proto = SemProtocol(tr)
        proto.sync_prompt()

        rx_print_enabled.set()
        t = threading.Thread(
            target=_rx_printer, args=(tr, log, rx_print_enabled, stop_evt, rx_state), daemon=True
        )
        t.start()

        start_mode_label = "manual" if args.manual else "driven"
        _print_header(args.run_name, args.session, cfg.device, cfg.baud, start_mode_label)

        # Start mode behavior
        driven = not args.manual

        while True:
            try:
                if driven:
                    cmd = input("").strip()
                    if not cmd:
                        continue
                    op = cmd.split()[0].lower()

                    if op == "exit":
                        break
                    if op == "help":
                        _print_help_all();  continue
                    if op == "sem":
                        _print_help_sem_only();  continue
                    if op == "manual":
                        _print_rule_big(cs.SWITCH_RULE_STYLE)
                        _info("Switched to manual mode (raw SEM commands; 'resume' to return).")
                        driven = False
                        # draw prompt *after* quiet window so it does not lead the device output
                        _wait_quiet_then_prompt(rx_state)
                        continue
                    if op == "status":
                        _do_status(proto, log, rx_print_enabled);  continue
                    if op == "watch":
                        _info("watch: Ctrl+C to stop")
                        try:
                            while True:
                                _do_status(proto, log, rx_print_enabled)
                                time.sleep(cs.DEFAULT_WATCH_INTERVAL_S)
                        except KeyboardInterrupt:
                            print(); _info("watch: stopped")
                        continue

                    # All other commands disabled in driven mode
                    _info("Command disabled in driven mode. Type 'manual' to gain control.")

                else:
                    # MANUAL: only show '>' after a quiet window
                    _wait_quiet_then_prompt(rx_state)
                    raw = input("").strip()
                    if not raw:
                        continue
                    if raw == "resume":
                        _print_rule_big(cs.SWITCH_RULE_STYLE)
                        _info("Resumed driven mode (high-level commands active).")
                        driven = True
                        continue
                    if raw == "help":
                        _print_help_all();  continue
                    if raw == "sem":
                        _print_help_sem_only();  continue
                    if raw == "exit":
                        break

                    # Raw SEM pass-through
                    _tx_echo(raw)
                    log.log_tx(raw)
                    tr.write_line(raw)
                    # DO NOT print '>' now — wait for the device burst to finish
                    # The next loop iteration will call _wait_quiet_then_prompt()

            except (EOFError, KeyboardInterrupt):
                break

    finally:
        stop_evt.set()
        time.sleep(0.1)
        log.close()
        tr.close()


if __name__ == "__main__":
    sys.exit(main())
# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/console/sem_console.py
# -----------------------------------------------------------------------------
# SEM interactive console with driven and manual modes.
#
# Driven mode:
#   - Only non-invasive commands are accepted: help, sem, status, watch, manual, exit.
#   - State-changing commands (idle/observe/inject/assist/raw SEM) are disabled.
#
# Manual mode:
#   - Raw SEM commands at the prompt.
#   - The '>' appears only after a quiet RX window to avoid stray prompts.
#
# Header:
#   - Title centered and bold, Portugal time "YYYY-MM-DD HH:MM".
#   - Run / Session / Started values shown in green (configurable).
# =============================================================================

from __future__ import annotations

import argparse
import sys
import threading
import time
import datetime
from contextlib import contextmanager

from fi import settings
from fi.semio.transport import SerialConfig, SemTransport
from fi.semio.protocol import SemProtocol
from fi.log import EventLogger

from fi.core.injector import (
    ensure_idle,
    go_observe,
    inject_once,
    status as status_query,
    assist_until_fc,
)

from fi.console import console_settings as cs

# Portugal time zone
try:
    from zoneinfo import ZoneInfo
    _PT_TZ = ZoneInfo("Europe/Lisbon")
except Exception:
    _PT_TZ = None


# ---------- terminal helpers -------------------------------------------------
def _info(msg: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_INFO}{msg}", cs.TAG_INFO))

def _tx_echo(cmd: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_TX}{cmd}", cs.TAG_SEND))

def _rx_echo(line: str) -> None:
    print(cs.colorize(f"{cs.PREFIX_RX}{line}", cs.TAG_RECV))


# ---------- rules / centering -------------------------------------------------
def _rule(char: str, width: int) -> str:
    return char * width

def _print_rule_big(style: str | None = None) -> None:
    print(cs.colorize(_rule(cs.BIG_LINE_CHAR, cs.LINE_WIDTH), style or cs.BIG_LINE_STYLE))

def _print_rule_small(style: str | None = None) -> None:
    print(cs.colorize(_rule(cs.SMALL_LINE_CHAR, cs.LINE_WIDTH), style or cs.SMALL_LINE_STYLE))

def _center(text: str, width: int) -> str:
    if len(text) >= width:
        return text
    pad = (width - len(text)) // 2
    return " " * pad + text


# ---------- pause gate for RX printer ----------------------------------------
@contextmanager
def _pause_rx(rx_event: threading.Event):
    was_enabled = rx_event.is_set()
    if was_enabled:
        rx_event.clear()
        time.sleep(0.01)
    try:
        yield
    finally:
        if was_enabled:
            rx_event.set()


# ---------- RX activity tracker for manual prompt gating ---------------------
class _RxState:
    def __init__(self) -> None:
        self.lock = threading.Lock()
        self.last_rx = time.monotonic()

    def bump(self) -> None:
        with self.lock:
            self.last_rx = time.monotonic()

    def millis_since_rx(self) -> float:
        with self.lock:
            return (time.monotonic() - self.last_rx) * 1000.0


# ---------- header / help ----------------------------------------------------
def _now_pt_str_minutes() -> str:
    dt = datetime.datetime.now(_PT_TZ) if _PT_TZ else datetime.datetime.now()
    return dt.strftime("%Y-%m-%d %H:%M")

def _print_header(run_name: str, session: str, device: str, baud: int, start_mode_label: str) -> None:
    _print_rule_big()
    title = _center("FATORI-V — SEM Console", cs.LINE_WIDTH)
    print(cs.colorize(title, cs.HEADER_TITLE_STYLE))
    _print_rule_big()

    print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()

    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))

    _print_rule_big()

    print(cs.colorize("Start mode:", cs.SECTION_HEADER_STYLE), start_mode_label)
    print(cs.colorize("  • In driven mode only: help, sem, status, watch, manual, exit.", cs.HELP_BODY_STYLE))
    print(cs.colorize("  • For raw SEM commands, type 'manual'. To return, type 'resume'.", cs.HELP_BODY_STYLE))
    print(cs.colorize("  • Type 'help' anytime for the command list; 'sem' prints the SEM cheatsheet.", cs.HELP_BODY_STYLE))

    _print_rule_big()

    print(
        f"{cs.colorize('Run:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(run_name, cs.HEADER_RUN_VALUE_STYLE)}    "
        f"{cs.colorize('Session:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(session, cs.HEADER_SESSION_VALUE_STYLE)}"
    )
    print(
        f"{cs.colorize('Device:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(f'{device} @ {baud}', cs.HEADER_VALUE_STYLE)}    "
        f"{cs.colorize('Started:', cs.HEADER_LABEL_STYLE)} "
        f"{cs.colorize(_now_pt_str_minutes(), cs.HEADER_TIME_VALUE_STYLE)}"
    )
    _print_rule_small()


def _print_help_all() -> None:
    _print_rule_small()
    print(cs.colorize("Console commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.CONSOLE_HELP.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()
    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()


def _print_help_sem_only() -> None:
    _print_rule_small()
    print(cs.colorize("SEM IP commands", cs.SECTION_HEADER_STYLE))
    print(cs.colorize(cs.SEM_CHEATSHEET.rstrip(), cs.HELP_BODY_STYLE))
    _print_rule_small()


# ---------- RX printer -------------------------------------------------------
def _rx_printer(tr: SemTransport, log: EventLogger, enabled_evt: threading.Event, stop_evt: threading.Event, rx_state: _RxState) -> None:
    poll = cs.RX_PRINTER_POLL_S
    while not stop_evt.is_set():
        if not enabled_evt.is_set():
            time.sleep(poll)
            continue
        lines = tr.read_lines()
        if lines:
            for ln in lines:
                log.log_rx(ln)
                _rx_echo(ln)
                rx_state.bump()
        else:
            time.sleep(poll)


# ---------- driven-mode helpers ----------------------------------------------
def _do_status(proto: SemProtocol, log: EventLogger, rx_gate: threading.Event) -> None:
    with _pause_rx(rx_gate):
        _tx_echo("S")
        s = status_query(proto, log)
        if not s:
            print("<no counters seen>")
        else:
            for k, v in s.items():
                pair = f"{k} {v}"
                log.log_rx(pair)
                _rx_echo(pair)


# ---------- manual prompt gating ---------------------------------------------
def _wait_quiet_then_prompt(rx_state: _RxState, quiet_ms: int = None, max_wait_ms: int = None) -> None:
    """
    Wait until no RX activity for ~quiet_ms, then print the manual prompt.
    A max bound avoids permanent silence if the device spams output.
    """
    if quiet_ms is None:
        quiet_ms = int(cs.MANUAL_PROMPT_QUIET_MS)
    if max_wait_ms is None:
        max_wait_ms = int(cs.MANUAL_PROMPT_MAXWAIT_MS)

    t0 = time.monotonic()
    while True:
        if rx_state.millis_since_rx() >= quiet_ms:
            break
        if (time.monotonic() - t0) * 1000.0 > max_wait_ms:
            break
        time.sleep(0.02)
    print(cs.PROMPT_MANUAL, end="", flush=True)


# ---------- main --------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description="Interactive SEM console (driven + manual modes).")
    ap.add_argument("--manual", action="store_true", help="Start in manual mode")
    ap.add_argument("--dev", default=settings.DEFAULT_SEM_DEVICE, help="Serial device path")
    ap.add_argument("--baud", type=int, default=settings.BAUDRATE, help="Serial baud rate")
    ap.add_argument("--run-name", default=settings.DEFAULT_RUN_NAME, help="Run name for results/<run_name>/...")
    ap.add_argument("--session", default=settings.DEFAULT_SESSION_LABEL, help="Session/benchmark label")
    args = ap.parse_args(argv)

    cfg = SerialConfig(device=args.dev, baud=args.baud)
    log = EventLogger(run_name=args.run_name, session_label=args.session, defer=settings.DEFER_LOG_WRITE)
    tr = SemTransport(cfg)

    rx_print_enabled = threading.Event()
    stop_evt = threading.Event()
    rx_state = _RxState()

    try:
        tr.open()
        start_reader = getattr(tr, "start_reader", None)
        if callable(start_reader):
            start_reader()

        log.set_header(device=cfg.device, baud=cfg.baud, sem_freq_hz=settings.SEM_FREQ_HZ)

        proto = SemProtocol(tr)
        proto.sync_prompt()

        rx_print_enabled.set()
        t = threading.Thread(
            target=_rx_printer, args=(tr, log, rx_print_enabled, stop_evt, rx_state), daemon=True
        )
        t.start()

        start_mode_label = "manual" if args.manual else "driven"
        _print_header(args.run_name, args.session, cfg.device, cfg.baud, start_mode_label)

        # Start mode behavior
        driven = not args.manual

        while True:
            try:
                if driven:
                    cmd = input("").strip()
                    if not cmd:
                        continue
                    op = cmd.split()[0].lower()

                    if op == "exit":
                        break
                    if op == "help":
                        _print_help_all();  continue
                    if op == "sem":
                        _print_help_sem_only();  continue
                    if op == "manual":
                        _print_rule_big(cs.SWITCH_RULE_STYLE)
                        _info("Switched to manual mode (raw SEM commands; 'resume' to return).")
                        driven = False
                        # draw prompt *after* quiet window so it does not lead the device output
                        _wait_quiet_then_prompt(rx_state)
                        continue
                    if op == "status":
                        _do_status(proto, log, rx_print_enabled);  continue
                    if op == "watch":
                        _info("watch: Ctrl+C to stop")
                        try:
                            while True:
                                _do_status(proto, log, rx_print_enabled)
                                time.sleep(cs.DEFAULT_WATCH_INTERVAL_S)
                        except KeyboardInterrupt:
                            print(); _info("watch: stopped")
                        continue

                    # All other commands disabled in driven mode
                    _info("Command disabled in driven mode. Type 'manual' to gain control.")

                else:
                    # MANUAL: only show '>' after a quiet window
                    _wait_quiet_then_prompt(rx_state)
                    raw = input("").strip()
                    if not raw:
                        continue
                    if raw == "resume":
                        _print_rule_big(cs.SWITCH_RULE_STYLE)
                        _info("Resumed driven mode (high-level commands active).")
                        driven = True
                        continue
                    if raw == "help":
                        _print_help_all();  continue
                    if raw == "sem":
                        _print_help_sem_only();  continue
                    if raw == "exit":
                        break

                    # Raw SEM pass-through
                    _tx_echo(raw)
                    log.log_tx(raw)
                    tr.write_line(raw)
                    # DO NOT print '>' now — wait for the device burst to finish
                    # The next loop iteration will call _wait_quiet_then_prompt()

            except (EOFError, KeyboardInterrupt):
                break

    finally:
        stop_evt.set()
        time.sleep(0.1)
        log.close()
        tr.close()


if __name__ == "__main__":
    sys.exit(main())
