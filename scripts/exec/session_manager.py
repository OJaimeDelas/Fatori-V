# =============================================================================
# FATORI-V • Execution • Session Manager
# File: session_manager.py
# -----------------------------------------------------------------------------
# Manages execution sessions and their metadata throughout benchmark runs.
# =============================================================================

from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict
import json
import fatori_settings as cfg
from scripts.logging.logger import log_event


@dataclass
class Session:
    """
    Container for session execution information.
    
    A session represents a single execution of a benchmark, including
    all associated metadata, paths, and state information.
    """
    session_id: int                          # Unique session identifier
    benchmark_name: str                      # Name of benchmark being executed
    start_time: Optional[datetime] = None    # When execution started
    end_time: Optional[datetime] = None      # When execution completed
    status: str = "pending"                  # Status: pending, running, success, failed, timeout
    console_output_path: Optional[Path] = None   # Path to console output log
    metrics_path: Optional[Path] = None          # Path to metrics file
    fi_log_path: Optional[Path] = None           # Path to FI log (if FI enabled)
    session_dir: Optional[Path] = None           # Directory for all session files
    injection_enabled: bool = False              # Whether FI is enabled for this session
    timeout_s: int = 300                         # Execution timeout
    
    def __str__(self):
        """String representation for logging."""
        duration = ""
        if self.start_time and self.end_time:
            elapsed = (self.end_time - self.start_time).total_seconds()
            duration = f", {elapsed:.1f}s"
        
        return f"Session {self.session_id}: {self.benchmark_name} ({self.status}{duration})"
    
    def get_duration(self):
        """
        Get execution duration in seconds.
        
        Returns:
            Float with duration, or None if not complete
        """
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return None


class SessionManager:
    """
    Manages execution sessions across benchmark runs.
    
    This class handles:
    - Session ID generation
    - Session directory creation
    - Session metadata persistence
    - Result organization
    """
    
    def __init__(self, config, results_dir=None):
        """
        Initialize session manager.
        
        Args:
            config: The loaded YAML configuration dictionary
            results_dir: Base directory for results (defaults to cfg.RESULTS_DIR)
        """
        self.config = config
        self.results_dir = Path(results_dir) if results_dir else cfg.RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        # Track sessions
        self._next_session_id = 1
        self._sessions = {}  # Maps session_id -> Session object
        
        log_event('SESSION_MANAGER_INITIALIZED', results_dir=str(self.results_dir))
    
    def get_next_session_id(self):
        """
        Get the next available session ID.
        
        Session IDs are sequential integers starting from 1.
        
        Returns:
            Integer session ID
        """
        session_id = self._next_session_id
        self._next_session_id += 1
        return session_id
    
    def get_session_dir(self, session_id):
        """
        Get path to session results directory.
        
        Sessions are organized as: results/session_<id>/
        
        Args:
            session_id: Session ID number
        
        Returns:
            Path object to session directory
        """
        session_dir = self.results_dir / f"session_{session_id:04d}"
        return session_dir
    
    def create_session(self, benchmark_name, injection_enabled=False, timeout_s=300):
        """
        Create a new execution session.
        
        Uses bench_id-based directory structure:
        results/<run_id>/sessions/<bench_id>/
        
        This allocates a session ID, creates the session directory,
        and initializes session metadata.
        
        Args:
            benchmark_name: Name of benchmark to execute
            injection_enabled: Whether FI is enabled for this session
            timeout_s: Execution timeout in seconds
        
        Returns:
            Session object
        """
        from scripts.results.directory_manager import get_session_directory
        
        # Allocate session ID
        session_id = self.get_next_session_id()
        
        # Use benchmark name as bench_id
        bench_id = benchmark_name
        
        # Create session directory using new structure
        session_dir = get_session_directory(self.results_dir, bench_id)
        
        # Define file paths with proper naming
        console_output = session_dir / f"fatori_{bench_id}_log.txt"
        metrics_file = session_dir / "metrics.txt"
        fi_log = session_dir / "fi" / "injection_log.txt" if injection_enabled else None
        
        # Create session object
        session = Session(
            session_id=session_id,
            benchmark_name=benchmark_name,
            status="pending",
            console_output_path=console_output,
            metrics_path=metrics_file,
            fi_log_path=fi_log,
            session_dir=session_dir,
            injection_enabled=injection_enabled,
            timeout_s=timeout_s
        )
        
        # Register session
        self._sessions[session_id] = session
        
        log_event('SESSION_CREATED',
                  session_id=session_id,
                  benchmark_name=benchmark_name,
                  session_dir=str(session_dir))
        
        return session
    
    def start_session(self, session):
        """
        Mark session as started.
        
        Args:
            session: Session object
        """
        session.start_time = datetime.now()
        session.status = "running"
        
        log_event('SESSION_STARTED', session_id=session.session_id)
    
    def complete_session(self, session, status="success"):
        """
        Mark session as completed.
        
        Args:
            session: Session object
            status: Final status (success, failed, timeout)
        """
        session.end_time = datetime.now()
        session.status = status
        
        log_event('SESSION_COMPLETED',
                  session_id=session.session_id,
                  status=status)
    
    def save_session_info(self, session, info_dict=None):
        """
        Save session metadata to JSON file.
        
        This persists session information for later analysis.
        
        Args:
            session: Session object
            info_dict: Optional additional information dictionary
        
        Returns:
            Path to saved info file
        """
        # Build session info dictionary
        session_info = {
            'session_id': session.session_id,
            'benchmark_name': session.benchmark_name,
            'status': session.status,
            'injection_enabled': session.injection_enabled,
            'timeout_s': session.timeout_s,
            'start_time': session.start_time.isoformat() if session.start_time else None,
            'end_time': session.end_time.isoformat() if session.end_time else None,
            'duration_s': session.get_duration(),
            'console_output': str(session.console_output_path) if session.console_output_path else None,
            'metrics_file': str(session.metrics_path) if session.metrics_path else None,
            'fi_log': str(session.fi_log_path) if session.fi_log_path else None,
        }
        
        # Merge additional info
        if info_dict:
            session_info.update(info_dict)
        
        # Write to session directory
        info_path = session.session_dir / "session_info.json"
        
        try:
            with info_path.open('w') as f:
                json.dump(session_info, f, indent=2)
            
            log_event('SESSION_INFO_SAVED', info_path=str(info_path))
            return info_path
        except Exception as e:
            log_event('SESSION_INFO_SAVE_ERROR', error_message=str(e))
            return None
    
    def get_session(self, session_id):
        """
        Get session object by ID.
        
        Args:
            session_id: Session ID
        
        Returns:
            Session object, or None if not found
        """
        return self._sessions.get(session_id)
    
    def get_all_sessions(self):
        """
        Get list of all sessions.
        
        Returns:
            List of Session objects
        """
        return list(self._sessions.values())
    
    def get_sessions_by_status(self, status):
        """
        Get sessions with a specific status.
        
        Args:
            status: Status string to filter by
        
        Returns:
            List of Session objects
        """
        return [s for s in self._sessions.values() if s.status == status]