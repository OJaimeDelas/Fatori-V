# =============================================================================
# FATORI-V • Global Settings
# File: fatori_settings.py
# -----------------------------------------------------------------------------
# User-editable configuration for all Fatori-V operations.
# =============================================================================

from pathlib import Path

# =============================================================================
# Dry Run Mode
# =============================================================================

# When True, system runs through all phases but prints commands instead of executing
DRY_RUN_MODE = False

# ==============================================================================
# Directory Structure
# ==============================================================================

# Root directory is the location of this settings file
ROOT_DIR = Path(__file__).parent.resolve()

# Main directories
RUNS_DIR = ROOT_DIR / "runs"
RESULTS_DIR = ROOT_DIR / "results"
INPUTS_DIR = ROOT_DIR / "inputs"
TMP_DIR = ROOT_DIR / "tmp"
SCRIPTS_DIR = ROOT_DIR / "scripts"
FI_DIR = ROOT_DIR / "fi"
BENCHMARKS_DIR = ROOT_DIR / "benchmarks"
ARCHITECTURE_DIR = ROOT_DIR / "architecture"
BUILDDIR_NAME = "iob_soc_V1.0"
BUILDDIR = ROOT_DIR / BUILDDIR_NAME

# Subdirectories under tmp/
TMP_GENERATED_DIR = TMP_DIR / "generated"
TMP_BACKUP_DIR = TMP_DIR / "backup"
TMP_TCL_DIR = TMP_DIR / "tcl"
TMP_SYNC_DIR = TMP_DIR / "sync"

# Subdirectories under inputs/
INPUTS_HARDWARE_DIR = INPUTS_DIR / "hardware"
INPUTS_SOFTWARE_DIR = INPUTS_DIR / "software"
INPUTS_OTHER_DIR = INPUTS_DIR / "others"
INPUTS_TCL_DIR = INPUTS_DIR / "tcl"

# ==============================================================================
# Build System Configuration
# ==============================================================================

# Reports directory (relative to builddir)
REPORTS_DIR_RELATIVE = "hardware/fpga/reports"

# Vivado TCL input directory (relative to builddir)
VIVADO_INPUT_RELATIVE = "../tmp/tcl/"

# Benchmark directory (relative to builddir)
BENCHMARK_DIR_RELATIVE_BASE = "../../benchmarks"

# Sync file for benchmark-FI coordination
SYNC_FILE_NAME = "sync_file.sync"
SYNC_FILE_RELATIVE_PATH = "hardware/fpga/sync_file.sync"

# External tool scripts
VIVADO_PARSER_SCRIPT = SCRIPTS_DIR / "reports" / "vivado_report_system.py"

# ==============================================================================
# User-Editable Defaults
# ==============================================================================

# Board configuration
DEFAULT_BOARD = "xcku040"
BOARD_GRAB_TIMEOUT_DEFAULT = 1000

# FI configuration defaults
FI_DEVICE_DEFAULT = "/dev/ttyUSB1"
FI_BAUDRATE_DEFAULT = 1250000
FI_LOG_LEVEL_DEFAULT = "verbose"

# Build strategy
FULL_MAKE_BUILD = True  # True: fpga-run per benchmark, False: fpga-bit-only + fpga-fw-run

# Make targets 
MAKE_FPGA_RUN = "fpga-run"
MAKE_FPGA_BIT_ONLY = "fpga-bit-only"
MAKE_FPGA_FW_RUN = "fpga-fw-run"
MAKE_JOBS_DEFAULT = 4

# Default values for features
DEFAULT_GLOBAL_SEED = 42
DEFAULT_HPMC_NUM_LEVEL_0 = 0
DEFAULT_HPMC_NUM_LEVEL_PLUS = 10
DEFAULT_HPMC_WIDTH = 32
DEFAULT_MON_N = 3
DEFAULT_MON_M = 2
DEFAULT_BENCHMARK_TIMEOUT = -1

# Validation defaults
VALIDATION_STRICT_DEFAULT = True
VALIDATION_SAVE_VERIFIED_DEFAULT = True

# ==============================================================================
# File Names (for reference in path helpers)
# ==============================================================================

# Static input file names
FATORI_REGISTERS_YAML_NAME = "fatori_registers.yaml"
SYSTEM_DICT_YAML_NAME = "system_dict.yaml"
SYSTEM_HIERARCHY_YAML_NAME = "system_hierarchy.yaml"
GEN_LOCATIONS_YAML_NAME = "gen_locations.yaml"
HARDWARE_LOCATIONS_YAML = "locations.yaml"
SOFTWARE_LOCATIONS_YAML = "locations.yaml"