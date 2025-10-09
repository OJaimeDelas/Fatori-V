#!/usr/bin/env python3
# =============================================================================
# FATORI-V • Defines & Pblocks Generator
# File: fatori-v/scripts/pblocks/fatori_pblocks.py
# -----------------------------------------------------------------------------
# Generates per-run artifacts for module-target pblocks:
#   • fatori_pblocks.svh  — Verilog macros gating synthesis attributes per target.
#   • fatori_pblocks.tcl  — Vivado commands to create/resize/attach pblocks.
#
# Contract
#   • This module is primarily imported by fatori_defines.py; only the top-level
#     orchestrator should read YAML. The 'generate' function consumes a dict.
#   • File emission is self-contained: we write to 'final_dir' and optionally
#     mirror to results/<run>/gen. Lower-level printing is kept minimal/silent.
# =============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Dict, Any, List
import importlib.util
import shutil

try:
    import yaml  # type: ignore
except Exception as e:
    print(f"[ERROR] Missing dependency 'pyyaml': {e}")
    raise


# --- Load top settings without relying on sys.path packages -------------------
def _load_settings():
    """
    Load the project settings module used by pblocks/defines generation.

    Resolution strategy (in order):
      1) Prefer '<repo_root>/settings.py' which sits alongside 'fatori-v.py'.
      2) If not found, fall back to legacy 'scripts/settings.py' (backward compatibility).
      3) If neither exists, raise a clear FileNotFoundError.
    """
    pblocks_dir = Path(__file__).resolve().parent
    scripts_dir = pblocks_dir.parent
    repo_root = scripts_dir.parent

    root_settings_py = repo_root / "settings.py"
    legacy_settings_py = scripts_dir / "settings.py"

    target = None
    module_name = None
    if root_settings_py.is_file():
        target = root_settings_py
        module_name = "fatori_v_settings_root"
    elif legacy_settings_py.is_file():
        target = legacy_settings_py
        module_name = "fatori_v_settings_legacy"

    if target is None or module_name is None:
        raise FileNotFoundError(f"settings.py not found at expected locations: {root_settings_py} or {legacy_settings_py}")

    spec = importlib.util.spec_from_file_location(module_name, target)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to import settings from {target}")
    mod = importlib.util.module_from_spec(spec)  # type: ignore
    spec.loader.exec_module(mod)  # type: ignore
    return mod


# --- Simple config helpers ----------------------------------------------------
def _get(d: Dict[str, Any], *keys, default=None):
    cur: Any = d
    for k in keys:
        if not isinstance(cur, dict):
            return default
        cur = cur.get(k, None)
        if cur is None:
            return default
    return cur


# --- Board modules map --------------------------------------------------------
def _load_modules_map(board: str) -> Dict[str, Any]:
    """Load boards/<board>/modules.yaml as a dict."""
    here = Path(__file__).resolve()
    mp = here.parent / "boards" / board / "modules.yaml"
    if not mp.exists():
        raise FileNotFoundError(f"modules.yaml not found for board '{board}': {mp}")
    with mp.open("r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


# --- Emit SVH -----------------------------------------------------------------
def _emit_svh(all_targets: Dict[str, Any], enabled: Dict[str, bool], out: Path, run_id: str, seed) -> Path:
    """
    Write fatori_pblocks.svh with per-target macros.
      • FATORI_TARGET_<NAME> => 1 if enabled else 0
      • FATORI_ATTR_<NAME>   => attribute string when enabled else blank
    """
    lines: List[str] = []
    lines.append("// =============================================================================")
    lines.append("// FATORI-V • Generated Defines (Pblocks)")
    lines.append("// File: fatori_pblocks.svh")
    lines.append("// -----------------------------------------------------------------------------")
    lines.append(f"// Run: {run_id}")
    lines.append(f"// Seed: {seed}")
    lines.append("// 'FATORI_TARGET_<NAME>' expands to 1 or 0.")
    lines.append("// 'FATORI_ATTR_<NAME>' expands to synthesis attributes when enabled.")
    lines.append("// =============================================================================")
    lines.append("")
    lines.append("`ifndef FATORI_PBLOCKS_SVH")
    lines.append("`define FATORI_PBLOCKS_SVH")
    lines.append("")
    for tname, _ in all_targets.items():
        key = tname.upper()
        on = 1 if enabled.get(tname, False) else 0
        attr = '(* keep_hierarchy = "yes", dont_touch = "true" *)' if on else ""
        lines.append(f"`define FATORI_TARGET_{key} {on}")
        lines.append(f"`define FATORI_ATTR_{key} {attr}")
        lines.append("")
    lines.append("`endif  // FATORI_PBLOCKS_SVH")
    txt = "\n".join(lines)
    with out.open("w", encoding="utf-8") as fh:
        fh.write(txt + "\n")
    return out


# --- Emit TCL -----------------------------------------------------------------
def _slice_range(x0: int, y0: int, x1: int, y1: int) -> str:
    return f"SLICE_X{x0}Y{y0}:SLICE_X{x1}Y{y1}"

def _emit_tcl(all_targets: Dict[str, Any], enabled: Dict[str, bool], out: Path, board: str) -> Path:
    """Write fatori_pblocks.tcl for enabled targets."""
    lines: List[str] = []
    lines.append("# =============================================================================")
    lines.append("# FATORI-V • Generated Vivado TCL (Pblocks)")
    lines.append("# File: fatori_pblocks.tcl")
    lines.append("# -----------------------------------------------------------------------------")
    lines.append(f"# Board: {board}")
    lines.append("# =============================================================================")
    lines.append("")
    for tname, meta in all_targets.items():
        if not enabled.get(tname, False):
            continue
        pb = f"pb_{tname}"
        path = str(meta.get("path") or "").strip()
        rects = list(meta.get("rects") or [])
        lines.append(f"create_pblock {pb}")
        for r in rects:
            x0 = int(r.get("x0")); y0 = int(r.get("y0")); x1 = int(r.get("x1")); y1 = int(r.get("y1"))
            rng = _slice_range(x0, y0, x1, y1)
            lines.append(f"resize_pblock [get_pblocks {pb}] -add {{{rng}}}")
        if path:
            lines.append(f"add_cells_to_pblock [get_pblocks {pb}] [get_cells -hier -quiet {path}]")
        lines.append("")
    txt = "\n".join(lines)
    with out.open("w", encoding="utf-8") as fh:
        fh.write(txt + "\n")
    return out


# --- Public entry -------------------------------------------------------------
def generate(cfg: Dict[str, Any], run_id: str, final_dir: Path, copy_to_results: bool, verbose: bool=False) -> List[Path]:
    """
    Import entry point used by fatori_defines.py.
    Returns a list of produced header files to be included by the master header.
    """
    area_prof = str(_get(cfg, "general", "fault_injection", "area_profile", default="")).strip().lower()
    if area_prof not in ("modules", "module"):
        return []

    ident = _get(cfg, "run", "identification", default={}) or {}
    seed = ident.get("seed", "-")
    board = str(_get(cfg, "run", "hardware", "board", default="")).strip()
    if not board:
        raise ValueError("run.hardware.board is required for modules pblocks generation")

    all_targets = (_load_modules_map(board) or {}).get("targets", {}) or {}

    # Prefer the modern 'modules' section; keep legacy 'module' as a fallback.
    area_sec = _get(cfg, "specifics", "fault_injection", "area", "modules", default={}) or {}
    if not area_sec:
        area_sec = _get(cfg, "specifics", "fault_injection", "area", "module", default={}) or {}
    tgt_cfg = area_sec.get("targets", {}) or {}

    # Normalize boolean-like values from the config into a {name: bool} map.
    enabled = {
        k: (bool(v) if isinstance(v, bool) else (str(v).strip().lower() in ("on", "true", "1", "yes")))
        for k, v in tgt_cfg.items()
    }

    final_dir.mkdir(parents=True, exist_ok=True)
    svh = final_dir / "fatori_pblocks.svh"
    tcl = final_dir / "fatori_pblocks.tcl"

    _emit_svh(all_targets, enabled, svh, run_id, seed)
    _emit_tcl(all_targets, enabled, tcl, board)

    if copy_to_results:
        s = _load_settings()
        res = Path(getattr(s, "RESULTS_DIR_NAME", "results")) / run_id / getattr(s, "DEFINES_RESULTS_SUBDIR", "gen")
        res.mkdir(parents=True, exist_ok=True)
        shutil.copy2(svh, res / svh.name)
        shutil.copy2(tcl, res / tcl.name)

    return [svh]
