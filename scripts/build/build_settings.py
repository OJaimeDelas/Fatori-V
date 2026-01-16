# =============================================================================
# FATORI-V • Build Settings
# File: build_settings.py
# -----------------------------------------------------------------------------
# Settings for build orchestration system.
# =============================================================================

# Build phases
PHASE_CLEAN_SETUP = "clean_setup"
PHASE_IBEX_SETUP = "ibex_setup"
PHASE_FPGA_BIT = "fpga_bit"
PHASE_FW_COMPILE = "fw_compile"
PHASE_FPGA_RUN = "fpga_run"

# Make command defaults
DEFAULT_MAKE_JOBS = 4
DEFAULT_MAKE_TARGET_SEPARATOR = " "

# File backup settings
BACKUP_ENABLED = True
BACKUP_SUFFIX = ".backup"

# Build timeout (seconds, -1 for no timeout)
BUILD_TIMEOUT_DEFAULT = 3600

# Build workflow settings
CLEAN_BEFORE_BUILD = True  # Run clean setup before building
RUN_IBEX_SETUP = True      # Run ibex-setup before FPGA build
MAKE_PARALLEL_JOBS = 4     # Number of parallel jobs for make (-j flag)

# UART/FPGA execution settings
DEFAULT_GRAB_TIMEOUT = 300  # Default timeout for UART grab (seconds)
DEFAULT_FPGA_TIMEOUT = 600  # Default timeout for FPGA operations (seconds)