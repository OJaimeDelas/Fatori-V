# =============================================================================
# FATORI-V • FI Engine
# File: logging_setup.py
# -----------------------------------------------------------------------------
# Setup logging infrastructure for FI campaigns.
#=============================================================================

from dataclasses import dataclass
from fi import fi_settings
from fi.log import events


@dataclass
class LogContext:
    """
    Simple container for logging context.
    
    Holds the resolved log file path for reference by other components.
    
    Attributes:
        log_file_path: Full path to the log file being written
    """
    log_file_path: str


def setup_logging(cfg) -> LogContext:
    """
    Setup logging infrastructure for a campaign.
    
    This function:
    1. Resolves the log directory path (CLI override or settings default)
    2. Sets up the log file via events.setup_log_file()
    3. Logs initial startup information
    4. Returns a LogContext for reference
    
    Args:
        cfg: Config object with logging parameters
    
    Returns:
        LogContext with resolved log file path
    """
    # Use CLI override if provided, otherwise use setting default
    log_root = getattr(cfg, 'log_root_override', None) or fi_settings.LOG_ROOT
    log_filename = fi_settings.LOG_FILENAME
    
    # Setup log file (creates directory, opens file, writes header)
    events.setup_log_file(log_root, log_filename)
    
    # Log startup information
    events.log_startup(cfg)
    
    # Return context with file path
    return LogContext(
        log_file_path=f"{log_root}/{log_filename}"
    )