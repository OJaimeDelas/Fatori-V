# =============================================================================
# FATORI-V • Build System • Progress Tracker
# File: progress_tracker.py
# -----------------------------------------------------------------------------
# Tracks build progress through multiple steps.
# =============================================================================

import time
from enum import Enum
from scripts.logging.logger import log_event


class StepStatus(Enum):
    """Status of a build step."""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class BuildProgressTracker:
    """
    Tracks progress through build steps.
    
    This class maintains state for multi-step build processes,
    tracking which steps are complete, in progress, or failed.
    """
    
    def __init__(self, steps):
        """
        Initialize progress tracker with list of steps.
        
        Args:
            steps: List of step names (strings) in execution order
        """
        self.steps = steps
        self.step_status = {step: StepStatus.PENDING for step in steps}
        self.step_start_times = {}
        self.step_end_times = {}
        self.step_errors = {}
        self.current_step = None
    
    def start_step(self, step_name):
        """
        Mark a step as started.
        
        Args:
            step_name: Name of the step
        """
        if step_name not in self.steps:
            log_event('BUILD_STEP_UNKNOWN', step_name=step_name)
            return
        
        self.current_step = step_name
        self.step_status[step_name] = StepStatus.RUNNING
        self.step_start_times[step_name] = time.time()
        
        log_event('BUILD_STEP_START', step_name=step_name)
    
    def complete_step(self, step_name):
        """
        Mark a step as completed successfully.
        
        Args:
            step_name: Name of the step
        """
        if step_name not in self.steps:
            log_event('BUILD_STEP_UNKNOWN', step_name=step_name)
            return
        
        self.step_status[step_name] = StepStatus.COMPLETED
        self.step_end_times[step_name] = time.time()
        
        # Calculate elapsed time
        if step_name in self.step_start_times:
            elapsed = self.step_end_times[step_name] - self.step_start_times[step_name]
            log_event('BUILD_STEP_COMPLETE', step_name=step_name, elapsed_s=elapsed)
        else:
            log_event('BUILD_STEP_COMPLETE', step_name=step_name)
        
        self.current_step = None
    
    def fail_step(self, step_name, error):
        """
        Mark a step as failed.
        
        Args:
            step_name: Name of the step
            error: Error message or exception
        """
        if step_name not in self.steps:
            log_event('BUILD_STEP_UNKNOWN', step_name=step_name)
            return
        
        self.step_status[step_name] = StepStatus.FAILED
        self.step_end_times[step_name] = time.time()
        self.step_errors[step_name] = str(error)
        
        log_event('BUILD_STEP_FAILED', step_name=step_name, error_message=str(error))
        
        self.current_step = None
    
    def skip_step(self, step_name, reason=None):
        """
        Mark a step as skipped.
        
        Args:
            step_name: Name of the step
            reason: Optional reason for skipping
        """
        if step_name not in self.steps:
            log_event('BUILD_STEP_UNKNOWN', step_name=step_name)
            return
        
        self.step_status[step_name] = StepStatus.SKIPPED
        
        log_event('BUILD_STEP_SKIPPED', step_name=step_name, reason=reason or '')
    
    def get_progress(self):
        """
        Get overall progress as a fraction.
        
        Returns:
            Float between 0.0 and 1.0 representing progress
        """
        if not self.steps:
            return 1.0
        
        # Count completed and failed steps
        completed_count = sum(
            1 for status in self.step_status.values()
            if status in [StepStatus.COMPLETED, StepStatus.FAILED, StepStatus.SKIPPED]
        )
        
        return completed_count / len(self.steps)
    
    def get_status(self):
        """
        Get current status as a string.
        
        Returns:
            String describing current status
        """
        if self.current_step:
            return f"Running: {self.current_step}"
        
        progress = self.get_progress()
        
        if progress == 1.0:
            # All steps complete - check if any failed
            failed_steps = [
                step for step, status in self.step_status.items()
                if status == StepStatus.FAILED
            ]
            
            if failed_steps:
                return f"Failed at: {failed_steps[0]}"
            else:
                return "Completed"
        
        # In progress
        completed = sum(
            1 for status in self.step_status.values()
            if status == StepStatus.COMPLETED
        )
        return f"Progress: {completed}/{len(self.steps)} steps"
    
    def get_summary(self):
        """
        Get detailed summary of all steps.
        
        Returns:
            Dictionary with step details
        """
        summary = {
            'total_steps': len(self.steps),
            'completed': 0,
            'failed': 0,
            'pending': 0,
            'skipped': 0,
            'steps': {}
        }
        
        for step_name in self.steps:
            status = self.step_status[step_name]
            
            # Count by status
            if status == StepStatus.COMPLETED:
                summary['completed'] += 1
            elif status == StepStatus.FAILED:
                summary['failed'] += 1
            elif status == StepStatus.PENDING:
                summary['pending'] += 1
            elif status == StepStatus.SKIPPED:
                summary['skipped'] += 1
            
            # Step details
            step_info = {
                'status': status.value,
                'elapsed': None,
                'error': None
            }
            
            # Calculate elapsed time if available
            if step_name in self.step_start_times and step_name in self.step_end_times:
                step_info['elapsed'] = self.step_end_times[step_name] - self.step_start_times[step_name]
            
            # Add error if failed
            if step_name in self.step_errors:
                step_info['error'] = self.step_errors[step_name]
            
            summary['steps'][step_name] = step_info
        
        return summary