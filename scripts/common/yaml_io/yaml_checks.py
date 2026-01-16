# =============================================================================
# FATORI-V • YAML Checks
# File: yaml_checks.py
# -----------------------------------------------------------------------------
# Basic YAML sanity checks called during loading.
# =============================================================================

from pathlib import Path


def run_yaml_checks(data, path: Path):
    """
    Perform basic sanity checks on loaded YAML data.
    
    This is called immediately after YAML loading to catch obvious issues.
    Full validation is performed by the validation system.
    
    Args:
        data: The loaded YAML dictionary
        path: Path to the YAML file for error messages
    
    Raises:
        ValueError: If basic structural issues are found
    """
    # Check that data is a dictionary
    if not isinstance(data, dict):
        raise ValueError(f"YAML file {path} must contain a dictionary at top level")
    
    # Check for completely empty YAML
    if not data:
        raise ValueError(f"YAML file {path} is empty or contains no keys")
    
    # Additional basic checks can be added here
    # Full validation is done by scripts.validation modules