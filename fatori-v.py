# =============================================================================
# FATORI-V • Global Controller
# File: fatori-v.py
# -----------------------------------------------------------------------------
# Top-level controller that iterates over run YAML files and drives FI per run.
#=============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, List

import fatori_settings as cfg

# YAML loading and run-level helpers
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.common.yaml_io.run_config import (
    find_run_yamls,
    preview_runs,
    derive_run_id,
    resolve_global_seed,
)

# CLI banners
from scripts.common.cli_style.banners import (
    print_main_banner,
    print_run_header,
    print_run_footer,
)

# Per-run layout in results/
from scripts.common.run_scripts.run_layout import (
    RunPaths,
    ensure_results_dirs,
    copy_run_yaml_to_results,
)

# FI interface helpers
from scripts.common.fi_scripts.fi_interface import (
    build_area_profile,
    build_time_profile,
    build_fi_command,
    run_fi_console,
)


def main(argv: List[str] | None = None) -> int:
    """
    Discover runs, and for each YAML:
      - load configuration,
      - derive run_id and seed,
      - set up results/<run_id>/,
      - build FI area/time profiles,
      - launch the FI console.
    """
    runs_dir = Path(cfg.RUNS_DIR_NAME)

    yaml_paths = find_run_yamls(runs_dir)
    if not yaml_paths:
        print(f"[INFO] No run YAML files found in '{runs_dir}'. Nothing to do.")
        return 0

    previews = preview_runs(yaml_paths)
    print_main_banner(previews)

    for yaml_path in yaml_paths:
        # ---------------------------------------------------------------------
        # Load full run configuration for this YAML
        # ---------------------------------------------------------------------
        run_cfg: dict[str, Any] = load_run_yaml(yaml_path)

        # Identification and seed
        run_id = derive_run_id(run_cfg, yaml_path)
        seed = resolve_global_seed(run_cfg, cfg.DEFAULT_GLOBAL_SEED)

        # ---------------------------------------------------------------------
        # Prepare per-run directory structure under results/<run_id>/
        # ---------------------------------------------------------------------
        run_paths: RunPaths = ensure_results_dirs(run_id, cfg)
        copy_run_yaml_to_results(yaml_path, run_paths, cfg)

        # ---------------------------------------------------------------------
        # Build FI area/time profiles based on the YAML contents
        # ---------------------------------------------------------------------
        area_profile, area_args_csv = build_area_profile(run_cfg, seed)
        time_profile, time_args_csv = build_time_profile(run_cfg)

        print_run_header(
            run_id=run_id,
            yaml_filename=yaml_path.name,
            area_profile=area_profile,
            time_profile=time_profile,
            seed=seed,
        )

        # ---------------------------------------------------------------------
        # Build FI command-line and launch FI console
        # ---------------------------------------------------------------------
        fi_cmd = build_fi_command(
            run_id=run_id,
            seed=seed,
            area_profile=area_profile,
            area_args_csv=area_args_csv,
            time_profile=time_profile,
            time_args_csv=time_args_csv,
        )

        # exit_code = run_fi_console(fi_cmd)

        print_run_footer(run_id)

        if exit_code != 0:
            print(
                f"[WARN] FI console for run '{run_id}' exited with "
                f"non-zero code {exit_code}"
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
