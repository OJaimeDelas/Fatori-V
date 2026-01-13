# =============================================================================
# FATORI-V • YAML Run Config Helpers
# File: run_config.py
# -----------------------------------------------------------------------------
# Helpers for discovering run YAMLs, deriving run IDs and resolving seeds.
#=============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import random

import yaml



def find_run_yamls(runs_dir: Path) -> List[Path]:
    """
    Find all run YAML files under the given runs directory.

    Currently only scans the top level of `runs_dir` for *.yaml / *.yml files.
    """
    if not runs_dir.exists():
        return []

    yaml_paths: List[Path] = []
    for entry in runs_dir.iterdir():
        if not entry.is_file():
            continue
        if entry.suffix.lower() in (".yaml", ".yml"):
            yaml_paths.append(entry)

    return sorted(yaml_paths, key=lambda p: p.name)


def preview_runs(yaml_paths: List[Path]) -> List[Tuple[str, str]]:
    """
    Build a human-readable preview list for the main banner.

    Returns:
        List of (run_name, yaml_filename) pairs.
        The run_name is taken from run.identification.name when present,
        otherwise it falls back to the YAML filename stem.
    """
    previews: List[Tuple[str, str]] = []

    for path in yaml_paths:
        run_name = path.stem
        try:
            with path.open("r", encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            # Keep the filename stem as the run name on error
            previews.append((run_name, path.name))
            continue

        run_block = data.get("run") or {}
        ident = run_block.get("identification") or {}
        name_val = ident.get("name")

        if isinstance(name_val, str) and name_val.strip():
            run_name = name_val.strip()

        previews.append((run_name, path.name))

    return previews


def derive_run_id(run_cfg: Dict[str, Any], yaml_path: Path) -> str:
    """
    Compute the run ID for this configuration.

    Prefers run.identification.name when present and non-empty, otherwise
    falls back to the YAML filename stem.
    """
    run_block = run_cfg.get("run") or {}
    ident = run_block.get("identification") or {}
    name_val = ident.get("name")

    if isinstance(name_val, str):
        stripped = name_val.strip()
        if stripped:
            return stripped

    return yaml_path.stem


def resolve_global_seed(
    run_cfg: Dict[str, Any],
    default_seed: Optional[int],
) -> int:
    """
    Determine the global seed for this run.

    Priority:
      1) If run.identification.seed is a valid integer, use that.
      2) Else if default_seed is not None, use default_seed.
      3) Else generate a fresh random 64-bit seed.
    """
    run_block = run_cfg.get("run") or {}
    ident = run_block.get("identification") or {}
    yaml_seed = ident.get("seed")

    if isinstance(yaml_seed, int):
        return yaml_seed

    if isinstance(yaml_seed, str):
        # Accept numeric strings too, if they parse cleanly
        try:
            value = int(yaml_seed, 0)
        except ValueError:
            pass
        else:
            return value

    if default_seed is not None:
        return default_seed

    # Fall back to a fresh random 64-bit value
    return random.getrandbits(64)
