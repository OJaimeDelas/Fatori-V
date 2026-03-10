# =============================================================================
# FATORI-V • Results • Directory Manager
# File: directory_manager.py
# -----------------------------------------------------------------------------
# Manages results directory structure creation and organization.
# =============================================================================

from pathlib import Path
from datetime import datetime
from typing import Optional
import fatori_settings as cfg
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import *
from scripts.logging.logger import log_event


def get_run_id(config):
    """
    Get run ID from configuration.
    
    Format: {run_name}_{timestamp}
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with run ID
    """
    # Get run name
    run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    name = run_ident.get(KEY_IDENT_NAME, 'unnamed_run')
    
    # Sanitize name for filesystem
    safe_name = name.replace(' ', '_').replace('/', '_').replace('\\', '_')
    
    # Add timestamp for uniqueness (format: ddMMYY_HHmm)
    timestamp = datetime.now().strftime('%d%m%y_%H%M')
    
    return f"{safe_name}_{timestamp}"


def create_run_directory(config, base_dir: Optional[Path] = None) -> Path:
    """
    Create main run directory.
    
    Structure:
    results/
    └── <run_id>/
    
    Args:
        config: The loaded YAML configuration dictionary
        base_dir: Optional base directory (defaults to cfg.RESULTS_DIR)
    
    Returns:
        Path to created run directory
    """
    if base_dir is None:
        base_dir = cfg.RESULTS_DIR
    
    base_dir = Path(base_dir)
    base_dir.mkdir(parents=True, exist_ok=True)
    
    # Get run ID
    run_id = get_run_id(config)
    
    # Create run directory
    run_dir = base_dir / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('RESULTS_RUN_DIR_CREATED', run_dir=str(run_dir))
    
    return run_dir


def create_reports_directory(run_dir: Path) -> Path:
    """
    Create reports subdirectory.
    
    Structure:
    <run_id>/
    └── reports/
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Path to reports directory
    """
    reports_dir = run_dir / 'reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created reports directory: {reports_dir}")
    
    return reports_dir


def create_gen_directory(run_dir: Path) -> Path:
    """
    Create gen subdirectory for generated files.
    
    Structure:
    <run_id>/
    └── gen/
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Path to gen directory
    """
    gen_dir = run_dir / 'gen'
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created gen directory: {gen_dir}")
    
    return gen_dir


def create_sessions_directory(run_dir: Path) -> Path:
    """
    Create sessions subdirectory.
    
    Structure:
    <run_id>/
    └── sessions/
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Path to sessions directory
    """
    sessions_dir = run_dir / 'sessions'
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created sessions directory: {sessions_dir}")
    
    return sessions_dir


def create_session_directory(run_dir: Path, bench_id: str) -> Path:
    """
    Create individual session directory.
    
    Structure:
    <run_id>/
    └── sessions/
        └── <bench_id>/
    
    Args:
        run_dir: Path to run directory
        bench_id: Benchmark identifier
    
    Returns:
        Path to session directory
    """
    sessions_dir = run_dir / 'sessions'
    session_dir = sessions_dir / bench_id
    session_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created session directory: {session_dir}")
    
    return session_dir


def create_session_gen_directory(session_dir: Path) -> Path:
    """
    Create gen subdirectory within session.
    
    Structure:
    sessions/<bench_id>/
    └── gen/
    
    Args:
        session_dir: Path to session directory
    
    Returns:
        Path to session gen directory
    """
    gen_dir = session_dir / 'gen'
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created session gen directory: {gen_dir}")
    
    return gen_dir


def create_session_fi_directory(session_dir: Path) -> Path:
    """
    Create fi subdirectory within session.
    
    Structure:
    sessions/<bench_id>/
    └── fi/
    
    Args:
        session_dir: Path to session directory
    
    Returns:
        Path to session FI directory
    """
    fi_dir = session_dir / 'fi'
    fi_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('DEBUG', debug_message=f"Created session FI directory: {fi_dir}")
    
    return fi_dir


def ensure_directory_exists(dir_path: Path) -> Path:
    """
    Ensure directory exists, creating it if necessary.
    
    Args:
        dir_path: Path to directory
    
    Returns:
        Path to directory (for chaining)
    """
    dir_path = Path(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def get_session_directory(run_dir: Path, bench_id: str) -> Path:
    """
    Get path to session directory (creates if doesn't exist).
    
    Args:
        run_dir: Path to run directory
        bench_id: Benchmark identifier
    
    Returns:
        Path to session directory
    """
    return create_session_directory(run_dir, bench_id)


def get_session_gen_directory(run_dir: Path, bench_id: str) -> Path:
    """
    Get path to session gen directory (creates if doesn't exist).
    
    Args:
        run_dir: Path to run directory
        bench_id: Benchmark identifier
    
    Returns:
        Path to session gen directory
    """
    session_dir = get_session_directory(run_dir, bench_id)
    return create_session_gen_directory(session_dir)


def get_session_fi_directory(run_dir: Path, bench_id: str) -> Path:
    """
    Get path to session FI directory (creates if doesn't exist).
    
    Args:
        run_dir: Path to run directory
        bench_id: Benchmark identifier
    
    Returns:
        Path to session FI directory
    """
    session_dir = get_session_directory(run_dir, bench_id)
    return create_session_fi_directory(session_dir)


def initialize_run_structure(config, base_dir: Optional[Path] = None) -> dict:
    """
    Initialize complete run directory structure.
    
    Creates:
    - Run directory
    - reports/ subdirectory
    - gen/ subdirectory
    - sessions/ subdirectory
    
    Args:
        config: The loaded YAML configuration dictionary
        base_dir: Optional base directory (defaults to cfg.RESULTS_DIR)
    
    Returns:
        Dictionary with paths to key directories
    """
    # Create main run directory
    run_dir = create_run_directory(config, base_dir)
    
    # Create subdirectories
    reports_dir = create_reports_directory(run_dir)
    gen_dir = create_gen_directory(run_dir)
    sessions_dir = create_sessions_directory(run_dir)
    
    log_event('RESULTS_STRUCTURE_INITIALIZED', run_dir=str(run_dir))
    
    return {
        'run_dir': run_dir,
        'reports_dir': reports_dir,
        'gen_dir': gen_dir,
        'sessions_dir': sessions_dir
    }