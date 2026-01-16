# =============================================================================
# FATORI-V • Run Context
# File: run_context.py
# -----------------------------------------------------------------------------
# Encapsulates all information about a run execution.
# =============================================================================

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Optional
from scripts.orchestration.run_state import RunState
from scripts.logging.logger import log_event
import fatori_settings as cfg


class RunContext:
    """
    Encapsulates all information about a run.
    
    This provides a central object that holds configuration,
    results directory, state tracking, and other run metadata.
    """
    
    def __init__(self, config: Dict, results_dir: Path, yaml_path: Optional[Path] = None):
        """
        Initialize run context.
        
        Args:
            config: Loaded configuration dictionary
            results_dir: Path to results directory
            yaml_path: Optional path to source YAML file
        """
        self.config = config
        self.results_dir = Path(results_dir)
        self.yaml_path = Path(yaml_path) if yaml_path else None
        
        # Create run state tracker
        self.run_state = RunState()
        
        # Timestamps
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        
        log_event('DEBUG_RUN_CONTEXT_CREATED', results_dir=str(self.results_dir))
    
    def elapsed_time(self) -> timedelta:
        """
        Get elapsed time since run started.
        
        Returns:
            Timedelta representing elapsed time
        """
        if self.end_time:
            return self.end_time - self.start_time
        else:
            return datetime.now() - self.start_time
    
    def elapsed_seconds(self) -> float:
        """
        Get elapsed time in seconds.
        
        Returns:
            Float with seconds elapsed
        """
        return self.elapsed_time().total_seconds()
    
    def get_phase_dir(self, phase_name: str) -> Path:
        """
        Get directory for phase-specific files.
        
        Args:
            phase_name: Name of the phase
        
        Returns:
            Path to phase directory
        """
        phase_dir = self.results_dir / "phases" / phase_name
        phase_dir.mkdir(parents=True, exist_ok=True)
        return phase_dir
    
    def get_state_file_path(self) -> Path:
        """
        Get path to state file for persistence.
        
        Returns:
            Path to run_state.json
        """
        return self.results_dir / "run_state.json"
    
    def save_state(self):
        """Save current run state to file."""
        state_path = self.get_state_file_path()
        self.run_state.save_state(state_path)
    
    def load_state(self):
        """Load run state from file if it exists."""
        state_path = self.get_state_file_path()
        if state_path.exists():
            self.run_state = RunState.load_state(state_path)
    
    def log_info(self, message: str):
        """
        Log an info message.
        
        Args:
            message: Message to log
        """
        log_event('INFO', message=message)
    
    def log_warning(self, message: str):
        """
        Log a warning message.
        
        Args:
            message: Message to log
        """
        log_event('WARNING', warning_message=message)
    
    def log_error(self, message: str):
        """
        Log an error message.
        
        Args:
            message: Message to log
        """
        log_event('ERROR', error_message=message)
    
    def mark_complete(self):
        """Mark the run as complete."""
        self.end_time = datetime.now()
        self.run_state.end_run()
        
        duration = self.elapsed_seconds()
        log_event('RUN_MARKED_COMPLETE', duration=duration)
    
    def get_summary(self) -> Dict:
        """
        Get summary dictionary of run context.
        
        Returns:
            Dictionary with run summary
        """
        return {
            'results_dir': str(self.results_dir),
            'yaml_path': str(self.yaml_path) if self.yaml_path else None,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'elapsed_seconds': self.elapsed_seconds(),
            'completed_phases': self.run_state.completed_phases,
            'failed_phases': self.run_state.failed_phases,
            'is_complete': self.run_state.is_complete(),
            'has_failures': self.run_state.has_failures(),
        }