# =============================================================================
# FATORI-V • Mappings • Board Mapping
# File: board_mapping.py
# -----------------------------------------------------------------------------
# Maps YAML board names to make BOARD parameter values.
# =============================================================================

from scripts.common.common_settings import KEY_HW_BOARD

# Mapping from YAML board names to make BOARD= values
# These correspond to board definitions in architecture/hardware/fpga/vivado/
BOARD_DICT = {
    "xcku040": "iob_aes_ku040_db_g",
    "aes-ku040-db-g": "iob_aes_ku040_db_g",
    "aes_ku040_db_g": "iob_aes_ku040_db_g",
    "iob_aes_ku040_db_g": "iob_aes_ku040_db_g",
    # Add other boards as needed
}

# Default board if not specified
DEFAULT_BOARD_YAML = "xcku040"


def get_make_board_name(yaml_board):
    """
    Convert a YAML board name to the make BOARD= parameter value.
    
    This translates user-friendly board names in YAML to the actual
    directory names used in the architecture's board definitions.
    
    Args:
        yaml_board: Board name as specified in YAML (can be None)
    
    Returns:
        String suitable for make BOARD= parameter
    
    Raises:
        ValueError: If board name is not recognized
    """
    # Handle None/empty - use default
    if not yaml_board:
        yaml_board = DEFAULT_BOARD_YAML
    
    # Convert to lowercase for case-insensitive matching
    yaml_board_lower = yaml_board.lower()
    
    # Look up in mapping dictionary
    if yaml_board_lower in BOARD_DICT:
        return BOARD_DICT[yaml_board_lower]
    
    # If not found, raise error with helpful message
    valid_boards = ", ".join(sorted(set(BOARD_DICT.keys())))
    raise ValueError(
        f"Unknown board '{yaml_board}'. Valid boards: {valid_boards}"
    )


def is_valid_board(yaml_board):
    """
    Check if a board name is valid.
    
    Args:
        yaml_board: Board name to check
    
    Returns:
        Boolean indicating if board is recognized
    """
    if not yaml_board:
        return True  # Empty/None defaults to valid board
    
    yaml_board_lower = yaml_board.lower()
    return yaml_board_lower in BOARD_DICT


def get_supported_boards():
    """
    Get list of all supported board names.
    
    Returns:
        List of valid board name strings
    """
    return sorted(set(BOARD_DICT.keys()))