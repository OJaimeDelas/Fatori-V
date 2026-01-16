# =============================================================================
# FATORI-V • Pblocks Settings
# File: pblocks_settings.py
# -----------------------------------------------------------------------------
# Settings for pblock generation system.
# =============================================================================

# Generated file names
PBLOCKS_HEADER_NAME = "fatori_pblocks.svh"
PBLOCKS_TCL_NAME = "fatori_pblocks.tcl"

# Include guard name
PBLOCKS_INCLUDE_GUARD = "FATORI_PBLOCKS_SVH"

# Pblock configuration file for external pblock_gen system
PBLOCK_CONFIG_NAME = "pblock_config.yaml"

# Device-specific defaults
XCKU040_CLOCK_REGIONS = {
    "x_min": 0,
    "x_max": 5,
    "y_min": 0,
    "y_max": 3
}