### scripts/common/common_settings.py
# =============================================================================
# FATORI-V • Common Settings
# File: common_settings.py 
# -----------------------------------------------------------------------------
# Provides shared defaults and helpers for common utilities.
#=============================================================================

from __future__ import annotations

# -----------------------------------------------------------------------------
# CLI / banner behaviour
# -----------------------------------------------------------------------------
# Whether to use colour / ANSI escape codes in CLI output.
USE_COLOUR_OUTPUT: bool = True

# Default line width for decorative CLI separators (####, ----, ****, etc.).
CLI_LINE_WIDTH: int = 72

# ANSI colour codes (users can tweak these if they want different colours).
COLOR_RESET: str = "\033[0m"

# Base colours (examples; feel free to change)
COLOR_BRIGHT_MAGENTA: str = "\033[95m"
COLOR_BRIGHT_WHITE: str   = "\033[97m"
COLOR_BRIGHT_BLUE: str    = "\033[94m"
COLOR_BRIGHT_CYAN: str    = "\033[96m"

# Banner colour targets
MAIN_HEADER_LINE_COLOR: str = COLOR_BRIGHT_MAGENTA
MAIN_TITLE_COLOR: str       = COLOR_BRIGHT_WHITE

RUN_HEADER_LINE_COLOR: str  = COLOR_BRIGHT_BLUE
RUN_TITLE_COLOR: str        = COLOR_BRIGHT_CYAN


# -----------------------------------------------------------------------------
# Subprocess behaviour
# -----------------------------------------------------------------------------
# If True, helper functions that run subprocesses should default to
# check=True (raising on non-zero return codes) unless explicitly overridden.
SUBPROCESS_CHECK_BY_DEFAULT: bool = True

# If True, helpers may clean up environment variables passed to subprocesses
# (e.g. strip noisy variables) before spawning child processes.
SUBPROCESS_CLEAN_ENV_BY_DEFAULT: bool = False