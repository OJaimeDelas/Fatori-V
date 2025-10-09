# =============================================================================
# FATORI-V • Orchestrator Settings
# File: settings.py
# -----------------------------------------------------------------------------
# Centralized paths and defaults for the top-level runner (fatori-v.py).
#
# Responsibilities
#   • Define authoritative top-level defaults (device, baud, ACME/EBD paths,
#     runs/results folders). The orchestrator passes these explicitly to the
#     lower layers to avoid ambiguity when similar defaults also exist under
#     fi/settings.py.
#   • Provide stable locations for the runs/ folder (YAML inputs) and results/
#     folder (per-run outputs mirrored for quick inspection).
#   • Enumerate finish-line hints so the orchestrator can chain runs without
#     altering fi.fault_injection behavior.
#   • Expose terminal controls for how the FI console should present itself
#     when invoked by the orchestrator (simple header; hide help blocks).
#
# Notes
#   • All paths are resolved relative to fatori-v.py at runtime.
#   • The FI framework keeps writing its own detailed logs under
#     results/<run>/<session>/ as before. The orchestrator does not replace
#     that log; it only mirrors key artifacts to the top-level results folder.
# =============================================================================

from __future__ import annotations

# --- Top-level folders (relative to fatori-v.py location) --------------------
RUNS_DIR_NAME: str = "runs"        # where YAML run files live
RESULTS_DIR_NAME: str = "results"  # where the orchestrator mirrors artifacts

# --- Defines output control ---------------------------------------------------
# Where generated define headers (e.g., fatori_defines.svh and feature headers)
# are written by default. This is also where downstream RTL expects them.
# May be an absolute or relative path; relative is resolved from fatori-v/.
DEFINES_FINAL_PATH: str = "."
# If True, a second copy of all generated headers is mirrored to
# results/<run_id>/gen for archival alongside run artifacts.
DEFINES_COPY_TO_RESULTS: bool = True
# Subdirectory name under results/<run_id> to store the mirrored headers.
DEFINES_RESULTS_SUBDIR: str = "gen"

# --- Serial defaults (authoritative at the top layer) ------------------------
DEFAULT_SEM_DEVICE: str = "/dev/ttyUSB0"
DEFAULT_BAUDRATE: int = 1_250_000

# Path to the board module rectangles map (YAML). Used by fatori-v.py to
# generate pblock TCL and by area 'module' profile to resolve rectangles.
BOARD_MODULE_MAP_PATH: str = "fatori-v/scripts/pblocks/boards/xcku040/modules.yaml"

# Generate a per-run Vivado TCL with the enabled pblocks. The TCL will be
# written under results/<run_id>/pblocks_<run_id>.tcl. Running Vivado is
# not automated at this layer; the TCL can be sourced manually or by CI.
GENERATE_PBLOCK_TCL: bool = True

# --- FI / ACME integration defaults -----------------------------------------
# Essential Bits default path for ACME-backed area profiles (confirmed path).
EBD_DEFAULT_PATH: str = "fi/build/design.ebd"

# ACME cache directory (device/module address lists).
ACME_CACHE_DIR: str = "fi/build/acme"

# Default board key for ACME device maps (UltraScale KU040).
ACME_DEFAULT_BOARD: str = "xcku040"

# --- Sessions / seeds --------------------------------------------------------
DEFAULT_SESSION_LABEL: str = "ctrl01"
# If YAML lacks a seed, None here means the orchestrator will generate
# a random 64-bit seed per run; otherwise set a fixed integer to pin runs.
DEFAULT_GLOBAL_SEED = None

# --- Console finish detection ------------------------------------------------
# FINISH_LINE_HINTS lists substrings that indicate a campaign finished.
# fatori-v.py streams FI stdout and, on seeing any of these, sends "exit"
# so fi.fault_injection can close cleanly and flush its log. This avoids
# switching to manual mode between YAML runs.
FINISH_LINE_HINTS = (
    "] finished.",  # canonical suffix printed by fi/fault_injection watcher
)

# --- Artifact names mirrored into results/<run_id>/ --------------------------
TOP_COPY_INJECTION_LOG: str = "injection_log.txt"
TOP_COPY_ACME_LIST: str = "acme_injection_addresses.txt"
TOP_SUBDIR_RUN_YAML: str = "run_yaml"
TOP_SUBDIR_REPORTS: str = "reports"
TOP_SUBDIR_PLOTS: str = "plots"

# --- Terminal controls for FI when launched by the orchestrator --------------
# The orchestrator requests the FI console to use a simpler header and hide
# help-heavy sections. These flags are translated into CLI options passed
# to "python -m fi.fault_injection".
FI_HEADER_STYLE_FOR_RUNS: str = "simple"  # 'simple' or 'fancy'
FI_HIDE_CONSOLE_COMMANDS: bool = True
FI_HIDE_SEM_CHEATSHEET: bool = True
FI_HIDE_START_MODE: bool = True

# --- Optional automatic application of generated pblocks.tcl -----------------
# If True, the orchestrator will attempt to launch Vivado in batch mode and
# source the generated fatori_pblocks.tcl after it is created. When False,
# the script only prints clear instructions about how to source it manually.
APPLY_PBLOCKS_TCL: bool = False

# Vivado executable to use when APPLY_PBLOCKS_TCL is True.
VIVADO_BIN: str = "vivado"

# Optional absolute/relative path to an .xpr project. If provided, the path is
# exported as environment variable FATORI_XPR for TCLs that wish to open it.
# If left as None, the TCL is expected to be sourced inside an already-open
# project context.
VIVADO_XPR: str | None = None