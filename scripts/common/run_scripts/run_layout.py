# =============================================================================
# FATORI-V • Common Run Layout
# File: run_layout.py
# -----------------------------------------------------------------------------
# Helpers for creating per-run result directories and copying run YAMLs.
#=============================================================================

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any
import shutil


@dataclass
class RunPaths:
    """
    Collection of important paths for a single run under results/.

    Attributes:
        run_root:    Root directory for this run, e.g. results/<run_id>/.
        reports_dir: Directory for build/implementation reports.
        plots_dir:   Directory for generated plots.
        gen_dir:     Directory for generated headers, or None if mirroring
                     to results/<run>/gen is disabled.
    """
    run_root: Path
    reports_dir: Path
    plots_dir: Path
    gen_dir: Path | None


def _resolve_copy_to_results_flag(settings: Any) -> bool:
    """
    Determine whether generated files should be mirrored to results/<run>/gen.

    Supports both GEN_CPY_TO_RESULTS and DEFINES_COPY_TO_RESULTS for
    compatibility; defaults to False if neither is present.
    """
    if hasattr(settings, "GEN_CPY_TO_RESULTS"):
        return bool(getattr(settings, "GEN_CPY_TO_RESULTS"))
    if hasattr(settings, "DEFINES_COPY_TO_RESULTS"):
        return bool(getattr(settings, "DEFINES_COPY_TO_RESULTS"))
    return False


def ensure_results_dirs(run_id: str, settings: Any) -> RunPaths:
    """
    Create the standard directory layout under results/<run_id>/.

    Uses directory names from the global settings module:
      - RESULTS_DIR_NAME
      - TOP_SUBDIR_REPORTS
      - TOP_SUBDIR_PLOTS
      - GEN_DIR_NAME (if mirroring generated files is enabled)

    Args:
        run_id:   Logical identifier of the run.
        settings: Settings object/module (typically fatori_settings).

    Returns:
        RunPaths instance referencing the created directories.
    """
    results_root = Path(getattr(settings, "RESULTS_DIR_NAME", "results"))
    run_root = results_root / run_id
    run_root.mkdir(parents=True, exist_ok=True)

    reports_name = getattr(settings, "TOP_SUBDIR_REPORTS", "reports")
    plots_name = getattr(settings, "TOP_SUBDIR_PLOTS", "plots")

    reports_dir = run_root / reports_name
    plots_dir = run_root / plots_name

    reports_dir.mkdir(parents=True, exist_ok=True)
    plots_dir.mkdir(parents=True, exist_ok=True)

    gen_dir: Path | None = None
    if _resolve_copy_to_results_flag(settings):
        gen_dir_name = getattr(settings, "GEN_DIR_NAME", "gen")
        gen_dir = run_root / gen_dir_name
        gen_dir.mkdir(parents=True, exist_ok=True)

    return RunPaths(
        run_root=run_root,
        reports_dir=reports_dir,
        plots_dir=plots_dir,
        gen_dir=gen_dir,
    )


def copy_run_yaml_to_results(
    yaml_path: Path,
    run_paths: RunPaths,
    settings: Any,
) -> Path:
    """
    Copy the run YAML into the results directory for this run.

    If TOP_SUBDIR_RUN_YAML is set in settings, the YAML is copied into
    results/<run_id>/<TOP_SUBDIR_RUN_YAML>/; otherwise it is copied directly
    under results/<run_id>/.

    Args:
        yaml_path:  Path to the original YAML file.
        run_paths:  RunPaths instance for this run.
        settings:   Settings object/module (typically fatori_settings).

    Returns:
        Path to the copied YAML inside the results tree.
    """
    subdir_name = getattr(settings, "TOP_SUBDIR_RUN_YAML", None)
    if isinstance(subdir_name, str) and subdir_name.strip():
        target_dir = run_paths.run_root / subdir_name.strip()
        target_dir.mkdir(parents=True, exist_ok=True)
    else:
        target_dir = run_paths.run_root

    dest = target_dir / yaml_path.name
    shutil.copy2(yaml_path, dest)
    return dest
