# =============================================================================
# FATORI-V • Run Setup
# File: run_setup.py
# -----------------------------------------------------------------------------
# Sets up run environment including configuration loading and logging.
# =============================================================================

from pathlib import Path
from typing import Tuple, Dict
import fatori_settings as cfg
from scripts.common.yaml_io.load_run_yaml import load_run_yaml
from scripts.logging.logger import initialize_logger, log_event
from scripts.common.cli_style.banners import print_main_banner
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import *


def load_configuration(yaml_path: Path) -> Dict:
    """
    Load and parse configuration YAML file.
    
    Args:
        yaml_path: Path to YAML configuration file
    
    Returns:
        Configuration dictionary
    
    Raises:
        FileNotFoundError: If YAML file doesn't exist
        ValueError: If YAML is invalid
    """
    yaml_path = Path(yaml_path)
    
    if not yaml_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
    
    log_event('CONFIG_LOADING', yaml_path=str(yaml_path))
    
    try:
        config = load_run_yaml(yaml_path)
        log_event('CONFIG_LOADED_SUCCESS')
        return config
    except Exception as e:
        log_event('ERROR_CONFIG_LOAD', error_message=str(e))
        raise


def create_results_directory(config: Dict) -> Path:
    """
    Create results directory for this run.
    
    The directory name is based on run identification in config.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Path to created results directory
    """
    from datetime import datetime
    
    # Get run name from config
    run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    run_name = run_ident.get(KEY_IDENT_NAME, 'unnamed_run')
    
    # Sanitize name for filesystem
    safe_name = run_name.replace(' ', '_').replace('/', '_')
    
    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"{safe_name}_{timestamp}"
    
    # Create directory
    results_dir = cfg.RESULTS_DIR / dir_name
    results_dir.mkdir(parents=True, exist_ok=True)
    
    log_event('RESULTS_DIR_CREATED', results_dir=str(results_dir))
    
    # Create subdirectories
    subdirs = ['phases', 'sessions', 'logs']
    for subdir in subdirs:
        (results_dir / subdir).mkdir(exist_ok=True)
    
    return results_dir


def setup_run_logging(results_dir: Path, log_level: str = None):
    """
    Setup logging for the run.
    
    Args:
        results_dir: Results directory where log file will be written
        log_level: Log level (INFO, DEBUG, WARNING, ERROR)
    
    Returns:
        Configured logger
    """
    if log_level is None:
        log_level = cfg.LOG_LEVEL_DEFAULT
    
    # Log file path
    log_file = results_dir / "logs" / "run.log"
    
    # Setup logging using new event logger
    initialize_logger(
        log_level=log_level.lower(),  # New logger expects lowercase
        log_file=log_file
    )
    
    log_event('LOGGING_CONFIGURED')
    log_event('LOG_FILE_SET', log_file=str(log_file))
    
    return None  # New logger is global, no return value


def display_banner(config: Dict):
    """
    Display FATORI-V banner and run information.
    
    Args:
        config: Configuration dictionary
    """
    # Get run information
    run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    run_name = run_ident.get(KEY_IDENT_NAME, 'Unnamed Run')
    
    # Display banner
    print_main_banner([(run_name, "configuration")])


def validate_environment():
    """
    Validate that the environment is properly configured.
    
    Checks:
    - Required directories exist
    - Python version
    - Required tools available
    
    Returns:
        Boolean indicating if environment is valid
    """
    errors = []
    
    # Check required directories
    required_dirs = [
        cfg.INPUTS_DIR,
        cfg.BENCHMARKS_DIR,
    ]
    
    for dir_path in required_dirs:
        if not dir_path.exists():
            errors.append(f"Required directory not found: {dir_path}")
    
    # Check Python version
    import sys
    if sys.version_info < (3, 7):
        errors.append(f"Python 3.7+ required, found {sys.version}")
    
    if errors:
        for error in errors:
            log_event('ENV_VALIDATION_ERROR', error_message=error)
        return False
    
    log_event('ENV_VALIDATION_PASSED')
    return True


def setup_run(yaml_path: Path, log_level: str = None) -> Tuple[Dict, Path]:
    """
    Setup run environment with configuration and logging.
    
    This is the main entry point for run setup. It:
    1. Loads configuration
    2. Creates results directory
    3. Sets up logging
    4. Displays banner
    5. Validates environment
    
    Args:
        yaml_path: Path to configuration YAML file
        log_level: Optional log level override
    
    Returns:
        Tuple of (config dictionary, results directory path)
    
    Raises:
        ValueError: If setup fails
    """
    # Initial basic logging to console only
    initialize_logger(log_level=(log_level or cfg.LOG_LEVEL_DEFAULT).lower())
    
    # Load configuration
    try:
        config = load_configuration(yaml_path)
    except Exception as e:
        log_event('ERROR_CONFIG_LOAD_FAILED', error_message=str(e))
        raise ValueError(f"Configuration loading failed: {e}")
    
    # Create results directory
    try:
        results_dir = create_results_directory(config)
    except Exception as e:
        log_event('ERROR_RESULTS_DIR_FAILED', error_message=str(e))
        raise ValueError(f"Results directory creation failed: {e}")
    
    # Setup logging with file output
    setup_run_logging(results_dir, log_level)
    
    # Display banner
    display_banner(config)
    
    # Validate environment
    if not validate_environment():
        raise ValueError("Environment validation failed")
    
    log_event('RUN_SETUP_COMPLETE')
    
    return config, results_dir