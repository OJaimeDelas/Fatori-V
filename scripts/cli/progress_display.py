# =============================================================================
# FATORI-V • Progress Display
# File: progress_display.py
# -----------------------------------------------------------------------------
# Progress tracking and display for run execution.
# =============================================================================

from datetime import datetime, timedelta
from typing import List, Optional
from scripts.logging.logger import log_event


class ProgressDisplay:
    """
    Displays progress for single or multiple runs.
    
    Shows:
    - Current run (N of M)
    - Current phase
    - Progress indicators
    - Timing information
    """
    
    def __init__(self, total_runs: int = 1):
        """
        Initialize progress display.
        
        Args:
            total_runs: Total number of runs to execute
        """
        self.total_runs = total_runs
        self.current_run = 0
        self.current_run_name: Optional[str] = None
        self.current_phase: Optional[str] = None
        self.run_start_time: Optional[datetime] = None
        self.phase_start_time: Optional[datetime] = None
        self.completed_runs = []
        self.failed_runs = []
    
    def start_run(self, run_name: str, run_number: int):
        """
        Mark the start of a run.
        
        Args:
            run_name: Name/identifier of the run
            run_number: Run number (1-indexed)
        """
        self.current_run = run_number
        self.current_run_name = run_name
        self.run_start_time = datetime.now()
        
        print()
        print("=" * 80)
        print(f"RUN {run_number} OF {self.total_runs}: {run_name}")
        print("=" * 80)
        print()
        
        log_event('PROGRESS_RUN_START',
                  run_number=run_number,
                  total_runs=self.total_runs,
                  run_name=run_name)
    
    def update_phase(self, phase_name: str):
        """
        Update current phase being executed.
        
        Args:
            phase_name: Name of the phase
        """
        self.current_phase = phase_name
        self.phase_start_time = datetime.now()
        
        print(f"  [{self.current_run}/{self.total_runs}] Phase: {phase_name}")
        
        log_event('PROGRESS_PHASE_UPDATE',
                  run_number=self.current_run,
                  phase=phase_name)
    
    def complete_run(self, run_name: str, success: bool, duration: float):
        """
        Mark a run as complete.
        
        Args:
            run_name: Name of the run
            success: Whether run succeeded
            duration: Run duration in seconds
        """
        if success:
            self.completed_runs.append((run_name, duration))
            status = "✓ SUCCESS"
        else:
            self.failed_runs.append((run_name, duration))
            status = "✗ FAILED"
        
        print()
        print(f"{status} - {run_name} ({self._format_duration(duration)})")
        print()
        
        log_event('PROGRESS_RUN_COMPLETE',
                  run_name=run_name,
                  success=success,
                  duration_s=duration)
    
    def display_summary(self):
        """
        Display summary of all runs.
        """
        print()
        print("=" * 80)
        print("EXECUTION SUMMARY")
        print("=" * 80)
        print(f"Total runs: {self.total_runs}")
        print(f"Successful: {len(self.completed_runs)}")
        print(f"Failed: {len(self.failed_runs)}")
        print()
        
        if self.completed_runs:
            print("Successful runs:")
            for run_name, duration in self.completed_runs:
                print(f"  ✓ {run_name} ({self._format_duration(duration)})")
            print()
        
        if self.failed_runs:
            print("Failed runs:")
            for run_name, duration in self.failed_runs:
                print(f"  ✗ {run_name} ({self._format_duration(duration)})")
            print()
        
        # Total time
        total_time = sum(d for _, d in self.completed_runs + self.failed_runs)
        print(f"Total execution time: {self._format_duration(total_time)}")
        print("=" * 80)
        print()
        
        log_event('PROGRESS_SUMMARY',
                  total_runs=self.total_runs,
                  successful=len(self.completed_runs),
                  failed=len(self.failed_runs),
                  total_time_s=total_time)
    
    def _format_duration(self, seconds: float) -> str:
        """
        Format duration as human-readable string.
        
        Args:
            seconds: Duration in seconds
        
        Returns:
            Formatted string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def get_eta(self) -> Optional[str]:
        """
        Estimate time remaining.
        
        Returns:
            ETA string or None if cannot estimate
        """
        if not self.completed_runs:
            return None
        
        # Average time per completed run
        avg_time = sum(d for _, d in self.completed_runs) / len(self.completed_runs)
        
        # Remaining runs
        remaining = self.total_runs - len(self.completed_runs) - len(self.failed_runs)
        
        if remaining <= 0:
            return None
        
        # Estimate remaining time
        eta_seconds = avg_time * remaining
        
        return self._format_duration(eta_seconds)