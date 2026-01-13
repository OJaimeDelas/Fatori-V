# =============================================================================
# FATORI-V • FI Interface
# File: fi_interface.py
# -----------------------------------------------------------------------------
# Helpers for building FI area/time profiles, FI command lines and running FI.
#=============================================================================

from __future__ import annotations

from typing import Any, Dict, Tuple, List
import subprocess
import sys

import fatori_settings as cfg
from scripts.common import common_settings as cset


# -----------------------------------------------------------------------------
# Area profile helpers
# -----------------------------------------------------------------------------
def build_area_profile(run_cfg: Dict[str, Any], seed: int) -> Tuple[str, str]:
    """
    Determine the area profile and build the CSV of area arguments for FI.

    Args:
        run_cfg: Parsed run configuration dictionary.
        seed:    Global seed chosen for this run.

    Returns:
        (area_profile_name, area_args_csv)
    """
    general_fi = (run_cfg.get("general") or {}).get("fault_injection") or {}
    specifics_fi = (run_cfg.get("specifics") or {}).get("fault_injection") or {}
    area_cfg = specifics_fi.get("area") or {}

    profile = str(general_fi.get("area_profile", "address_list")).lower()
    args: Dict[str, Any] = {}

    if profile == "address_list":
        addr_cfg = area_cfg.get("address_list") or {}
        file_path = addr_cfg.get("path") or addr_cfg.get("file")
        if file_path:
            args["file"] = str(file_path)

        mode = addr_cfg.get("mode") or addr_cfg.get("order") or "sequential"
        mode_str = str(mode).lower()
        args["mode"] = "random" if mode_str.startswith("rand") else "sequential"

        args["seed"] = addr_cfg.get("seed", seed)

    elif profile in ("device", "devices"):
        dev_cfg = area_cfg.get("device") or {}
        mode = dev_cfg.get("mode") or dev_cfg.get("order") or "sequential"
        mode_str = str(mode).lower()
        args["mode"] = "random" if mode_str.startswith("rand") else "sequential"
        args["seed"] = dev_cfg.get("seed", seed)

    elif profile.startswith("module"):
        mod_cfg = area_cfg.get("module") or {}

        labels = mod_cfg.get("labels")
        if not labels:
            # Fallback: enabled targets map
            targets = mod_cfg.get("targets") or {}
            labels = [
                name
                for name, enabled in targets.items()
                if str(enabled).lower() in ("on", "true", "1", "yes")
            ]
        if labels:
            args["labels"] = ",".join(labels)

        root = mod_cfg.get("root")
        if root:
            args["root"] = str(root)

        mode = mod_cfg.get("mode") or mod_cfg.get("order") or "sequential"
        mode_str = str(mode).lower()
        args["mode"] = "random" if mode_str.startswith("rand") else "sequential"

        args["seed"] = mod_cfg.get("seed", seed)

    # Unknown profiles leave args empty; FI console must handle that case.
    csv = ",".join(f"{k}={v}" for k, v in args.items())
    return profile, csv


# -----------------------------------------------------------------------------
# Time profile helpers
# -----------------------------------------------------------------------------
def build_time_profile(run_cfg: Dict[str, Any]) -> Tuple[str, str]:
    """
    Determine the time profile and build the CSV of time arguments for FI.

    Args:
        run_cfg: Parsed run configuration dictionary.

    Returns:
        (time_profile_name, time_args_csv)
    """
    general_fi = (run_cfg.get("general") or {}).get("fault_injection") or {}
    specifics_fi = (run_cfg.get("specifics") or {}).get("fault_injection") or {}
    time_cfg = specifics_fi.get("time") or {}

    profile = str(general_fi.get("time_profile", "uniform")).lower()
    args: Dict[str, Any] = {}

    if profile == "uniform":
        cfg_u = time_cfg.get("uniform") or {}
        if "rate_hz" in cfg_u:
            args["rate_hz"] = cfg_u["rate_hz"]
        if "period_s" in cfg_u:
            args["period_s"] = cfg_u["period_s"]
        if "duration_s" in cfg_u:
            args["duration_s"] = cfg_u["duration_s"]
        if "startup_delay_ms" in cfg_u:
            args["startup_delay_ms"] = cfg_u["startup_delay_ms"]
        if "max_shots" in cfg_u:
            args["max_shots"] = cfg_u["max_shots"]

        # Ack behaviour
        ack_val = cfg_u.get("ack", True)
        ack_str = str(ack_val).lower()
        if ack_str in ("false", "off", "0", "no"):
            args["ack"] = "false"
        else:
            args["ack"] = "true"
            if "ack_timeout_s" in cfg_u:
                args["ack_timeout_s"] = cfg_u["ack_timeout_s"]

    elif profile == "ramp":
        cfg_r = time_cfg.get("ramp") or {}
        for key in ("start_hz", "end_hz", "duration_s", "step_hz", "step_every_s"):
            if key in cfg_r:
                args[key] = cfg_r[key]
        if "hold_at_top" in cfg_r:
            args["hold_at_top"] = cfg_r["hold_at_top"]
        if "continue_at_top" in cfg_r:
            args["continue_at_top"] = cfg_r["continue_at_top"]
        if "startup_delay_ms" in cfg_r:
            args["startup_delay_ms"] = cfg_r["startup_delay_ms"]

    elif profile == "poisson":
        cfg_p = time_cfg.get("poisson") or {}
        if "lambda_hz" in cfg_p:
            args["lambda_hz"] = cfg_p["lambda_hz"]
        if "duration_s" in cfg_p:
            args["duration_s"] = cfg_p["duration_s"]
        if "startup_delay_ms" in cfg_p:
            args["startup_delay_ms"] = cfg_p["startup_delay_ms"]

    csv = ",".join(f"{k}={v}" for k, v in args.items())
    return profile, csv


# -----------------------------------------------------------------------------
# Command building and console execution
# -----------------------------------------------------------------------------
def build_fi_command(
    run_id: str,
    seed: int,
    area_profile: str,
    area_args_csv: str,
    time_profile: str,
    time_args_csv: str,
) -> List[str]:
    """
    Build the command-line argument list to launch the FI console.

    Args:
        run_id:         Logical identifier of the run.
        seed:           Global seed for FI.
        area_profile:   Name of the area profile.
        area_args_csv:  CSV string of area arguments (k=v,...).
        time_profile:   Name of the time profile.
        time_args_csv:  CSV string of time arguments (k=v,...).

    Returns:
        List of command-line arguments suitable for subprocess.run / Popen.
    """
    dev = cfg.DEFAULT_SEM_DEVICE
    baud = getattr(cfg, "DEFAULT_SEM_BAUDRATE", 1_250_000)

    cmd: List[str] = [
        sys.executable,
        "-u",
        "-m",
        "fi.fault_injection",
        "--dev",
        dev,
        "--baud",
        str(baud),
        "--run-name",
        run_id,
        "--seed",
        str(seed),
        "--area",
        area_profile,
        "--time",
        time_profile,
        "--header-style",
        cfg.FI_HEADER_STYLE_FOR_RUNS,
        "--show-console-commands",
        "false" if cfg.FI_HIDE_CONSOLE_COMMANDS else "true",
        "--show-sem-cheatsheet",
        "false" if cfg.FI_HIDE_SEM_CHEATSHEET else "true",
        "--show-start-mode",
        "false" if cfg.FI_HIDE_START_MODE else "true",
        "--on-end",
        "exit",
    ]

    if area_args_csv:
        cmd.extend(["--area-args", area_args_csv])
    if time_args_csv:
        cmd.extend(["--time-args", time_args_csv])

    return cmd


def run_fi_console(cmd: List[str]) -> int:
    """
    Run the FI console as a subprocess and return its exit code.

    For now this is a simple blocking call that prints the command and
    forwards the terminal to FI. More advanced interactive behaviour
    (auto-exit on specific lines, etc.) can be added here later.
    """
    print("Launching FI console:")
    print("  ", " ".join(cmd))
    print()
    completed = subprocess.run(
        cmd,
        check=cset.SUBPROCESS_CHECK_BY_DEFAULT,
    )
    return completed.returncode
