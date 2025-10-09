#!/usr/bin/env python3
# =============================================================================
# FATORI-V • Defines Orchestrator
# File: fatori-v/scripts/fatori_defines.py
# -----------------------------------------------------------------------------
# Purpose
#   Generates a per-run include header 'fatori_defines.svh' that consolidates
#   all feature-specific define headers produced by sub-tools (e.g., TMR).
#   The script reads the run YAML (legacy) or accepts minimal CLI args from the
#   top-level orchestrator, invokes feature generators, and emits a master header.
#
# Contract & Behavior
#   • Only fatori-v.py should read the run YAML in the modern flow; this file
#     accepts strings/args and builds a tiny config dict. Legacy --yaml is kept.
#   • Lower layers (like pblocks) must not print noisy info; this script keeps
#     its own prints gated behind --verbose, except for hard errors.
#   • Includes in the master header use only basenames so RTL can resolve them
#     from DEFINES_FINAL_PATH (no absolute paths are emitted).
# =============================================================================

from __future__ import annotations

import argparse
import subprocess
import sys
import shutil
import importlib.util
from pathlib import Path
from typing import Dict, List, Tuple

# ----- project-local settings -------------------------------------------------
_THIS_DIR = Path(__file__).resolve().parent.parent  # fatori-v/
sys.path.insert(0, str(_THIS_DIR))
import settings as _settings  # type: ignore

try:
    import yaml  # type: ignore
except Exception:
    print("[ERROR] PyYAML is required: pip install pyyaml", file=sys.stderr)
    sys.exit(2)


# ----- small utils ------------------------------------------------------------
def _load_yaml(path: Path) -> Dict:
    with path.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}

def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)

def _bool(v, default=False) -> bool:
    if isinstance(v, bool):
        return v
    if v is None:
        return default
    s = str(v).strip().lower()
    if s in ("1", "true", "yes", "on"):
        return True
    if s in ("0", "false", "no", "off"):
        return False
    return default

def _str(v, default="") -> str:
    return str(v) if v is not None else default

def _int(v, default=0) -> int:
    try:
        return int(v)
    except Exception:
        return default

def _exec(argv: List[str]) -> Tuple[int, str]:
    """Run a subprocess, capture stdout/stderr (merged)."""
    try:
        p = subprocess.run(argv, stdout=subprocess.PIPE,
                           stderr=subprocess.STDOUT, text=True, check=False)
        return p.returncode, p.stdout
    except FileNotFoundError:
        return 127, f"[ERROR] Tool not found: {argv[0]}"
    except Exception as e:
        return 1, f"[ERROR] Failed to run {' '.join(argv)}: {e}"


# ----- TMR integration (select_tmr.py) ---------------------------------------
def _maybe_run_tmr(cfg: Dict, run_id: str, outdir: Path, verbose: bool=False) -> List[Path]:
    """
    If the YAML/config contains a TMR section, invoke select_tmr.py to generate
    'outdir/fatori_tmr_config.svh'. Returns a list of produced headers.

    Expected config shape:
      specifics:
        fault_tolerance:
          tmr:
            enable: true
            json: "path/to/wrapped_registers.json"
            percentage: 50
            seed: null            # fallback to identification.seed if null
            file_enable: null     # optional path
            file_enable_include: false
            dis_flags: null       # optional path
            script: null          # optional override path to select_tmr.py
    """
    ft = (cfg.get("specifics", {}) or {}).get("fault_tolerance", {}) or {}
    tmr = ft.get("tmr", {}) or {}
    if not _bool(tmr.get("enable", False)):
        return []

    # Resolve tool path: YAML override → settings → PATH
    candidates = [
        _str(tmr.get("script")),
        getattr(_settings, "SELECT_TMR_SCRIPT_PATH", None),
        "select_tmr.py",
    ]
    tool = next((c for c in candidates if c and shutil.which(c)), None)
    if not tool:
        if verbose:
            print("[INFO] select_tmr.py not found on PATH nor settings; skipping TMR defines.")
        return []

    json_path = _str(tmr.get("json"))
    if not json_path:
        if verbose:
            print("[INFO] TMR 'json' not provided; skipping.")
        return []

    percentage = _int(tmr.get("percentage"), 0)

    ident = (cfg.get("run", {}).get("identification", {}) if isinstance(cfg.get("run"), dict) else {}) or {}
    seed = tmr.get("seed", None)
    if seed in (None, "null", "NULL"):
        seed = ident.get("seed", None)

    dis_flags       = _str(tmr.get("dis_flags")) or None
    file_enable     = _str(tmr.get("file_enable")) or None
    include_forced  = _bool(tmr.get("file_enable_include"), False)

    out_file = outdir / "fatori_tmr_config.svh"

    argv = [tool, "--json", json_path, "--percentage", str(percentage), "--out", str(out_file)]
    if seed is not None:      argv += ["--seed", str(seed)]
    if dis_flags:             argv += ["--dis_flags", dis_flags]
    if file_enable:           argv += ["--file_enable", file_enable]
    if include_forced:        argv += ["--file_enable_include"]
    if verbose:               argv += ["--verbose"]

    rc, out = _exec(argv)
    if verbose and out:
        print(out.rstrip())
    if rc != 0:
        print(f"[ERROR] select_tmr.py failed (rc={rc}); skipping its header.")
        return []
    return [out_file]


# ----- main -------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Generate consolidated fatori_defines.svh from run config.")
    # Primary path: receive minimal configuration via CLI arguments from the top-level orchestrator.
    ap.add_argument("--area-profile", required=False, help="Area profile name (e.g., 'modules')")
    ap.add_argument("--board", required=False, help="Hardware board identifier from run.hardware.board")
    ap.add_argument("--seed", required=False, help="Run identification seed")
    ap.add_argument("--modules-targets", required=False, help="Comma-separated list of enabled module labels")
    # Legacy fallback (discouraged):
    ap.add_argument("--yaml", required=False, help="Path to one run YAML (legacy)")
    # Location where headers will be generated. Defaults to settings.DEFINES_FINAL_PATH.
    ap.add_argument("--final-dir", default=None, help="Directory for generated headers (final destination)")
    # Results mirroring toggle
    ap.add_argument("--copy-to-results", dest="copy_to_results", action="store_true", help="Also mirror headers to results/<run_id>/gen")
    ap.add_argument("--no-copy-to-results", dest="copy_to_results", action="store_false", help="Do not mirror headers to results/<run_id>/gen")
    ap.set_defaults(copy_to_results=None)
    ap.add_argument("--run-id", default=None, help="Run id; if omitted, derived from config or 'run'")
    ap.add_argument("--verbose", action="store_true", help="Verbose tool output")
    args = ap.parse_args()

    # Build an internal config dict. Prefer direct CLI args; fall back to --yaml for legacy use.
    cfg: Dict = {}
    if args.yaml:
        yaml_path = Path(args.yaml).resolve()
        cfg = _load_yaml(yaml_path)
    else:
        ap_str = (args.area_profile or "").strip().lower()
        board = (args.board or "").strip()
        seed = (args.seed or "-").strip()
        enabled_csv = (args.modules_targets or "").strip()
        enabled: Dict[str, bool] = {}
        if enabled_csv:
            for label in [x.strip() for x in enabled_csv.split(",") if x.strip()]:
                enabled[label] = True
        # Compose the shape expected by downstream helpers.
        cfg = {
            "general": {"fault_injection": {"area_profile": ap_str}},
            "run": {
                "identification": {"seed": seed},
                "hardware": {"board": board},
            },
            "specifics": {
                "fault_injection": {
                    "area": {"modules": {"targets": enabled}}
                }
            }
        }

    # Determine run_id if not explicitly provided
    if args.run_id:
        run_id = args.run_id
    else:
        name = None
        try:
            name = str(((cfg.get("run") or {}).get("identification") or {}).get("name"))
        except Exception:
            name = None
        run_id = name or "run"

    # Final destination for generated headers
    final_dir = Path(args.final_dir).resolve() if args.final_dir else Path(getattr(_settings, "DEFINES_FINAL_PATH", ".")).resolve()
    _ensure_dir(final_dir)

    headers: List[Path] = []
    headers += _maybe_run_tmr(cfg, run_id, final_dir, verbose=args.verbose)

    # Optional: module pblocks (SVH + TCL); only when area_profile == 'module' or 'modules'
    area_prof = str(cfg.get("general", {}).get("fault_injection", {}).get("area_profile", "")).strip().lower()
    if area_prof in ("module", "modules"):
        # Load fatori_pblocks by absolute path: fatori-v/scripts/pblocks/fatori_pblocks.py
        pb_path = (_THIS_DIR / "scripts" / "pblocks" / "fatori_pblocks.py").resolve()
        try:
            spec = importlib.util.spec_from_file_location("fatori_pblocks", pb_path)
            if spec is None or spec.loader is None:
                raise ImportError("Cannot locate fatori_pblocks at " + str(pb_path))
            _pblocks = importlib.util.module_from_spec(spec)  # type: ignore
            spec.loader.exec_module(_pblocks)  # type: ignore
        except Exception as e:
            print(f"[ERROR] fatori_pblocks import failed: {e}; skipping pblocks generation.")
            _pblocks = None  # type: ignore
        if _pblocks is not None:  # type: ignore
            copy_flag = (args.copy_to_results if args.copy_to_results is not None
                         else bool(getattr(_settings, "DEFINES_COPY_TO_RESULTS", True)))
            headers += _pblocks.generate(cfg, run_id, final_dir, copy_flag, verbose=args.verbose)  # type: ignore

    # Master include header (includes by basename only)
    master = final_dir / "fatori_defines.svh"
    with master.open("w", encoding="utf-8") as fh:
        fh.write("// =============================================================================\n")
        fh.write("// Auto-generated by fatori_defines.py\n")
        fh.write(f"// Run: {run_id}\n")
        fh.write("// =============================================================\n")
        fh.write("// made by: Jaime Aguiar - IST Master's Student\n")
        fh.write("// =============================================================================\n\n")
        fh.write("`ifndef FATORI_DEFINES_SVH\n`define FATORI_DEFINES_SVH\n\n")
        for h in headers:
            try:
                inc_name = h.name  # Path-like object
            except Exception:
                inc_name = str(h).replace('\\', '/').split('/')[-1]
            fh.write(f"`include \"{inc_name}\"\n")
        fh.write("\n`endif\n")

    # Info prints only under --verbose
    if args.verbose:
        print(f"[INFO] Wrote master defines: {master}")
        if headers:
            print("[INFO] Included:")
            for h in headers:
                print(f"  - {h}")

    # Optional mirroring to results/<run_id>/<DEFINES_RESULTS_SUBDIR>
    copy_flag = (args.copy_to_results if args.copy_to_results is not None
                else bool(getattr(_settings, "DEFINES_COPY_TO_RESULTS", True)))
    if copy_flag:
        results_dir = Path(getattr(_settings, "RESULTS_DIR_NAME", "results"))
        subdir = getattr(_settings, "DEFINES_RESULTS_SUBDIR", "gen")
        mirror_dir = results_dir / run_id / subdir
        _ensure_dir(mirror_dir)
        # Copy master and each header
        import shutil as _sh
        _sh.copy2(master, mirror_dir / master.name)
        for h in headers:
            dest_name = getattr(h, "name", str(h))
            try:
                dest_name = h.name
            except Exception:
                dest_name = str(h).split("/")[-1]
            _sh.copy2(h, mirror_dir / dest_name)
        if args.verbose:
            print(f"[INFO] Mirrored headers to: {mirror_dir}")


if __name__ == "__main__":
    main()
