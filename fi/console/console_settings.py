# =============================================================================
# FATORI-V • Fault Injection Framework
# File: fi/console/console_settings.py
# -----------------------------------------------------------------------------
# Console appearance, colors, prompts, header lines, help text, and the SEM
# command cheat sheet shown by the interactive console.
#
# Purpose
#   Centralizes all console-facing presentation and UX knobs. Logic imports
#   styles and strings from this module to keep code paths free of literals.
#
# Structure
#   • ANSI palette and helpers (colorize/mkstyle)
#   • Layout and rule characters
#   • Named style tokens used by the console
#   • Prompt strings and mode switch styling
#   • Tag prefixes and colors for console echo
#   • Runtime behavior knobs used by the console loop
#   • Help text blocks
#   • UART formatting knobs mirrored for discoverability
#   • Log formatting knobs (TX asterisk spacing)
#   • Header style selection and section visibility (added; defaults preserve behavior)
# =============================================================================

from __future__ import annotations

# ---------- ANSI color/style palette -----------------------------------------
ANSI = {
    "reset": "\x1b[0m",
    "bold":  "\x1b[1m",
    # Standard 8 colors
    "black":   "\x1b[30m", "red":     "\x1b[31m", "green":  "\x1b[32m",
    "yellow":  "\x1b[33m", "blue":    "\x1b[34m", "magenta":"\x1b[35m",
    "cyan":    "\x1b[36m", "white":   "\x1b[37m",
    # Bright variants
    "br_black":  "\x1b[90m", "br_red":    "\x1b[91m", "br_green": "\x1b[92m",
    "br_yellow": "\x1b[93m", "br_blue":   "\x1b[94m", "br_magenta":"\x1b[95m",
    "br_cyan":   "\x1b[96m", "br_white":  "\x1b[97m",
}

def colorize(text: str, style: str | None) -> str:
    """
    Apply an ANSI style to text; returns text unchanged if style is falsy.
    Styles should end with ANSI['reset'] to avoid color leakage.
    """
    if not style:
        return text
    return f"{style}{text}{ANSI['reset']}"

def mkstyle(*names: str) -> str:
    """
    Compose a style by concatenating palette entries by name.
    Example: mkstyle('bold', 'br_blue')
    """
    return "".join(ANSI[n] for n in names if n in ANSI)

# ---------- layout and rules --------------------------------------------------
LINE_WIDTH       = 110          # header/help width
BIG_LINE_CHAR    = "="          # for major separators
SMALL_LINE_CHAR  = "-"          # for minor separators

# Line styles (colors)
BIG_LINE_STYLE   = mkstyle("br_blue")
SMALL_LINE_STYLE = mkstyle("br_blue")

# Section headers (e.g., "Console commands", "SEM IP commands")
SECTION_HEADER_STYLE = mkstyle("br_red", "bold")

# Help bodies use neutral text color for readability
HELP_BODY_STYLE       = mkstyle("white")
HEADER_TITLE_STYLE    = mkstyle("bold", "br_green")

# Header label/value styles
HEADER_LABEL_STYLE         = mkstyle("br_white")
HEADER_VALUE_STYLE         = mkstyle("white")
HEADER_RUN_VALUE_STYLE     = mkstyle("br_green")
HEADER_SESSION_VALUE_STYLE = mkstyle("br_green")
HEADER_TIME_VALUE_STYLE    = mkstyle("br_green")

# Prompt strings
PROMPT_DRIVEN = ""
PROMPT_MANUAL = "> "

# Mode switch visual rule (printed before INFO when changing modes)
SWITCH_RULE_STYLE = mkstyle("br_red")

# Tag prefixes used by the console printer
PREFIX_INFO  = "[INFO] "
PREFIX_TX    = "[SEND] "
PREFIX_RX    = "[RECV] "
PREFIX_ERROR = "[ERROR] "

# Tag colors (tune here)
TAG_INFO = mkstyle("br_blue")
TAG_SEND = mkstyle("br_yellow")
TAG_RECV = mkstyle("br_green")
TAG_ERROR = mkstyle("br_red")

# ---------- runtime behaviour knobs ------------------------------------------
# Initial state to push the SEM core into when the console starts.
#   'observe' -> send O (enter Observation)
#   'idle'    -> send I (enter Idle)
START_MODE = "idle"

# Whether to issue a one-shot status (S) right after the start-mode transition.
SEND_STATUS_ON_START = True

# Default interval for "watch" command (seconds)
DEFAULT_WATCH_INTERVAL_S = 1.0

# Background RX printer poll period (seconds)
RX_PRINTER_POLL_S = 0.03

# Manual prompt gating: how long to wait after last RX line before printing '>'
# The console’s manual-mode gate uses these as suggested defaults.
MANUAL_PROMPT_QUIET_MS   = 1500   # quiet window before '>' appears
MANUAL_PROMPT_MAXWAIT_MS = 2500   # hard cap to avoid starvation

# Consider recent TX activity before printing the manual prompt.
MANUAL_PROMPT_CONSIDER_TX = True
MANUAL_PROMPT_TX_QUIET_MS = 350

# Control whether injection TX echoes are presentation-gated to follow SC 00.
# Disabling does not change TX pacing, only the console echo ordering.
INJECTION_ECHO_GATE_ENABLED = True

# ---------- help text blocks --------------------------------------------------
CONSOLE_HELP = """\
  inject <ADDR>        one-shot inject (ADDR is LFA or PFA-encoded; may include word/bit)
  assist [MS]          assist window; default 1500 ms if omitted
  status               one-shot parsed counters
  watch [S]            periodic status; default 1.0s; Ctrl+C to stop
  manual               switch to manual mode (raw SEM commands)
  help                 show this help
  sem                  show SEM command cheat sheet
  exit                 close the session
"""

SEM_CHEATSHEET = """\
  S                 : Status report (valid in Idle and Observation).
  O                 : Enter Observation (command from Idle; mitigation modes only).
  I                 : Enter Idle (command from Observation or Detect-only).
  D                 : Enter Detect-only (command from Idle).
  U                 : Enter Diagnostic Scan (single sweep; command from Idle).

  N <ADDR>          : Error injection using frame address encoding.
                       • Default format uses 10 digit LFA with word/bit fields encoded into the hex.
                         Example: N C00A098000
                       • PFA-based injection is also supported.

  Q <ADDR>          : Configuration frame read (LFA or PFA accepted).
                       • Word/bit in the address are ignored; returns entire frame contents.

  T <ADDR>          : Frame address translation between PFA and LFA (valid in Idle).

  P <REG>           : Configuration register read (“peek”), valid in Idle.
                       • Argument is 2 hex digits (binary 0ssrrrr: SLR select + reg index).

  X <ADDR>          : External memory (Xmem) read; valid in Idle when classification is enabled.

  R <xx>            : Software reset; argument don’t-care; valid in Idle.
"""

# ---------- I/O formatting & timeouts (mirrored for discoverability) ----------
# These are mirrored to keep user-facing knobs in one place.
CR_TERMINATOR   = "\r"
READ_TIMEOUT_S  = 0.05
WRITE_TIMEOUT_S = 0.10
OPEN_TIMEOUT_S  = 2.0
PROMPT_REGEX    = r"^[IOD]>\s*$"

# ---------- log formatting knobs ---------------------------------------------
# Number of spaces inserted between the transmitted command string and
# the trailing '*' marker in TX log lines.
LOG_TX_ASTERISK_SPACES = 15

# ---------- header style & section visibility (new; defaults keep behavior) ---
# Header modes:
#   • 'fancy'  -> original centered banner + full help sections
#   • 'simple' -> thin blue rules and a left-aligned green "SEM Console" title
HEADER_STYLE_DEFAULT = "fancy"    # default used by fi.fault_injection unless overridden
HEADER_STYLE_FANCY   = "fancy"
HEADER_STYLE_SIMPLE  = "simple"

# Section visibility defaults (fi.fault_injection may override per-run)
SHOW_CONSOLE_COMMANDS_DEFAULT = True
SHOW_SEM_CHEATSHEET_DEFAULT   = True
SHOW_START_MODE_DEFAULT       = True

# -----------------------------------------------------------------------------
# End of file
# -----------------------------------------------------------------------------
