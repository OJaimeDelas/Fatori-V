from scripts.common.common_settings import *
from scripts.validation.validation_settings import *
from scripts.validation.schema_validator import *
from scripts.logging.logger import log_event


def validate_run_config(config, strict=STRICT_MODE_DEFAULT):
    """
    Perform complete validation of a run configuration.
    
    This orchestrates all validation checks and aggregates results.
    All business logic validation is in validation_checks.py (user validations).
    
    Args:
        config: The loaded YAML configuration dictionary
        strict: If True, treat warnings as errors
    
    Returns:
        Tuple of (is_valid, validation_result)
        - is_valid: Boolean indicating if configuration passed validation
        - validation_result: Dictionary with detailed validation information
    """
    # Create combined result
    combined = create_validation_result()
    
    # Run structural validation checks only
    validators = [
        ("Schema", validate_schema),
        ("Field Types", validate_field_types),
        ("Value Ranges", validate_value_ranges),
    ]
    
    # Run user-defined validations (all business logic is here)
    from scripts.validation.user_validator import execute_user_validations
    user_result = execute_user_validations(config)
    combined[KEY_ERRORS].extend(user_result[KEY_ERRORS])
    combined[KEY_WARNINGS].extend(user_result[KEY_WARNINGS])
    combined[KEY_CORRECTIONS].extend(user_result[KEY_CORRECTIONS])
    if not user_result[KEY_VALID]:
        combined[KEY_VALID] = False
    
    # Continue with standard validators
    validators = validators  # Keep original list for loop below
    
    for validator_name, validator_func in validators:
        result = validator_func(config)
        
        # Merge errors
        combined[KEY_ERRORS].extend(result[KEY_ERRORS])
        
        # Merge warnings
        combined[KEY_WARNINGS].extend(result[KEY_WARNINGS])
        
        # Merge corrections
        combined[KEY_CORRECTIONS].extend(result[KEY_CORRECTIONS])
        
        # Update validity
        if not result[KEY_VALID]:
            combined[KEY_VALID] = False
    
    # In strict mode, warnings invalidate ONLY if no corrections were applied
    # Warnings with corrections are considered resolved
    if strict and combined[KEY_WARNINGS]:
        # If warnings exist but no corrections were applied, validation fails
        if not combined[KEY_CORRECTIONS]:
            combined[KEY_VALID] = False
    
    # Always fail if there are actual errors (regardless of strict mode)
    if combined[KEY_ERRORS]:
        combined[KEY_VALID] = False
    
    return combined[KEY_VALID], combined


def print_validation_results(validation_result):
    """
    Log validation results using centralized logging system.
    
    Args:
        validation_result: Dictionary from validate_run_config
    """
    errors = validation_result[KEY_ERRORS]
    warnings = validation_result[KEY_WARNINGS]
    corrections = validation_result[KEY_CORRECTIONS]
    
    # Log errors
    if errors:
        for error in errors:
            log_event('VALIDATION_ERROR', error_message=error)
    
    # Log warnings
    if warnings:
        for warning in warnings:
            log_event('VALIDATION_WARNING', warning_message=warning)
    
    # Log corrections
    if corrections:
        for correction in corrections:
            log_event('VALIDATION_AUTO_CORRECTION', correction_description=correction)
    
    # Log final status if no issues
    if not errors and not warnings:
        log_event('VALIDATION_COMPLETE_NO_ISSUES')