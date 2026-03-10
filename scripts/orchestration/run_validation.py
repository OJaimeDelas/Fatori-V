# =============================================================================
# FATORI-V • Run Validation Wrapper
# File: run_validation.py
# -----------------------------------------------------------------------------
# Wrapper for complete run configuration validation.
# =============================================================================

import yaml
from pathlib import Path
from typing import Dict, Tuple
from scripts.validation.run_validator import validate_run_config, print_validation_results
from scripts.validation.validation_settings import STRICT_MODE_DEFAULT
from scripts.logging.logger import log_event


def save_verified_config(config: Dict, output_path: Path):
    """
    Save verified configuration to YAML file.
    
    Args:
        config: Configuration dictionary
        output_path: Path where verified config should be saved
    
    Returns:
        Boolean indicating success
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with output_path.open('w') as f:
            yaml.dump(config, f, default_flow_style=False, sort_keys=False)
        
        log_event('CONFIG_SAVED', output_path=str(output_path))
        return True
    
    except Exception as e:
        log_event('ERROR_CONFIG_SAVE_FAILED', error_message=str(e))
        return False


def display_validation_summary(validation_result: Dict):
    """
    Display validation summary using event logger.
    
    Args:
        validation_result: Validation result dictionary
    """
    errors = validation_result.get('errors', [])
    warnings = validation_result.get('warnings', [])
    corrections = validation_result.get('corrections', [])
    
    log_event('VALIDATION_SUMMARY_START')
    
    if not errors and not warnings:
        log_event('VALIDATION_CONFIG_VALID')
    else:
        if errors:
            log_event('VALIDATION_ERROR_COUNT', error_count=len(errors))
            for i, error in enumerate(errors[:5], 1):
                log_event('VALIDATION_ERROR_ITEM', index=i, error_message=error)
            if len(errors) > 5:
                log_event('VALIDATION_ERROR_MORE', additional_count=len(errors) - 5)
        
        if warnings:
            log_event('VALIDATION_WARNING_COUNT', warning_count=len(warnings))
            for i, warning in enumerate(warnings[:5], 1):
                log_event('VALIDATION_WARNING_ITEM', index=i, warning_message=warning)
            if len(warnings) > 5:
                log_event('VALIDATION_WARNING_MORE', additional_count=len(warnings) - 5)
    
    if corrections:
        log_event('VALIDATION_CORRECTIONS_APPLIED', correction_count=len(corrections))
    
    log_event('VALIDATION_SUMMARY_END')


def validate_run(config: Dict, results_dir: Path, strict: bool = None) -> Tuple[bool, Dict]:
    """
    Perform complete validation of run configuration.
    
    This wraps the validation system and provides:
    - Validation execution
    - Result display
    - Verified config saving
    
    Args:
        config: Configuration dictionary to validate
        results_dir: Results directory where verified config will be saved
        strict: If True, warnings are treated as errors (None = use default)
    
    Returns:
        Tuple of (is_valid: bool, validation_result: dict)
    """
    log_event('VALIDATION_START_FULL')
    
    # Use default strict mode if not specified
    if strict is None:
        strict = STRICT_MODE_DEFAULT
    
    log_event('VALIDATION_STRICT_MODE', enabled=strict)
    
    # Run validation
    try:
        is_valid, validation_result = validate_run_config(config, strict=strict)
    except Exception as e:
        log_event('ERROR_VALIDATION_EXCEPTION', error_message=str(e))
        return False, {'errors': [str(e)], 'warnings': [], 'corrections': [], 'valid': False}
    
    # Display results
    display_validation_summary(validation_result)
    
    # Check if validation passed
    if not is_valid:
        log_event('ERROR_VALIDATION_FAILED_CANNOT_PROCEED')
    
    return is_valid, validation_result