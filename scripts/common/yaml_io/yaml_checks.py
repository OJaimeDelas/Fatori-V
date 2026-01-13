# =============================================================================
# FATORI-V • YAML Checks
# File: yaml_checks.py 
# -----------------------------------------------------------------------------
# Defines and runs small consistency checks over the run YAML.
# It's USER-MODIFIABLE (check common/Readme)
#=============================================================================

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Callable


YamlCheck = Callable[[Dict[str, Any], Path], None]


# Global list of check functions. Users can append to this list.
REGISTERED_CHECKS: List[YamlCheck] = []


def run_yaml_checks(cfg: Dict[str, Any], yaml_path: Path) -> None:
    """
    Run all registered YAML checks for a given configuration.

    By default this does nothing, until the user appends checks to
    REGISTERED_CHECKS in this file.
    """
    for check in REGISTERED_CHECKS:
        check(cfg, yaml_path)
