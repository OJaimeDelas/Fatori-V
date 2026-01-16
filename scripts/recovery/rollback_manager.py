# =============================================================================
# FATORI-V • Rollback Manager
# File: rollback_manager.py
# -----------------------------------------------------------------------------
# Manages rollback points for reverting to earlier phases.
# =============================================================================

import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
from scripts.orchestration.run_context import RunContext
from scripts.recovery.state_persistence import save_run_state
import fatori_settings as cfg
from scripts.logging.logger import log_event


def get_rollback_dir(context: RunContext) -> Path:
    """
    Get rollback directory for this run.
    
    Args:
        context: Run context
    
    Returns:
        Path to rollback directory
    """
    return context.results_dir / "rollback"


def create_rollback_point(context: RunContext, phase_name: str) -> bool:
    """
    Create a rollback point before executing a phase.
    
    Saves:
    - Current run state
    - Current configuration
    - Backup of critical files
    
    Args:
        context: Run context
        phase_name: Phase about to be executed
    
    Returns:
        Boolean indicating success
    """
    log_event('ROLLBACK_POINT_CREATE', phase=phase_name)
    
    rollback_dir = get_rollback_dir(context)
    rollback_dir.mkdir(parents=True, exist_ok=True)
    
    # Create phase-specific rollback directory
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    phase_rollback = rollback_dir / f"{phase_name}_{timestamp}"
    phase_rollback.mkdir(exist_ok=True)
    
    try:
        # Save run state
        state_path = phase_rollback / "run_state.json"
        save_run_state(context, state_path)
        
        # Save phase info
        info_path = phase_rollback / "rollback_info.txt"
        with info_path.open('w') as f:
            f.write(f"Rollback Point\n")
            f.write(f"Created: {datetime.now().isoformat()}\n")
            f.write(f"Phase: {phase_name}\n")
            f.write(f"Completed phases: {', '.join(context.run_state.completed_phases)}\n")
        
        log_event('ROLLBACK_POINT_CREATED',
                  phase=phase_name,
                  path=str(phase_rollback))
        return True
    
    except Exception as e:
        log_event('ROLLBACK_POINT_CREATE_ERROR',
                  phase=phase_name,
                  error_message=str(e))
        return False


def list_rollback_points(context: RunContext) -> list:
    """
    List available rollback points.
    
    Args:
        context: Run context
    
    Returns:
        List of (phase_name, path) tuples
    """
    rollback_dir = get_rollback_dir(context)
    
    if not rollback_dir.exists():
        return []
    
    points = []
    
    for item in rollback_dir.iterdir():
        if item.is_dir():
            # Extract phase name from directory name
            parts = item.name.rsplit('_', 2)
            if len(parts) >= 1:
                phase_name = parts[0]
                points.append((phase_name, item))
    
    return sorted(points, key=lambda x: x[1].name)


def rollback_to_phase(phase_name: str, context: RunContext) -> bool:
    """
    Rollback to a specific phase.
    
    This restores the run state from before the phase was executed.
    
    Args:
        phase_name: Phase to rollback to
        context: Run context
    
    Returns:
        Boolean indicating success
    """
    log_event('ROLLBACK_START', phase=phase_name)
    
    # Find rollback point
    rollback_points = list_rollback_points(context)
    
    matching_points = [p for p in rollback_points if p[0] == phase_name]
    
    if not matching_points:
        log_event('ROLLBACK_POINT_NOT_FOUND', phase=phase_name)
        return False
    
    # Use most recent rollback point
    _, rollback_path = matching_points[-1]
    
    try:
        # Load saved state
        state_path = rollback_path / "run_state.json"
        
        if not state_path.exists():
            log_event('ROLLBACK_STATE_FILE_NOT_FOUND',
                      state_path=str(state_path))
            return False
        
        from scripts.recovery.state_persistence import load_run_state
        
        restored_context = load_run_state(state_path)
        
        if not restored_context:
            log_event('ROLLBACK_STATE_LOAD_FAILED')
            return False
        
        # Restore run state
        context.run_state = restored_context.run_state
        context.config = restored_context.config
        
        log_event('ROLLBACK_SUCCESS',
                  phase=phase_name,
                  completed_phases=context.run_state.completed_phases)
        
        return True
    
    except Exception as e:
        log_event('ROLLBACK_ERROR',
                  phase=phase_name,
                  error_message=str(e))
        return False


def cleanup_rollback_points(context: RunContext, keep_latest: int = 3) -> int:
    """
    Clean up old rollback points to save space.
    
    Args:
        context: Run context
        keep_latest: Number of latest rollback points to keep
    
    Returns:
        Number of rollback points removed
    """
    rollback_dir = get_rollback_dir(context)
    
    if not rollback_dir.exists():
        return 0
    
    # Get all rollback points sorted by time (oldest first)
    points = sorted(rollback_dir.iterdir(), key=lambda p: p.stat().st_mtime)
    
    # Determine how many to remove
    remove_count = max(0, len(points) - keep_latest)
    
    if remove_count == 0:
        return 0
    
    log_event('ROLLBACK_CLEANUP_START', remove_count=remove_count)
    
    removed = 0
    for point in points[:remove_count]:
        try:
            shutil.rmtree(point)
            removed += 1
        except Exception as e:
            log_event('ROLLBACK_CLEANUP_ERROR',
                      point=str(point),
                      error_message=str(e))
    
    log_event('ROLLBACK_CLEANUP_COMPLETE', removed_count=removed)
    
    return removed