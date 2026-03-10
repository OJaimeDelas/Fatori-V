# =============================================================================
# FATORI-V • Common YAML I/O • Run YAML Loader
# File: load_run_yaml.py
# -----------------------------------------------------------------------------
# Loads a run YAML, normalises on/off string values, and runs basic checks.
# =============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict

import yaml

from scripts.common.yaml_io import yaml_checks

# String values that are unambiguously on or off regardless of YAML quoting.
# Users may write either the bare YAML keyword (e.g. `enable: off`, which
# yaml.safe_load gives as Python bool False) or the quoted form
# (e.g. `enable: 'off'`, which yaml.safe_load gives as Python string 'off').
# Both are normalised to Python booleans here so the rest of the system
# always sees consistent types.
_STRING_ON  = {"on", "true", "yes", "1", "enabled"}
_STRING_OFF = {"off", "false", "no", "0", "disabled"}


def _normalise_on_off(obj: Any) -> Any:
    """
    Recursively convert on/off string values to Python booleans.

    Only strings whose lowercase form exactly matches a known on/off keyword
    are converted; all other strings, numbers, and nested structures pass
    through unchanged.
    """
    if isinstance(obj, dict):
        return {k: _normalise_on_off(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_normalise_on_off(v) for v in obj]
    if isinstance(obj, str):
        low = obj.lower()
        if low in _STRING_ON:
            return True
        if low in _STRING_OFF:
            return False
    return obj


def load_run_yaml(path: Path) -> Dict[str, Any]:
    """
    Load a run YAML file into a Python dictionary and run basic checks.

    After parsing, all on/off string values are normalised to Python booleans
    so that both `feature: off` and `feature: 'off'` behave identically
    throughout the system.

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

    # Normalise quoted on/off strings to booleans before any other processing.
    data = _normalise_on_off(data)

    # Let the user-defined checks run; by default this is a no-op.
    yaml_checks.run_yaml_checks(data, path)

    return data