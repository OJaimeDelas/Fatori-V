# =============================================================================
# FATORI-V • Validation Settings
# File: validation_settings.py
# -----------------------------------------------------------------------------
# Configuration for the validation system.
# =============================================================================

# Validation modes
STRICT_MODE_DEFAULT = True
AUTO_CORRECT_DEFAULT = False

# Error severity levels
SEVERITY_ERROR = "ERROR"
SEVERITY_WARNING = "WARNING"
SEVERITY_INFO = "INFO"

# M-of-N validation bounds
MON_N_MIN = 1
MON_N_MAX = 5
MON_M_MIN = 0

# Percentage validation bounds
PERCENTAGE_MIN = 0
PERCENTAGE_MAX = 100

# Metrics level bounds
METRICS_LEVEL_MIN = 0
METRICS_LEVEL_MAX = 5

# HPMC counter bounds
HPMC_NUM_MIN = 0
HPMC_NUM_MAX = 29
HPMC_WIDTH_MIN = 1
HPMC_WIDTH_MAX = 64

# Validation result keys
KEY_VALID = "valid"
KEY_ERRORS = "errors"
KEY_WARNINGS = "warnings"
KEY_CORRECTIONS = "corrections"


def create_validation_result():
    """
    Create an empty validation result structure.
    
    Returns:
        Dictionary with keys for validation status, errors, warnings, and corrections.
    """
    return {
        KEY_VALID: True,
        KEY_ERRORS: [],
        KEY_WARNINGS: [],
        KEY_CORRECTIONS: []
    }


def add_error(result, message):
    """Add an error message to validation result and mark as invalid."""
    result[KEY_ERRORS].append(message)
    result[KEY_VALID] = False


def add_warning(result, message):
    """Add a warning message to validation result."""
    result[KEY_WARNINGS].append(message)


def add_correction(result, message):
    """Add a correction message to validation result."""
    result[KEY_CORRECTIONS].append(message)