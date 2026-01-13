### scripts/common/yaml_io/load_run_yaml.py
# =============================================================================
# FATORI-V • YAML Loader
# File: load_run_yaml.py 
# -----------------------------------------------------------------------------
# Loads a run YAML, applies basic validation and triggers YAML checks.
#=============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from scripts.common.yaml_io import yaml_checks


def load_run_yaml(path: Path) -> Dict[str, Any]:
    """
    Load a run YAML file into a Python dictionary and run basic checks.

    Args:
        path: Path to the YAML file.

    Returns:
        A dictionary with the parsed YAML contents. If the file is empty,
        an empty dict is returned.

    Raises:
        ValueError: If the top-level YAML node is not a mapping.
        OSError:    If the file cannot be read.
    """
    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    if data is None:
        data = {}

    if not isinstance(data, dict):
        raise ValueError(
            f"Run YAML '{path}' must have a mapping at the top level, "
            f"got {type(data).__name__}"
        )

    # Let the user-defined checks run; by default this is a no-op.
    yaml_checks.run_yaml_checks(data, path)

    return data
