# =============================================================================
# FATORI-V • Results • Results Packager
# File: results_packager.py
# -----------------------------------------------------------------------------
# Packages complete results with all outputs, reports, and metrics.
# =============================================================================

import shutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Optional
import fatori_settings as cfg
from scripts.results.excel_exporter import export_to_excel
from scripts.results.csv_exporter import export_all_csvs
from scripts.results.summary_generator import generate_run_summary
from scripts.results.results_validator import validate_results
from scripts.build.path_resolver import resolve_reports_dir
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import *
from scripts.logging import logger


def get_run_name(config):
    """
    Get run name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with run name
    """
    run_ident = get_nested(config, KEY_RUN, KEY_RUN_IDENTIFICATION, default={})
    name = run_ident.get(KEY_IDENT_NAME, 'unnamed_run')
    
    # Sanitize name for filesystem
    safe_name = name.replace(' ', '_').replace('/', '_')
    
    return safe_name


def create_results_directory(config, base_dir=None):
    """
    Create results directory for this run.
    
    Args:
        config: The loaded YAML configuration dictionary
        base_dir: Optional base directory (defaults to cfg.RESULTS_DIR)
    
    Returns:
        Path to created results directory
    """
    if base_dir is None:
        base_dir = cfg.RESULTS_DIR
    
    base_dir = Path(base_dir)
    
    # Get run name
    run_name = get_run_name(config)
    
    # Add timestamp to ensure uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"{run_name}_{timestamp}"
    
    results_dir = base_dir / dir_name
    results_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log_event('DEBUG', debug_message=f"Created results directory: {results_dir}")
    
    return results_dir


def copy_session_results(sessions, results_dir):
    """
    Copy session directories to results package.
    
    Args:
        sessions: List of Session objects
        results_dir: Path to results directory
    
    Returns:
        Path to sessions directory
    """
    sessions_dest = results_dir / "sessions"
    sessions_dest.mkdir(parents=True, exist_ok=True)
    
    logger.log_event('DEBUG', debug_message=f"Copying {len(sessions)} session directories...")
    
    for session in sessions:
        if not session.session_dir or not session.session_dir.exists():
            logger.log_event('WARNING', warning_message=f"Session {session.session_id} directory not found")
            continue
        
        # Copy session directory
        dest = sessions_dest / session.session_dir.name
        
        try:
            if dest.exists():
                shutil.rmtree(dest)
            
            shutil.copytree(session.session_dir, dest)
            logger.log_event('DEBUG', debug_message=f"Copied session {session.session_id}")
        
        except Exception as e:
            logger.log_event('ERROR', error_message=f"Error copying session {session.session_id}: {e}")
    
    return sessions_dest


def copy_vivado_reports(results_dir):
    """
    Copy Vivado reports to results package.
    
    Args:
        results_dir: Path to results directory
    
    Returns:
        Path to reports directory or None
    """
    # Find source reports directory
    # Find source reports directory
    source_reports = resolve_reports_dir()
    
    if not source_reports.exists():
        logger.log_event('WARNING', warning_message=f"Vivado reports not found: {source_reports}")
        return None
    
    # Copy to results
    reports_dest = results_dir / "reports"
    
    try:
        if reports_dest.exists():
            shutil.rmtree(reports_dest)
        
        shutil.copytree(source_reports, reports_dest)
        logger.log_event('DEBUG', debug_message=f"Copied Vivado reports to {reports_dest}")
        
        return reports_dest
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error copying Vivado reports: {e}")
        return None


def copy_config(config_path, results_dir):
    """
    Copy configuration file to results package.
    
    Args:
        config_path: Path to configuration file
        results_dir: Path to results directory
    
    Returns:
        Path to copied config file
    """
    if not config_path or not Path(config_path).exists():
        logger.log_event('WARNING', warning_message="Configuration file not found")
        return None
    
    config_path = Path(config_path)
    dest = results_dir / "verified_config.yaml"
    
    try:
        shutil.copy2(config_path, dest)
        logger.log_event('DEBUG', debug_message=f"Copied configuration to {dest}")
        return dest
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error copying configuration: {e}")
        return None


def create_manifest(results_dir, config, metrics_aggregator):
    """
    Create manifest file with results metadata.
    
    Args:
        results_dir: Path to results directory
        config: The loaded YAML configuration dictionary
        metrics_aggregator: MetricsAggregator instance
    
    Returns:
        Path to manifest file
    """
    manifest_path = results_dir / "manifest.json"
    
    # Build manifest data
    manifest = {
        'created': datetime.now().isoformat(),
        'run_name': get_run_name(config),
        'fatori_version': '1.0',  # TODO: Get from version file
        'session_count': metrics_aggregator.get_session_count(),
        'files': {
            'summary': 'run_summary.txt',
            'excel': 'metrics.xlsx',
            'csv_summary': 'metrics_summary.csv',
            'csv_sessions': 'sessions.csv',
            'csv_build': 'build_metrics.csv',
            'config': 'verified_config.yaml',
            'sessions_dir': 'sessions/',
            'reports_dir': 'reports/',
        }
    }
    
    # Add aggregate statistics
    aggregates = metrics_aggregator.compute_aggregates()
    manifest['statistics'] = {
        'total_sessions': aggregates.get('session_count', 0),
        'successful_sessions': aggregates.get('success', {}).get('successful', 0),
        'fi_enabled_sessions': aggregates.get('fi_enabled_count', 0),
    }
    
    try:
        with manifest_path.open('w') as f:
            json.dump(manifest, f, indent=2)
        
        logger.log_event('DEBUG', debug_message=f"Created manifest: {manifest_path}")
        return manifest_path
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error creating manifest: {e}")
        return None


def package_results(config, metrics_aggregator, sessions=None, config_path=None, base_dir=None):
    """
    Package complete results with all outputs.
    
    This creates a comprehensive results package including:
    - Excel workbook with multiple sheets
    - CSV files for easy parsing
    - Text summary report
    - Session directories with logs
    - Vivado reports
    - Configuration file
    - Manifest with metadata
    
    Args:
        config: The loaded YAML configuration dictionary
        metrics_aggregator: MetricsAggregator instance with collected metrics
        sessions: Optional list of Session objects (for copying session dirs)
        config_path: Optional path to configuration file
        base_dir: Optional base directory for results (defaults to cfg.RESULTS_DIR)
    
    Returns:
        Path to results directory
    """
    logger.log_event('RESULTS_START')
    
    # Create results directory
    results_dir = create_results_directory(config, base_dir)
    
    logger.log_event('DEBUG', debug_message=f"Results will be packaged to: {results_dir}")
    
    # Generate text summary
    logger.log_event('DEBUG', debug_message="Generating run summary...")
    summary_text = generate_run_summary(config, metrics_aggregator)
    summary_path = results_dir / "run_summary.txt"
    with summary_path.open('w', encoding='utf-8') as f:
        f.write(summary_text)
    logger.log_event('RESULTS_FILE_CREATED', file_path=str(summary_path.name))
    
    # Generate Excel workbook
    logger.log_event('DEBUG', debug_message="Generating Excel workbook...")
    excel_path = results_dir / "metrics.xlsx"
    if export_to_excel(metrics_aggregator, excel_path, config):
        logger.log_event('RESULTS_FILE_CREATED', file_path=str(excel_path.name))
    else:
        logger.log_event('WARNING', warning_message="Excel export failed or unavailable")
    
    # Generate CSV files
    logger.log_event('DEBUG', debug_message="Generating CSV files...")
    csv_results = export_all_csvs(metrics_aggregator, results_dir)
    for csv_type, csv_path in csv_results.items():
        logger.log_event('RESULTS_FILE_CREATED', file_path=str(csv_path.name))
    
    # Copy session directories
    if sessions:
        logger.log_event('DEBUG', debug_message="Copying session directories...")
        copy_session_results(sessions, results_dir)
        logger.log_event('DEBUG', debug_message="Session directories copied")
    
    # Copy Vivado reports
    logger.log_event('DEBUG', debug_message="Copying Vivado reports...")
    if copy_vivado_reports(results_dir):
        logger.log_event('DEBUG', debug_message="Vivado reports copied")
    else:
        logger.log_event('WARNING', warning_message="Vivado reports not copied")
    
    # Copy configuration
    if config_path:
        logger.log_event('DEBUG', debug_message="Copying configuration...")
        if copy_config(config_path, results_dir):
            logger.log_event('DEBUG', debug_message="Configuration copied")
    
    # Create manifest
    logger.log_event('DEBUG', debug_message="Creating manifest...")
    if create_manifest(results_dir, config, metrics_aggregator):
        logger.log_event('DEBUG', debug_message="Manifest created")
    
    # Validate results package
    logger.log_event('DEBUG', debug_message="Validating results package...")
    is_valid, errors, warnings = validate_results(results_dir)
    
    if is_valid:
        logger.log_event('DEBUG', debug_message="Results package validated successfully")
    else:
        logger.log_event('ERROR', error_message="Results package validation failed:")
        for error in errors:
            logger.log_event('ERROR', error_message=f"  - {error}")
    
    if warnings:
        logger.log_event('WARNING', warning_message="Validation warnings:")
        for warning in warnings:
            logger.log_event('WARNING', warning_message=f"  - {warning}")
    
    file_count = len([f for f in results_dir.rglob('*') if f.is_file()])
    logger.log_event('RESULTS_END', file_count=file_count)
    
    return results_dir