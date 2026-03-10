# =============================================================================
# FATORI-V • Logging • Event Logger
# File: logger.py
# -----------------------------------------------------------------------------
# Central event dispatch system with dual log file support.
# =============================================================================

import sys
from pathlib import Path
from datetime import datetime
from typing import Optional

# Import configuration
from config.log_levels import LOG_LEVELS, DEFAULT_LOG_LEVEL
from config.messages_formats import FORMAT_FUNCTIONS


class EventLogger:
    """
    Centralized event-based logger with dual log file support.
    
    Maintains two log files:
    - General log: Entire FATORI-V execution (all runs)
    - Run log: Individual run (started/stopped per run)
    
    Routes all log/print operations through event system with
    configurable message formats and per-level controls.
    """
    
    def __init__(self, log_level: str = DEFAULT_LOG_LEVEL, 
                 general_log_file: Optional[Path] = None,
                 run_log_file: Optional[Path] = None):
        """
        Initialize event logger.
        
        Args:
            log_level: Log level name ('minimal', 'normal', 'verbose')
            general_log_file: Path to general log file (entire execution)
            run_log_file: Optional path to run-specific log file
        """
        self.log_level = log_level.lower()
        self.general_log_file = general_log_file
        self.run_log_file = run_log_file
        
        self.general_handle = None
        self.run_handle = None
        
        # Get event configuration for this level
        if self.log_level not in LOG_LEVELS:
            print(f"WARNING: Unknown log level '{log_level}', using 'normal'")
            self.log_level = 'normal'
        
        self.events = LOG_LEVELS[self.log_level]
        
        # Open general log file if specified
        if self.general_log_file:
            self._open_general_log()
        
        # Open run log file if specified
        if self.run_log_file:
            self._open_run_log()
    
    def _open_general_log(self):
        """Open general log file for writing."""
        try:
            self.general_log_file = Path(self.general_log_file)
            self.general_log_file.parent.mkdir(parents=True, exist_ok=True)
            # Reset general log on each fatori-v.py invocation (write mode, not append)
            self.general_handle = self.general_log_file.open('w', encoding='utf-8')
        except Exception as e:
            print(f"WARNING: Could not open general log file {self.general_log_file}: {e}")
            self.general_handle = None
    
    def _open_run_log(self):
        """Open run-specific log file for writing."""
        try:
            self.run_log_file = Path(self.run_log_file)
            self.run_log_file.parent.mkdir(parents=True, exist_ok=True)
            self.run_handle = self.run_log_file.open('w', encoding='utf-8')
        except Exception as e:
            print(f"WARNING: Could not open run log file {self.run_log_file}: {e}")
            self.run_handle = None
    
    def _write_to_console(self, message: str):
        """Write message to console."""
        print(message)
        sys.stdout.flush()
    
    def _write_to_files(self, message: str):
        """Write message to both log files (if open)."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_line = f"[{timestamp}] {message}\n"
        
        # Write to general log (always active if opened)
        if self.general_handle:
            try:
                self.general_handle.write(log_line)
                self.general_handle.flush()
            except Exception as e:
                print(f"WARNING: Error writing to general log file: {e}")
        
        # Write to run log (only when run is active)
        if self.run_handle:
            try:
                self.run_handle.write(log_line)
                self.run_handle.flush()
            except Exception as e:
                print(f"WARNING: Error writing to run log file: {e}")
    
    def start_run_log(self, run_log_file: Path):
        """
        Start run-specific logging.
        
        Opens a new log file for a specific run. All subsequent events
        will be written to both general log and run log.
        
        Args:
            run_log_file: Path to run-specific log file
        """
        # Close existing run log if open
        if self.run_handle:
            self.close_run_log()
        
        # Open new run log
        self.run_log_file = run_log_file
        self._open_run_log()
    
    def close_run_log(self):
        """Close run-specific log file."""
        if self.run_handle:
            try:
                self.run_handle.close()
            except Exception as e:
                print(f"WARNING: Error closing run log file: {e}")
            finally:
                self.run_handle = None
                self.run_log_file = None
    
    def log_event(self, event_name: str, **kwargs):
        """
        Log an event with given name and arguments.
        
        Args:
            event_name: Name of event (must be in FORMAT_FUNCTIONS)
            **kwargs: Keyword arguments passed to format function
        """
        # Check if event is enabled at this log level
        if event_name not in self.events:
            return
        
        event_config = self.events[event_name]
        
        # Check if event should be shown at all
        if not event_config['console'] and not event_config['file']:
            return
        
        # Get format function
        if event_name not in FORMAT_FUNCTIONS:
            # Fallback for unknown events
            message = f"{event_name}: {kwargs}"
        else:
            format_func = FORMAT_FUNCTIONS[event_name]
            try:
                message = format_func(**kwargs)
            except TypeError as e:
                # Format function signature doesn't match kwargs
                print(f"WARNING: Event '{event_name}' format error: {e}")
                message = f"{event_name}: {kwargs}"
        
        # Output to console if enabled
        if event_config['console']:
            self._write_to_console(message)
        
        # Output to files if enabled
        if event_config['file']:
            self._write_to_files(message)
    
    def set_log_level(self, log_level: str):
        """
        Change log level dynamically.
        
        Args:
            log_level: New log level ('minimal', 'normal', 'verbose')
        """
        log_level = log_level.lower()
        if log_level not in LOG_LEVELS:
            print(f"WARNING: Unknown log level '{log_level}', keeping current level")
            return
        
        self.log_level = log_level
        self.events = LOG_LEVELS[self.log_level]
    
    def close(self):
        """Close all log files."""
        # Close general log
        if self.general_handle:
            try:
                self.general_handle.close()
            except Exception as e:
                print(f"WARNING: Error closing general log file: {e}")
            finally:
                self.general_handle = None
        
        # Close run log
        self.close_run_log()


# =============================================================================
# GLOBAL LOGGER INSTANCE
# =============================================================================

_global_logger: Optional[EventLogger] = None


def initialize_logger(log_level: str = DEFAULT_LOG_LEVEL,
                     general_log_file: Optional[Path] = None,
                     run_log_file: Optional[Path] = None) -> EventLogger:
    """
    Initialize global logger instance.
    
    Args:
        log_level: Log level name ('minimal', 'normal', 'verbose')
        general_log_file: Path to general log file
        run_log_file: Optional path to run-specific log file
    
    Returns:
        EventLogger instance
    """
    global _global_logger
    
    # Close existing logger if present
    if _global_logger is not None:
        _global_logger.close()
    
    # Create new logger
    _global_logger = EventLogger(
        log_level=log_level,
        general_log_file=general_log_file,
        run_log_file=run_log_file
    )
    
    return _global_logger


def get_logger() -> EventLogger:
    """
    Get global logger instance.
    
    Returns:
        EventLogger instance
    
    Raises:
        RuntimeError: If logger not initialized
    """
    global _global_logger
    
    if _global_logger is None:
        raise RuntimeError("Logger not initialized. Call initialize_logger() first.")
    
    return _global_logger


def log_event(event_name: str, **kwargs):
    """
    Log event using global logger.
    
    Convenience function that calls get_logger().log_event().
    
    Args:
        event_name: Name of event
        **kwargs: Arguments for format function
    """
    logger = get_logger()
    logger.log_event(event_name, **kwargs)


def start_run_log(run_log_file: Path):
    """
    Start run-specific logging.
    
    Convenience function that calls get_logger().start_run_log().
    
    Args:
        run_log_file: Path to run-specific log file
    """
    logger = get_logger()
    logger.start_run_log(run_log_file)


def close_run_log():
    """
    Close run-specific log.
    
    Convenience function that calls get_logger().close_run_log().
    """
    logger = get_logger()
    logger.close_run_log()


def set_log_level(log_level: str):
    """
    Change log level.
    
    Convenience function that calls get_logger().set_log_level().
    
    Args:
        log_level: New log level
    """
    logger = get_logger()
    logger.set_log_level(log_level)


def close_logger():
    """
    Close global logger.
    
    Closes all log files and resets global logger.
    """
    global _global_logger
    
    if _global_logger is not None:
        _global_logger.close()
        _global_logger = None