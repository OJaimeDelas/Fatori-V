# =============================================================================
# FATORI-V • Configuration • Hardware Constants
# File: constants.py
# -----------------------------------------------------------------------------
# Hardware-wired constants that should not be edited by users.
# =============================================================================

# ==============================================================================
# Logging Constants
# ==============================================================================

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_LEVEL_DEFAULT = "VERBOSE"

# ==============================================================================
# File Generation Formatting
# ==============================================================================

INDENT_SPACES = 4
COMMENT_WIDTH = 80
HEADER_SEPARATOR_CHAR = "="
HEADER_SUB_SEPARATOR_CHAR = "-"
HEADER_WIDTH = 80

# ==============================================================================
# Macro Conventions
# ==============================================================================

MACRO_PREFIX = "FATORI_"
IBEX_PKG_PREFIX = "ibex_pkg::"

# ==============================================================================
# TCL Generation Constants
# ==============================================================================

TCL_INDENT = "  "
TCL_COMMENT_CHAR = "#"

# ==============================================================================
# File Extensions
# ==============================================================================

YAML_EXTENSIONS = [".yaml", ".yml"]
REPORT_EXTENSIONS = [".rpt", ".txt"]

# ==============================================================================
# Build System Constants
# ==============================================================================

VIVADO_LOG_DIR = "logs"
VIVADO_REPORTS_DIR = "reports"

# ==============================================================================
# FI Constants
# ==============================================================================

SEM_IP_NAME = "sem_0"
SEM_CLK_FREQ = 50000000  # 50 MHz
FI_SEM_CLK_HZ = 50000000  # Alias for consistency

# ==============================================================================
# Timeout Constants (in seconds)
# ==============================================================================

DEFAULT_COMMAND_TIMEOUT = 3600   # 1 hour
DEFAULT_MAKE_TIMEOUT = 7200      # 2 hours
DEFAULT_VIVADO_TIMEOUT = 10800   # 3 hours

# ==============================================================================
# Generated File Names
# ==============================================================================

# SystemVerilog headers
FATORI_FEATURES_SVH = "fatori_features.svh"
FATORI_FTM_SVH = "fatori_ftm.svh"
FATORI_REG_MON_SVH = "fatori_reg_mon.svh"
FATORI_LOGIC_MON_SVH = "fatori_logic_mon.svh"
FATORI_SELFTEST_SVH = "fatori_selftest.svh"
FATORI_PBLOCKS_SVH = "fatori_pblocks.svh"

# TCL files
PRE_SYNTHESIS_TCL = "pre_synthesis.tcl"
POST_OPT_TCL = "post_opt.tcl"
POST_ROUTE_TCL = "post_route.tcl"
POST_BITSTREAM_TCL = "post_bitstream.tcl"
PRE_BITSTREAM_TCL = "pre_bitstream.tcl"
SEM_GEN_TCL = "sem_gen.tcl"
REPORT_GEN_TCL = "report_gen.tcl"
FATORI_PBLOCKS_TCL = "fatori_pblocks.tcl"

# Software headers
BENCH_CONFIG_H = "bench_config.h"
METRICS_CONFIG_H = "metrics_config.h"

# Pblock system files
PBLOCK_CONFIG_YAML = "pblock_config.yaml"
PBLOCK_DICT_YAML = "pblock_dict.yaml"
FATORI_REGISTERS_ACTIVE_NAME = "fatori_registers_active.yaml"
SYSTEM_DICT_MERGED_NAME = "system_dict_merged.yaml"

# Results and metrics files
METRICS_FILE_NAME = "metrics.txt"
RUN_SUMMARY_FILE = "run_summary.txt"
METRICS_CSV_FILE = "metrics.csv"
METRICS_XLSX_FILE = "metrics.xlsx"
VERIFIED_CONFIG_FILE = "verified_config.yaml"
CONSOLE_OUTPUT_FILE = "console_output.log"

# ==============================================================================
# Static Input File Names
# ==============================================================================

FATORI_REGISTERS_YAML_NAME = "fatori_registers.yaml"
SYSTEM_DICT_YAML_NAME = "system_dict.yaml"
SYSTEM_HIERARCHY_YAML_NAME = "system_hierarchy.yaml"
GEN_LOCATIONS_YAML_NAME = "gen_locations.yaml"
HARDWARE_LOCATIONS_YAML = "locations.yaml"
SOFTWARE_LOCATIONS_YAML = "locations.yaml"

# ==============================================================================
# Benchmark Constants
# ==============================================================================

# Benchmark directory (relative to builddir)
BENCHMARK_DIR_RELATIVE_BASE = "../../benchmarks"