# =============================================================================
# FATORI-V • Global Settings
# File: fatori_settings.py
# -----------------------------------------------------------------------------
# Defines global paths and global-level defaults for FATORI-V runs.
#=============================================================================
# All paths relative to the repository root '. = Fatori-v/'

# -----------------------------------------------------------------------------
# Base project directories (relative to the repository root)
# -----------------------------------------------------------------------------
RUNS_DIR_NAME: str         = "runs"         # where run YAML files live
RESULTS_DIR_NAME: str      = "results"      # where per-run results are stored
GEN_DIR_NAME: str          = "gen"          # where generated headers are kept
BUILD_DIR_NAME: str        = "build"        # build artefacts and user inputs
HARDWARE_DIR_NAME: str     = "hardware"     # RTL overrides on top of architecture
ARCHITECTURE_DIR_NAME: str = "architecture" # reference architecture submodule
FI_DIR_NAME: str           = "fi"           # FI console and its build artefacts

# -----------------------------------------------------------------------------
# Run defaults (identification, seeds, sessions)
# -----------------------------------------------------------------------------
DEFAULT_GLOBAL_SEED = None          # if None, a new random seed is generated

# -----------------------------------------------------------------------------
# Header / defines 
# -----------------------------------------------------------------------------
GEN_CPY_TO_RESULTS: bool  = True  # Copies generated files to results/<run>/gen

# -----------------------------------------------------------------------------
# Vivado
# -----------------------------------------------------------------------------
VIVADO_BIN: str         = "vivado" # Vivado executable name or path

# -----------------------------------------------------------------------------
# Board Conections 
# -----------------------------------------------------------------------------
DEFAULT_DEVICE: str = "/dev/ttyUSB0"    # default UART for Fatori-V
DEFAULT_FPGA_TX_PIN: str = "D20"         # default UART tx pin for Fatori-V
DEFAULT_FPGA_RX_PIN: str = "C19"         # default UART tx pin for Fatori-V
DEFAULT_BAUDRATE: int   = 115_200       # default baudrate for Fatori-V


# -----------------------------------------------------------------------------
# Result layout (within results/<run>/)
# -----------------------------------------------------------------------------
TOP_COPY_INJECTION_LOG: str = "injection_log.txt"
TOP_COPY_ACME_LIST: str     = "acme_injection_addresses.txt"

TOP_SUBDIR_RUN_YAML: str = "."  # optional place to mirror the YAML
TOP_SUBDIR_REPORTS: str  = "reports"   # build-time reports
TOP_SUBDIR_PLOTS: str    = "plots"     # plots derived from metrics

# -----------------------------------------------------------------------------
# FI console and SEM
# -----------------------------------------------------------------------------
DEFAULT_SEM_DEVICE: str = "/dev/ttyUSB0"   # default UART for SEM
DEFAULT_SEM_FPGA_TX_PIN: str = "F18" # default UART tx pin for SEM console
DEFAULT_SEM_FPGA_RX_PIN: str = "G19" # default UART rx pin for SEM console
DEFAULT_SEM_BAUDRATE: int   = 1_250_000    # default baudrate for SEM UART

EBD_DEFAULT_PATH: str   = "fi/build/design.ebd"     # default EBD file for ACME
ACME_CACHE_DIR: str     = "fi/build/acme"           # where ACME caches results
ACME_DEFAULT_BOARD: str = "xcku040"                 # default board ID for ACME

FI_HEADER_STYLE_FOR_RUNS: str      = "simple"
FI_HIDE_CONSOLE_COMMANDS: bool     = True
FI_HIDE_SEM_CHEATSHEET: bool       = True
FI_HIDE_START_MODE: bool           = True
