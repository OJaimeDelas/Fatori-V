# =============================================================================
# FATORI-V • State Persistence
# File: state_persistence.py
# -----------------------------------------------------------------------------
# Saves and loads run state for resume capability.
# =============================================================================

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from scripts.orchestration.run_context import RunContext
import fatori_settings as cfg
from scripts.logging.logger import log_event


def serialize_run_state(context: RunContext) -> Dict:
    """
    Serialize run context to dictionary for persistence.
    
    Args:
        context: Run context to serialize
    
    Returns:
        Dictionary with serializable state
    """
    state = {
        'version': '1.0',
        'saved_at': datetime.now().isoformat(),
        'config': context.config,
        'results_dir': str(context.results_dir),
        'yaml_path': str(context.yaml_path) if context.yaml_path else None,
        'start_time': context.start_time.isoformat(),
        'end_time': context.end_time.isoformat() if context.end_time else None,
        'run_state': {
            'completed_phases': context.run_state.completed_phases,
            'failed_phases': context.run_state.failed_phases,
            'current_phase': context.run_state.current_phase,
        }
    }
    
    return state


def deserialize_run_state(state: Dict) -> Optional[RunContext]:
    """
    Deserialize run context from dictionary.
    
    Args:
        state: Serialized state dictionary
    
    Returns:
        Reconstructed RunContext or None if invalid
    """
    try:
        # Validate version
        if state.get('version') != '1.0':
            log_event('STATE_VERSION_UNSUPPORTED', version=state.get('version'))
            return None
        
        # Extract core data
        config = state['config']
        results_dir = Path(state['results_dir'])
        yaml_path = Path(state['yaml_path']) if state['yaml_path'] else None
        
        # Create context
        context = RunContext(config, results_dir, yaml_path)
        
        # Restore timestamps
        context.start_time = datetime.fromisoformat(state['start_time'])
        if state['end_time']:
            context.end_time = datetime.fromisoformat(state['end_time'])
        
        # Restore run state
        run_state_data = state['run_state']
        context.run_state.completed_phases = run_state_data['completed_phases']
        context.run_state.failed_phases = run_state_data['failed_phases']
        context.run_state.current_phase = run_state_data['current_phase']
        
        log_event('STATE_RESTORED', saved_at=state['saved_at'])
        
        return context
    
    except Exception as e:
        log_event('STATE_DESERIALIZE_ERROR', error_message=str(e))
        return None


def save_run_state(context: RunContext, state_path: Optional[Path] = None) -> bool:
    """
    Save run state to file.
    
    Args:
        context: Run context to save
        state_path: Optional path (defaults to results_dir/run_state.json)
    
    Returns:
        Boolean indicating success
    """
    if state_path is None:
        state_path = context.results_dir / "run_state.json"
    
    state_path = Path(state_path)
    state_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        # Serialize state
        state = serialize_run_state(context)
        
        # Write to file
        with state_path.open('w') as f:
            json.dump(state, f, indent=2)
        
        log_event('STATE_SAVED', state_path=str(state_path))
        return True
    
    except Exception as e:
        log_event('STATE_SAVE_ERROR', error_message=str(e))
        return False


def load_run_state(state_path: Path) -> Optional[RunContext]:
    """
    Load run state from file.
    
    Args:
        state_path: Path to state file
    
    Returns:
        Restored RunContext or None if load fails
    """
    state_path = Path(state_path)
    
    if not state_path.exists():
        log_event('STATE_FILE_NOT_FOUND', state_path=str(state_path))
        return None
    
    try:
        # Load state file
        with state_path.open('r') as f:
            state = json.load(f)
        
        # Deserialize
        context = deserialize_run_state(state)
        
        if context:
            log_event('STATE_LOADED', state_path=str(state_path))
        
        return context
    
    except Exception as e:
        log_event('STATE_LOAD_ERROR', error_message=str(e))
        return None


def is_resumable(state_path: Path) -> bool:
    """
    Check if a saved state is resumable.
    
    Args:
        state_path: Path to state file
    
    Returns:
        Boolean indicating if state can be resumed
    """
    if not state_path.exists():
        return False
    
    try:
        context = load_run_state(state_path)
        
        if not context:
            return False
        
        # Check if run is not already complete
        if context.run_state.is_complete():
            log_event('STATE_ALREADY_COMPLETE')
            return False
        
        # Check if run has failures
        if context.run_state.has_failures():
            log_event('STATE_HAS_FAILURES')
            # Still resumable, but with warnings
        
        return True
    
    except Exception as e:
        log_event('STATE_RESUMABLE_CHECK_ERROR', error_message=str(e))
        return False


def get_resume_point(state_path: Path) -> Optional[str]:
    """
    Get the phase from which to resume.
    
    Args:
        state_path: Path to state file
    
    Returns:
        Phase name to resume from, or None
    """
    context = load_run_state(state_path)
    
    if not context:
        return None
    
    # Get next phase to run
    next_phase = context.run_state.get_next_phase_to_run()
    
    return next_phase