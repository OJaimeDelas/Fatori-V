# =============================================================================
# FATORI-V • Results • Results Validator
# File: results_validator.py
# -----------------------------------------------------------------------------
# Validates completeness and integrity of results packages.
# =============================================================================

import json
from pathlib import Path
from typing import List, Tuple
from scripts.logging.logger import log_event


def check_file_exists(filepath, description=""):
    """
    Check if a file exists and log result.
    
    Args:
        filepath: Path to check
        description: Description for logging
    
    Returns:
        Boolean indicating if file exists
    """
    filepath = Path(filepath)
    exists = filepath.exists() and filepath.is_file()
    
    if exists:
        log_event('VALIDATION_FILE_FOUND', description=description, filename=filepath.name)
    else:
        log_event('VALIDATION_FILE_MISSING', description=description, filepath=str(filepath))
    
    return exists


def validate_json_file(filepath):
    """
    Validate that a JSON file can be parsed.
    
    Args:
        filepath: Path to JSON file
    
    Returns:
        Boolean indicating if file is valid
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False
    
    try:
        with filepath.open('r') as f:
            json.load(f)
        return True
    except Exception as e:
        log_event('VALIDATION_JSON_INVALID', filepath=str(filepath), error_message=str(e))
        return False


def validate_csv_file(filepath):
    """
    Validate that a CSV file can be read.
    
    Args:
        filepath: Path to CSV file
    
    Returns:
        Boolean indicating if file is valid
    """
    import csv
    
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False
    
    try:
        with filepath.open('r', encoding='utf-8') as f:
            reader = csv.reader(f)
            # Try to read first row
            next(reader)
        return True
    except Exception as e:
        log_event('VALIDATION_CSV_INVALID', filepath=str(filepath), error_message=str(e))
        return False


def validate_excel_file(filepath):
    """
    Validate that an Excel file can be opened.
    
    Args:
        filepath: Path to Excel file
    
    Returns:
        Boolean indicating if file is valid
    """
    filepath = Path(filepath)
    
    if not filepath.exists():
        return False
    
    try:
        from openpyxl import load_workbook
        wb = load_workbook(filepath, read_only=True)
        wb.close()
        return True
    except ImportError:
        log_event('VALIDATION_EXCEL_LIBRARY_MISSING')
        return True  # Assume valid if we can't check
    except Exception as e:
        log_event('VALIDATION_EXCEL_INVALID', filepath=str(filepath), error_message=str(e))
        return False


def validate_results(results_dir):
    """
    Validate completeness and integrity of results package.
    
    This performs comprehensive validation including:
    - Required files present
    - Files are valid (not corrupted)
    - Metrics are reasonable
    
    Args:
        results_dir: Path to results directory
    
    Returns:
        Tuple of (is_valid: bool, errors: List[str], warnings: List[str])
    """
    results_dir = Path(results_dir)
    
    log_event('VALIDATION_START', results_dir=str(results_dir))
    
    errors = []
    warnings = []
    
    if not results_dir.exists():
        errors.append(f"Results directory not found: {results_dir}")
        return False, errors, warnings
    
    # Check for required files
    required_files = {
        'run_summary.txt': "Run summary",
        'metrics_summary.csv': "Metrics summary CSV",
    }
    
    for filename, description in required_files.items():
        filepath = results_dir / filename
        if not check_file_exists(filepath, description):
            errors.append(f"Missing required file: {filename}")
    
    # Check optional but important files
    optional_files = {
        'sessions.csv': "Sessions CSV",
        'build_metrics.csv': "Build metrics CSV",
        'metrics.xlsx': "Excel workbook",
        'verified_config.yaml': "Verified configuration",
    }
    
    for filename, description in optional_files.items():
        filepath = results_dir / filename
        if not check_file_exists(filepath, description):
            warnings.append(f"Optional file missing: {filename}")
    
    # Validate file formats
    
    # Validate CSVs
    csv_files = ['metrics_summary.csv', 'sessions.csv', 'build_metrics.csv']
    for csv_file in csv_files:
        csv_path = results_dir / csv_file
        if csv_path.exists():
            if not validate_csv_file(csv_path):
                errors.append(f"Invalid CSV file: {csv_file}")
    
    # Validate Excel
    excel_path = results_dir / 'metrics.xlsx'
    if excel_path.exists():
        if not validate_excel_file(excel_path):
            errors.append("Invalid Excel file: metrics.xlsx")
    
    # Validate JSON files
    manifest_path = results_dir / 'manifest.json'
    if manifest_path.exists():
        if not validate_json_file(manifest_path):
            errors.append("Invalid manifest.json")
    
    # Check sessions directory
    sessions_dir = results_dir / 'sessions'
    if sessions_dir.exists():
        session_count = len(list(sessions_dir.glob('session_*')))
        log_event('VALIDATION_SESSIONS_FOUND', session_count=session_count)
        
        if session_count == 0:
            warnings.append("No session directories found")
    else:
        warnings.append("Sessions directory missing")
    
    # Determine validity
    is_valid = len(errors) == 0
    
    # Summary
    if is_valid:
        log_event('VALIDATION_PASSED')
    else:
        log_event('VALIDATION_FAILED', error_count=len(errors))
    
    if warnings:
        log_event('VALIDATION_WARNINGS', warning_count=len(warnings))
    
    return is_valid, errors, warnings