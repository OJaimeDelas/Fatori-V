# =============================================================================
# FATORI-V • Validation • User Validator
# File: user_validator.py
# -----------------------------------------------------------------------------
# Executes user-defined validation checks from config/validation_checks.py.
# =============================================================================

from scripts.common.common_settings import *
from scripts.validation.validation_settings import *
from scripts.logging.logger import log_event


def execute_user_validations(config):
    """
    Execute user-defined validation checks.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Validation result dictionary with errors, warnings, corrections applied
    """
    result = create_validation_result()
    
    try:
        # Import user validation checks
        from config.validation_checks import validation_sequence
        
        # Get check sequence
        checks = validation_sequence()
        
        log_event('USER_VALIDATION_START', check_count=len(checks))
        
        # Execute each check
        for idx, check in enumerate(checks):
            check_type = check.get('type', 'warning')
            logic = check.get('logic')
            message = check.get('message', 'Validation check failed')
            correction = check.get('correction')
            
            # Skip if logic function not provided
            if not callable(logic):
                log_event('USER_VALIDATION_INVALID_CHECK', check_index=idx)
                continue
            
            # Evaluate check logic
            try:
                triggered = logic(config)
            except Exception as e:
                log_event('USER_VALIDATION_CHECK_ERROR',
                          check_index=idx,
                          error_message=str(e))
                continue
            
            # If check triggered
            if triggered:
                # Get message (can be string or callable)
                msg = message(config) if callable(message) else message
                
                # Add to errors or warnings
                if check_type == 'error':
                    add_error(result, msg)
                    log_event('USER_VALIDATION_ERROR', message=msg)
                else:
                    add_warning(result, msg)
                    log_event('USER_VALIDATION_WARNING', message=msg)
                
                # Apply correction if provided
                if correction and callable(correction):
                    try:
                        correction(config)
                        add_correction(result, f"Applied correction: {msg}")
                        log_event('USER_VALIDATION_CORRECTION_APPLIED', message=msg)
                    except Exception as e:
                        log_event('USER_VALIDATION_CORRECTION_FAILED',
                                  message=msg,
                                  error_message=str(e))
        
        log_event('USER_VALIDATION_COMPLETE',
                  errors=len(result[KEY_ERRORS]),
                  warnings=len(result[KEY_WARNINGS]),
                  corrections=len(result[KEY_CORRECTIONS]))
        
        return result
    
    except ImportError:
        # validation_checks.py doesn't exist or has import errors
        log_event('USER_VALIDATION_NOT_AVAILABLE')
        return result
    
    except Exception as e:
        log_event('USER_VALIDATION_EXCEPTION', error_message=str(e))
        add_error(result, f"User validation system error: {e}")
        return result