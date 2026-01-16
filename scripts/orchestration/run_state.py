# =============================================================================
# FATORI-V • Run State Manager
# File: run_state.py
# -----------------------------------------------------------------------------
# Tracks execution progress through phases with state persistence.
# =============================================================================

import json
from datetime import datetime
from typing import Optional, List, Dict
from pathlib import Path
from scripts.orchestration.run_phases import PHASE_ORDER, RunPhase
from scripts.logging.logger import log_event


class RunState:
    """
    Tracks progress through run phases.
    
    This class maintains state about which phases have completed,
    which failed, and provides state persistence for resume support.
    """
    
    def __init__(self):
        """Initialize run state with no phases complete."""
        self.completed_phases: List[str] = []
        self.failed_phases: Dict[str, str] = {}  # phase -> error message
        self.phase_start_times: Dict[str, datetime] = {}
        self.phase_end_times: Dict[str, datetime] = {}
        self.current_phase: Optional[str] = None
        self.run_start_time: Optional[datetime] = None
        self.run_end_time: Optional[datetime] = None
    
    def start_run(self):
        """Mark the start of the entire run."""
        self.run_start_time = datetime.now()
        log_event('RUN_STATE_STARTED', start_time=str(self.run_start_time))
    
    def end_run(self):
        """Mark the end of the entire run."""
        self.run_end_time = datetime.now()
        
        if self.run_start_time:
            duration = (self.run_end_time - self.run_start_time).total_seconds()
            log_event('RUN_STATE_ENDED', end_time=str(self.run_end_time), duration=duration)
    
    def start_phase(self, phase_name: str):
        """
        Mark the start of a phase.
        
        Args:
            phase_name: Name of phase starting
        """
        self.current_phase = phase_name
        self.phase_start_times[phase_name] = datetime.now()
        log_event('PHASE_STATE_STARTED', phase_name=phase_name)
    
    def mark_phase_complete(self, phase_name: str):
        """
        Mark a phase as successfully completed.
        
        Args:
            phase_name: Name of phase that completed
        """
        if phase_name not in self.completed_phases:
            self.completed_phases.append(phase_name)
        
        self.phase_end_times[phase_name] = datetime.now()
        
        # Calculate duration
        if phase_name in self.phase_start_times:
            start = self.phase_start_times[phase_name]
            end = self.phase_end_times[phase_name]
            duration = (end - start).total_seconds()
            log_event('PHASE_STATE_COMPLETED', phase_name=phase_name, duration=duration)
        else:
            log_event('PHASE_STATE_COMPLETED', phase_name=phase_name)
    
    def mark_phase_failed(self, phase_name: str, error: str):
        """
        Mark a phase as failed.
        
        Args:
            phase_name: Name of phase that failed
            error: Error message describing the failure
        """
        self.failed_phases[phase_name] = error
        self.phase_end_times[phase_name] = datetime.now()
        
        log_event('PHASE_STATE_FAILED', phase_name=phase_name, error_message=error)
    
    def is_phase_complete(self, phase_name: str) -> bool:
        """
        Check if a phase has completed successfully.
        
        Args:
            phase_name: Phase to check
        
        Returns:
            Boolean indicating if phase completed
        """
        return phase_name in self.completed_phases
    
    def is_phase_failed(self, phase_name: str) -> bool:
        """
        Check if a phase has failed.
        
        Args:
            phase_name: Phase to check
        
        Returns:
            Boolean indicating if phase failed
        """
        return phase_name in self.failed_phases
    
    def get_current_phase(self) -> Optional[str]:
        """
        Get the currently executing phase.
        
        Returns:
            Phase name or None if no phase is running
        """
        return self.current_phase
    
    def get_next_phase_to_run(self) -> Optional[str]:
        """
        Get the next phase that should be executed.
        
        Returns:
            Phase name or None if all phases complete
        """
        for phase in PHASE_ORDER:
            if not self.is_phase_complete(phase) and not self.is_phase_failed(phase):
                return phase
        
        return None
    
    def is_complete(self) -> bool:
        """
        Check if all phases have completed successfully.
        
        Returns:
            Boolean indicating if run is complete
        """
        return len(self.completed_phases) == len(PHASE_ORDER)
    
    def has_failures(self) -> bool:
        """
        Check if any phases have failed.
        
        Returns:
            Boolean indicating if there are failures
        """
        return len(self.failed_phases) > 0
    
    def get_completion_percentage(self) -> float:
        """
        Get completion percentage (0.0 to 100.0).
        
        Returns:
            Percentage of phases completed
        """
        if len(PHASE_ORDER) == 0:
            return 100.0
        
        return (len(self.completed_phases) / len(PHASE_ORDER)) * 100.0
    
    def save_state(self, path: Path):
        """
        Save state to JSON file for resume support.
        
        Args:
            path: Path where state should be saved
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Build state dictionary
        state = {
            'completed_phases': self.completed_phases,
            'failed_phases': self.failed_phases,
            'current_phase': self.current_phase,
            'phase_start_times': {
                k: v.isoformat() for k, v in self.phase_start_times.items()
            },
            'phase_end_times': {
                k: v.isoformat() for k, v in self.phase_end_times.items()
            },
            'run_start_time': self.run_start_time.isoformat() if self.run_start_time else None,
            'run_end_time': self.run_end_time.isoformat() if self.run_end_time else None,
        }
        
        try:
            with path.open('w') as f:
                json.dump(state, f, indent=2)
            
            log_event('DEBUG_STATE_SAVED', path=str(path))
        except Exception as e:
            log_event('ERROR_STATE_SAVE_FAILED', error_message=str(e))
    
    @classmethod
    def load_state(cls, path: Path):
        """
        Load state from JSON file.
        
        Args:
            path: Path to state file
        
        Returns:
            RunState instance loaded from file
        """
        path = Path(path)
        
        if not path.exists():
            log_event('WARNING_STATE_FILE_NOT_FOUND', path=str(path))
            return cls()
        
        try:
            with path.open('r') as f:
                state = json.load(f)
            
            # Create instance
            run_state = cls()
            
            # Load data
            run_state.completed_phases = state.get('completed_phases', [])
            run_state.failed_phases = state.get('failed_phases', {})
            run_state.current_phase = state.get('current_phase')
            
            # Load timestamps
            for phase, iso_time in state.get('phase_start_times', {}).items():
                run_state.phase_start_times[phase] = datetime.fromisoformat(iso_time)
            
            for phase, iso_time in state.get('phase_end_times', {}).items():
                run_state.phase_end_times[phase] = datetime.fromisoformat(iso_time)
            
            if state.get('run_start_time'):
                run_state.run_start_time = datetime.fromisoformat(state['run_start_time'])
            
            if state.get('run_end_time'):
                run_state.run_end_time = datetime.fromisoformat(state['run_end_time'])
            
            log_event('STATE_LOADED', 
                      path=str(path),
                      completed_phases=len(run_state.completed_phases),
                      total_phases=len(PHASE_ORDER))
            
            return run_state
        
        except Exception as e:
            log_event('ERROR_STATE_LOAD_FAILED', error_message=str(e))
            return cls()