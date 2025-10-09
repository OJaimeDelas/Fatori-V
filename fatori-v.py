#!/usr/bin/env python3
# =============================================================================
# FATORI-V • Top Runner (Orchestrator)
# File: fatori-v.py
# -----------------------------------------------------------------------------
# Reads all YAML files under ./runs/ and, for each YAML "run":
#   • Parses the YAML and extracts only the parameters needed to invoke
#     the Fault Injection controller (fi.fault_injection) without modifying
#     FI's behavior.
#   • Launches fi.fault_injection as a subprocess, streams its console to our
#     stdout, allows user keystrokes to pass-through to FI (so 'exit' works),
#     and watches for end-of-campaign messages to automatically send 'exit'
#     so FI closes cleanly and the next YAML run can start.
#   • Mirrors key artifacts into ./results/<run_id>/:
#       - run_yaml/<yaml_file>
#       - injection_log.txt
#       - acme_injection_addresses.txt (if produced by the area profile)
#
# Presentation
#   • Prints a main banner "FATORI-V" framed by two yellow '=' lines above and
#     two below, then a summary list of all runs that will execute.
#   • Before each run, prints a per-run header with green "NEW RUN" centered
#     and a left-aligned "Run <name> from file <file.yaml>" line with names in
#     yellow, framed by pink '#' lines.
#   • After each run, prints a green centered "END of RUN" followed by a pink
#     '#' line.
#
# Notes
#   • All paths are resolved relative to this script.
#   • The FI framework keeps writing its own detailed logs under
#     results/<run_id>/<session>/ as before. The orchestrator does not replace
#     that log; it only mirrors key artifacts to the top-level results folder.
# =============================================================================

from __future__ import annotations

import sys
import shutil
import random
import pathlib
import os
import subprocess
import select
from typing import Any, Dict, List, Tuple, Optional
import json

# --- Load settings from ./settings.py (same folder as this script) -----------
import importlib.util as _importlib_util

_THIS_DIR = pathlib.Path(__file__).resolve().parent
_SETTINGS_PATH = _THIS_DIR / "settings.py"
_spec = _importlib_util.spec_from_file_location("fatori_v_settings", str(_SETTINGS_PATH))
if _spec is None or _spec.loader is None:
    raise RuntimeError("Failed to load settings.py alongside fatori-v.py")
_settings = _importlib_util.module_from_spec(_spec)
_spec.loader.exec_module(_settings)  # type: ignore

# --- YAML loader (PyYAML expected; clear error if missing) -------------------
try:
    import yaml  # type: ignore
except Exception as e:
    raise SystemExit(
        "ERROR: PyYAML is required to run fatori-v.py. "
        "Install with 'pip install pyyaml'."
    ) from e


# ---------- ANSI helpers -----------------------------------------------------
ANSI = {
    "reset": "\x1b[0m",
    "bold":  "\x1b[1m",
    # Standard 8 colors
    "black":   "\x1b[30m", "red":     "\x1b[31m", "green":  "\x1b[32m",
    "yellow":  "\x1b[33m", "blue":    "\x1b[34m", "magenta":"\x1b[35m",
    "cyan":    "\x1b[36m", "white":   "\x1b[37m",
    # Bright variants
    "br_black":  "\x1b[90m", "br_red":    "\x1b[91m", "br_green": "\x1b[92m",
    "br_yellow": "\x1b[93m", "br_blue":   "\x1b[94m", "br_magenta":"\x1b[95m",
    "br_cyan":   "\x1b[96m", "br_white":  "\x1b[97m",
    # Canary yellow (256-color xterm 226) — looks truly yellow on most themes
    "xterm_yellow": "\x1b[38;5;226m",
}

def _sty(s: str, *names: str) -> str:
    return "".join(ANSI[n] for n in names if n in ANSI) + s + ANSI["reset"]

LINE_WIDTH = 110
def _rule(ch: str, n: int = LINE_WIDTH) -> str:
    return ch * n
def _rule_alt_hashes(start_with_yellow: bool) -> str:
    """
    Build a full-width '#' rule with alternating colors per character:
    canary yellow and light blue. If start_with_yellow is True, the first '#'
    is yellow; otherwise it starts blue (the order is inverted).
    """
    plain = _rule("#")                      # same width as your headers
    width = len(plain)
    y = ANSI.get("xterm_yellow") or ANSI["yellow"]
    b = ANSI["br_cyan"]                    # light blue
    out = []
    pick_yellow = start_with_yellow
    for _ in range(width):
        out.append((y if pick_yellow else b) + "#" + ANSI["reset"])
        pick_yellow = not pick_yellow
    return "".join(out)

def _center(text: str, width: int = LINE_WIDTH) -> str:
    if len(text) >= width:
        return text
    pad = (width - len(text)) // 2
    return " " * pad + text


# ---------- Helpers: filesystem, YAML traversal, and FI console tee ----------
def _ensure_dir(p: pathlib.Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _safe_get(dct: Dict[str, Any], path: List[str], default: Any = None) -> Any:
    """Traverse a nested dict with a list of keys; return default if any missing."""
    cur = dct
    for k in path:
        if not isinstance(cur, dict) or k not in cur:
            return default
        cur = cur[k]
    return cur


def _kv_csv(opts: Dict[str, Any]) -> str:
    """
    Convert a flat dict into CSV 'k=v' suitable for fi.fault_injection.
    Only include keys with non-None, non-empty values (empty string is ignored).
    """
    parts: List[str] = []
    for k, v in opts.items():
        if v is None:
            continue
        if isinstance(v, str) and v.strip() == "":
            continue
        parts.append(f"{k}={v}")
    return ",".join(parts)


def _build_area_args(yaml_root: Dict[str, Any], profile: str, global_seed: Optional[int]) -> Tuple[str, Dict[str, Any]]:
    """
    Extract area-specific options from the full YAML.

    Accepted schema (robust to current documents):
      • address_list: 'file' OR 'path'; 'mode' ('sequential'|'random'); 'seed'
                      If 'file' is a bare filename, it is resolved under
                      'fi/area/examples/' relative to this script.
      • device      : 'mode' ('sequential'|'random'); 'seed'
                      'board'/'ebd_file' are injected by fi.fault_injection defaults.
      • module      : 'labels'/'enabled'; 'root'; 'mode'; 'seed'
    """
    spec_area = _safe_get(yaml_root, ["specifics", "fault_injection", "area"], {}) or {}
    prof = str(profile).lower()
    opts: Dict[str, Any] = {}

    if prof == "address_list":
        sec = spec_area.get("address_list", {}) or {}
        path = sec.get("file") or sec.get("path")
        if path:
            p = pathlib.Path(str(path))
            if not p.is_absolute():
                # First try relative to repo root as-given
                candidate = (_THIS_DIR / p).resolve()
                if not candidate.exists():
                    # Then resolve under fi/area/examples/
                    example = (_THIS_DIR / "fi" / "area" / "examples" / p.name).resolve()
                    path = str(example)
                else:
                    path = str(candidate)
            else:
                path = str(p)
            opts["path"] = path
        mode = sec.get("mode") or sec.get("order")
        if mode:
            opts["mode"] = "random" if str(mode).strip().lower() in ("random", "shuffle") else "sequential"
        seed = sec.get("seed", None)
        opts["seed"] = seed if seed is not None else (global_seed if global_seed is not None else None)

    elif prof == "device":
        sec = spec_area.get("device", {}) or {}
        mode = sec.get("mode") or sec.get("order")
        if mode:
            opts["mode"] = "random" if str(mode).strip().lower() in ("random", "shuffle") else "sequential"
        seed = sec.get("seed", None)
        opts["seed"] = seed if seed is not None else (global_seed if global_seed is not None else None)

    elif prof in ("module", "modules"):
        sec = spec_area.get("module", {}) or {}
        labels = sec.get("enabled") or sec.get("labels")
        if isinstance(labels, list) and labels:
            opts["labels"] = ",".join(str(x) for x in labels)
        elif isinstance(labels, str) and labels.strip():
            opts["labels"] = labels
        root = sec.get("root", None)
        if root:
            opts["root"] = root
        mode = sec.get("mode") or sec.get("order")
        if mode:
            opts["mode"] = "random" if str(mode).strip().lower() in ("random", "shuffle") else "sequential"
        seed = sec.get("seed", None)
        opts["seed"] = seed if seed is not None else (global_seed if global_seed is not None else None)

    return _kv_csv(opts), opts


def _build_time_args(yaml_root: Dict[str, Any], profile: str) -> Tuple[str, Dict[str, Any]]:
    """
    Extract time-specific options from the full YAML.

    Supported keys:
      • uniform: rate_hz, period_s, duration_s, ack, ack_timeout_s, max_shots, startup_delay_ms
                 If ack=false|off, ack_timeout_s is NOT forwarded.
      • ramp   : start_hz, end_hz, duration_s, step_hz, step_every_s, hold_at_top, continue_at_top, startup_delay_ms
      • poisson: lambda_hz, duration_s, startup_delay_ms
    """
    spec_time = _safe_get(yaml_root, ["specifics", "fault_injection", "time"], {}) or {}
    prof = str(profile).lower()
    opts: Dict[str, Any] = {}

    if prof == "uniform":
        sec = spec_time.get("uniform", {}) or {}
        for k in ("rate_hz", "period_s", "duration_s", "ack", "ack_timeout_s", "max_shots", "startup_delay_ms"):
            if k in sec:
                opts[k] = sec[k]
        # drop ack_timeout_s if ack is false/off
        try:
            ack_val = str(opts.get("ack", "")).strip().lower()
            if ack_val in ("", "0", "false", "off", "no"):
                opts.pop("ack_timeout_s", None)
        except Exception:
            pass

    elif prof == "ramp":
        sec = spec_time.get("ramp", {}) or {}
        for k in ("start_hz", "end_hz", "duration_s", "step_hz", "step_every_s", "hold_at_top", "continue_at_top", "startup_delay_ms"):
            if k in sec:
                opts[k] = sec[k]

    elif prof == "poisson":
        sec = spec_time.get("poisson", {}) or {}
        for k in ("lambda_hz", "duration_s", "startup_delay_ms"):
            if k in sec:
                opts[k] = sec[k]

    return _kv_csv(opts), opts


def _tee_and_autofinish(proc: subprocess.Popen) -> int:
    """
    Stream FI stdout to our console, forward user stdin lines to FI, and monitor
    for finish-line hints. Once a hint appears, send 'exit' to FI exactly once.
    Return FI's exit code.
    """
    exit_sent = False
    assert proc.stdout is not None
    while True:
        try:
            # Multiplex child's stdout and our stdin
            r, _, _ = select.select([proc.stdout, sys.stdin], [], [], 0.1)
        except Exception:
            r = [proc.stdout]

        if proc.stdout in r:
            line = proc.stdout.readline()
            if line == "":
                break  # child ended
            line = line.rstrip("\n")
            print(line)
            if (not exit_sent) and any(h in line for h in _settings.FINISH_LINE_HINTS):
                try:
                    if proc.stdin:
                        proc.stdin.write("exit\n")
                        proc.stdin.flush()
                    exit_sent = True
                except Exception:
                    exit_sent = True

        if sys.stdin in r:
            try:
                user_line = sys.stdin.readline()
            except Exception:
                user_line = ""
            if user_line == "":
                # stdin EOF; do nothing special
                pass
            else:
                try:
                    if proc.stdin:
                        proc.stdin.write(user_line)
                        proc.stdin.flush()
                except Exception:
                    pass

        if proc.poll() is not None:
            break

    proc.wait()
    return int(proc.returncode or 0)

def _load_modules_map(root_dir: Path, map_rel_path: str) -> dict:
    p = (root_dir / map_rel_path).resolve()
    with p.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

def _enabled_targets_from_yaml(cfg: dict) -> list[str]:
    # Reads specifics.fault_injection.area.modules.targets and returns enabled keys.
    tmap = (cfg.get("specifics", {}) or {}).get("fault_injection", {}).get("area", {}) or {}
    msec = tmap.get("modules", {}) or {}
    targets = msec.get("targets", {}) or {}
    enabled = []
    for name, val in targets.items():
        v = (str(val).strip().lower() if not isinstance(val, bool) else ("on" if val else "off"))
        if v in ("on", "true", "1", "yes"):
            enabled.append(name)
    return sorted(enabled)

def _resolve_rects_for_targets(modmap: dict, selected: list[str]) -> dict[str, list[dict]]:
    out = {}
    tmap = (modmap or {}).get("targets", {}) or {}
    for name in selected:
        info = tmap.get(name, {}) or {}
        rects = info.get("rects", []) or []
        if rects:
            out[name] = rects
    return out

def _write_pblocks_tcl(out_path: Path, target_rects: dict[str, list[dict]]) -> None:
    # Creates pblocks for enabled targets, resizes them to the SLICE rectangles,
    # and attaches RTL cells by REF_NAME == <target>. Source in Vivado before P&R.
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("# =============================================================================\n")
        fh.write("# FATORI-V • Generated Pblock TCL (per-run)\n")
        fh.write("# =============================================================================\n\n")
        for tgt, rects in target_rects.items():
            pblock = f"pblock_{tgt}"
            fh.write(f"create_pblock {pblock}\n")
            for r in rects:
                x0, y0, x1, y1 = int(r['x0']), int(r['y0']), int(r['x1']), int(r['y1'])
                fh.write(f"resize_pblock [get_pblocks {pblock}] -add {{SLICE_X{x0}Y{y0}:SLICE_X{x1}Y{y1}}}\n")
            fh.write(f"set _cells [get_cells -hier -filter {{REF_NAME == {tgt}}}]\n")
            fh.write(f"if {{[llength $_cells] > 0}} {{\n")
            fh.write(f"  add_cells_to_pblock [get_pblocks {pblock}] $_cells\n")
            fh.write(f"}} else {{\n")
            fh.write(f"  puts \"[INFO] No cells found with REF_NAME == {tgt}\"\n")
            fh.write(f"}}\n\n")

            
# ---------- Banner helpers ---------------------------------------------------

def _nl(n: int = 1) -> None:
    # exact n blank lines, no extra spaces
    if n > 0:
        print("\n" * n, end="")


def _print_main_banner(run_items: List[Tuple[str, str]]) -> None:
    """
    Print the main program banner and the list of runs that will execute.
    run_items: list of tuples (run_name, yaml_filename)
    """
    print(_rule_alt_hashes(start_with_yellow=True))
    print(_rule_alt_hashes(start_with_yellow=False))
    print(_sty(_center("FATORI-V"), "br_green", "bold"))
    print(_rule_alt_hashes(start_with_yellow=False))
    print(_rule_alt_hashes(start_with_yellow=True))
    print(_sty("Runs that will execute:", "bold", "white"))
    if not run_items:
        print(_sty("  (none found under ./runs)", "white"))
    else:
        for rn, fn in run_items:
            print(_sty("  - ", "white") + _sty(rn, "xterm_yellow") + _sty(f"  (from {fn})", "white"))
    _nl() #New Line


def _print_per_run_header(run_name: str, yaml_name: str, area_prof: str, time_prof: str, seed: int) -> None:
    """
    Print the per-run header. Pink '#' lines, green 'NEW RUN' centered, then
    left-aligned 'Run <name> from file <yaml>' with names in yellow, and the
    short 'Launching' block without specifics.
    """
    print(ANSI["br_magenta"] + _rule("#") + ANSI["reset"])
    print(_sty(_center("NEW RUN"), "br_green", "bold"))
    _nl() #New Line
    left = (_sty("Runing ", "white") + _sty(run_name, "xterm_yellow") +
            _sty(" from file ", "white") + _sty(yaml_name, "xterm_yellow") +
            _sty(" with:", "white"))
    print(left)
    # Minimal launch summary (no specifics for area/time)
    print("       area=" + _sty(area_prof, "br_green"))
    print("       time=" + _sty(time_prof, "br_green"))
    print(f"       seed={seed}")

    _nl() #New Line
    print(ANSI["br_magenta"] + _rule("-") + ANSI["reset"])

    # -----------------------------------------------------------------------------
    if area_prof=="modules":
        # Concise pblocks notices shown immediately after NEW RUN header.
        # They intentionally mirror the results/ path (blue [INFO] like the rest).
        try:
            _defs_subdir = getattr(_settings, "DEFINES_RESULTS_SUBDIR", "gen")
            _results_root = getattr(_settings, "RESULTS_DIR_NAME", "results")
            _info_c = ANSI.get("br_blue", ANSI.get("blue", ""))
            _reset = ANSI.get("reset", "")
            print(f"{_info_c}[INFO] Wrote: fatori-v/{_results_root}/{run_name}/{_defs_subdir}/fatori_pblocks.svh")
            print(f"{_info_c}[INFO] Wrote: fatori-v/{_results_root}/{run_name}/{_defs_subdir}/fatori_pblocks.tcl")
            _nl() #New Line
            print(ANSI["br_magenta"] + _rule("-") + ANSI["reset"])
        except Exception:
            pass
    # -----------------------------------------------------------------------------


def _print_end_of_run() -> None:
    """Green centered 'END of RUN' followed by a pink '#' line."""
    print(_sty(_center("END of RUN"), "br_green", "bold"))
    print(ANSI["br_magenta"] + _rule("#") + ANSI["reset"])



# ---------- Load modules map (board rectangles) -------------------------------
def _load_modules_map(root_dir: Path, map_rel_path: str) -> dict:
    p = (root_dir / map_rel_path).resolve()
    with p.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

def _enabled_targets_from_yaml(cfg: dict) -> list[str]:
    tmap = (cfg.get("specifics", {}) or {}).get("fault_injection", {}).get("area", {}) or {}
    msec = tmap.get("module", {}) or {}
    targets = msec.get("targets", {}) or {}
    enabled = []
    for name, val in targets.items():
        v = str(val).strip().lower() if not isinstance(val, bool) else ("on" if val else "off")
        if v in ("on", "true", "1", "yes"):
            enabled.append(name)
    return sorted(enabled)

def _resolve_rects_for_targets(modmap: dict, selected: list[str]) -> dict[str, list[dict]]:
    out = {}
    tmap = (modmap or {}).get("targets", {}) or {}
    for name in selected:
        info = tmap.get(name, {}) or {}
        rects = info.get("rects", []) or []
        if rects:
            out[name] = rects
    return out

def _write_pblocks_tcl(out_path: Path, target_rects: dict[str, list[dict]]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as fh:
        fh.write("# Auto-generated by fatori-v.py — per-run pblock definitions\n")
        fh.write("# Source this TCL in Vivado to create/resize pblocks.\n\n")
        for tgt, rects in target_rects.items():
            pblock_name = f"pblock_{tgt}"
            fh.write(f"create_pblock {pblock_name}\n")
            for r in rects:
                x0, y0, x1, y1 = int(r["x0"]), int(r["y0"]), int(r["x1"]), int(r["y1"])
                fh.write(f"resize_pblock [get_pblocks {pblock_name}] -add {{SLICE_X{x0}Y{y0}:SLICE_X{x1}Y{y1}}}\n")
            fh.write("\n")

# ---------- Main runner: iterate YAML files and invoke FI one by one ---------
def main(argv: Optional[List[str]] = None) -> int:
    # Resolve base folders relative to fatori-v.py
    runs_dir = (_THIS_DIR / _settings.RUNS_DIR_NAME).resolve()
    results_dir = (_THIS_DIR / _settings.RESULTS_DIR_NAME).resolve()
    _ensure_dir(runs_dir)
    _ensure_dir(results_dir)

    # Discover YAML files (top-level only; no subdirectories)
    yaml_paths: List[pathlib.Path] = []
    yaml_paths.extend(sorted(pathlib.Path(runs_dir).glob("*.yaml")))
    yaml_paths.extend(sorted(pathlib.Path(runs_dir).glob("*.yml")))

    # Prepare list for the "Runs that will execute" banner
    run_items_preview: List[Tuple[str, str]] = []
    for ypath in yaml_paths:
        try:
            with ypath.open("r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
            run_name = _safe_get(cfg, ["run", "identification", "name"], ypath.stem)
            run_items_preview.append((str(run_name), ypath.name))
        except Exception:
            run_items_preview.append((ypath.stem, ypath.name))

    _print_main_banner(run_items_preview)

    if not yaml_paths:
        # Nothing to do
        return 0

    # Process each YAML
    for ypath in yaml_paths:
        # Load YAML (full document; we only pluck required parts)
        try:
            with ypath.open("r", encoding="utf-8") as fh:
                cfg = yaml.safe_load(fh) or {}
        except Exception as e:
            print(f"[ERROR] Failed to parse YAML '{ypath.name}': {e}")
            # Keep batch running: continue with next file.
            continue

        # Determine run_id exactly from YAML name (no timestamp)
        run_name = _safe_get(cfg, ["run", "identification", "name"], None)
        run_id = str(run_name).strip() if isinstance(run_name, str) and run_name.strip() else ypath.stem

        # Ensure per-run results mirror folders
        run_out_dir = results_dir / run_id
        _ensure_dir(run_out_dir)
        _ensure_dir(run_out_dir / _settings.TOP_SUBDIR_REPORTS)
        _ensure_dir(run_out_dir / _settings.TOP_SUBDIR_PLOTS)

        # Snapshot the exact YAML into results/<run_id>/ (keep original filename)
        try:
            shutil.copy2(ypath, run_out_dir / ypath.name)
        except Exception as e:
            print(f"[ERROR] Failed to snapshot YAML '{ypath.name}': {e}")

        # Global seed: YAML > settings default/random
        yaml_seed = _safe_get(cfg, ["run", "identification", "seed"], None)
        if yaml_seed is None:
            global_seed = _settings.DEFAULT_GLOBAL_SEED if _settings.DEFAULT_GLOBAL_SEED is not None else random.getrandbits(64)
        else:
            global_seed = int(yaml_seed)

        # Serial params (authoritative from top settings for now)
        dev = _settings.DEFAULT_SEM_DEVICE
        baud = _settings.DEFAULT_BAUDRATE

        # Area/time profile names from the YAML (full YAML is accepted)
        area_prof = _safe_get(cfg, ["general", "fault_injection", "area_profile"], "address_list")
        time_prof = _safe_get(cfg, ["general", "fault_injection", "time_profile"], "uniform")

        # Build area/time argument CSVs from specifics
        area_csv, _ = _build_area_args(cfg, area_prof, global_seed)
        time_csv, _ = _build_time_args(cfg, time_prof)

        # Session label (stable default)
        session_label = _settings.DEFAULT_SESSION_LABEL

        # Compose the FI CLI (pass top-layer authoritative defaults explicitly)
        fi_cmd: List[str] = [
            sys.executable, "-u", "-m", "fi.fault_injection",
            "--dev", str(dev),
            "--baud", str(baud),
            "--run-name", str(run_id),
            "--session", str(session_label),
            "--area", str(area_prof),
            "--time", str(time_prof),
            "--seed", str(global_seed),
            "--header-style", "simple",
            "--show-console-commands", "false",
            "--show-sem-cheatsheet", "false",
            "--show-start-mode", "false",
        ]
        # Pass fatori-v behavior knob to FI: when orchestration is used the default is 'exit'
        fi_cmd.extend(["--on-end", "exit"])

        if area_csv:
            fi_cmd.extend(["--area-args", area_csv])
        if time_csv:
            fi_cmd.extend(["--time-args", time_csv])

        # Per-run header
        # Generate defines and pblocks artifacts for this run before launching FI
        try:
            # The defines driver writes to a final directory and may also mirror to results.
            # Older versions accepted --outdir; newer accept --final-dir and copy flags.
            final_dir = pathlib.Path(getattr(_settings, "DEFINES_FINAL_PATH", ".")).resolve()

            # Compute results mirror directory for defines/pblocks artifacts (used below to locate TCL).
            defs_outdir = (results_dir / run_id / getattr(_settings, "DEFINES_RESULTS_SUBDIR", "gen")).resolve()

            # Extract values to pass downstream as simple CLI strings (avoid handing off the YAML).
            try:
                area_prof = str(_safe_get(cfg, ["general", "fault_injection", "area_profile"], "")).strip().lower()
            except Exception:
                area_prof = ""
            try:
                board = str(_safe_get(cfg, ["run", "hardware", "board"], "")).strip()
            except Exception:
                board = ""
            try:
                targets_map = (_safe_get(cfg, ["specifics", "fault_injection", "area", "modules", "targets"], {}) or {})
                if not targets_map:
                    targets_map = (_safe_get(cfg, ["specifics", "fault_injection", "area", "module", "targets"], {}) or {})
            except Exception:
                targets_map = {}

            # Build a compact CSV containing only enabled target labels.
            enabled_labels = []
            if isinstance(targets_map, dict):
                for name, val in targets_map.items():
                    v = (str(val).strip().lower() if not isinstance(val, bool) else ("on" if val else "off"))
                    if v in ("on", "true", "1", "yes"):
                        enabled_labels.append(str(name))
            enabled_csv = ",".join(sorted(set(enabled_labels)))

            # Call the defines generator passing strings only; no temporary handoff files are created.
            defs_cmd = [
                sys.executable,
                str((_THIS_DIR / "scripts" / "fatori_defines.py").resolve()),
                "--area-profile", str(area_prof),
                "--board", str(board),
                "--seed", str(global_seed),
                "--modules-targets", enabled_csv,
                "--run-id", str(run_id),
                "--final-dir", str(final_dir),
            ]
            if bool(getattr(_settings, "DEFINES_COPY_TO_RESULTS", True)):
                defs_cmd.append("--copy-to-results")
            else:
                defs_cmd.append("--no-copy-to-results")
            rc = subprocess.run(defs_cmd, cwd=str(_THIS_DIR), text=True, capture_output=True)
            if rc.returncode != 0:
                print("[WARN] Defines/pblocks generation returned non-zero:")
                if rc.stdout: print(rc.stdout)
                if rc.stderr: print(rc.stderr)
            else:
                if rc.stdout:
                    print(rc.stdout, end="")
            # Optional: automatically apply the generated pblocks TCL in Vivado.
            try:
                tcl_candidates = [
                    defs_outdir / "fatori_pblocks.tcl",
                    final_dir / "fatori_pblocks.tcl",
                ]
                tcl_path = next((p for p in tcl_candidates if p.exists()), None)
                if tcl_path is not None:
                    if bool(getattr(_settings, "APPLY_PBLOCKS_TCL", False)):
                        vbin = str(getattr(_settings, "VIVADO_BIN", "vivado"))
                        vlog = (results_dir / run_id / "vivado_pblocks.log").resolve()
                        vjou = (results_dir / run_id / "vivado_pblocks.jou").resolve()
                        env = os.environ.copy()
                        xpr = getattr(_settings, "VIVADO_XPR", None)
                        if xpr:
                            env["FATORI_XPR"] = str(pathlib.Path(xpr).resolve())
                        vcmd = [vbin, "-mode", "batch", "-source", str(tcl_path), "-notrace",
                                "-log", str(vlog), "-journal", str(vjou)]
                        print(f"[INFO] Applying pblocks in Vivado: {' '.join(vcmd)}")
                        vrc = subprocess.run(vcmd, cwd=str(_THIS_DIR), text=True, capture_output=True, env=env)
                        if vrc.returncode != 0:
                            print("[WARN] Vivado pblocks apply returned non-zero.")
                            if vrc.stdout: print(vrc.stdout)
                            if vrc.stderr: print(vrc.stderr)
                        else:
                            print("[INFO] Vivado pblocks applied.")
                    
            except Exception as ie:
                print(f"[WARN] Post-defines pblocks step skipped: {ie}")
        except Exception as e:
            print(f"[WARN] Could not generate defines/pblocks: {e}")


        _print_per_run_header(run_id, ypath.name, str(area_prof), str(time_prof), int(global_seed))

        # Run FI with cwd at this folder so FI writes ./results/
        try:
            proc = subprocess.Popen(
                fi_cmd,
                cwd=str(_THIS_DIR),              # ensure 'results/' is under this folder
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
            )
        except Exception as e:
            print(f"[ERROR] Failed to start FI: {e}")
            continue

        rc = _tee_and_autofinish(proc)
        _print_end_of_run()

    return 0


if __name__ == "__main__":
    sys.exit(main())
