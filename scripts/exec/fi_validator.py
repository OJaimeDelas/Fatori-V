# =============================================================================
# FATORI-V • Execution • FI Validator
# File: fi_validator.py
# -----------------------------------------------------------------------------
# Validates fault injection configuration before execution.
# =============================================================================

from pathlib import Path
from typing import List, Tuple
import fatori_settings as cfg
from scripts.exec.fi_command_builder import (
    get_fi_specifics,
    get_area_profile_name,
    get_time_profile_name,
    get_fi_device
)
from scripts.logging.logger import log_event


def validate_area_profile(config):
    """
    Validate area profile configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Tuple of (errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    area_profile = get_area_profile_name(config)
    fi_specifics = get_fi_specifics(config)
    area_config = fi_specifics.get('area', {})
    
    # Valid area profiles
    valid_profiles = ['device', 'modules', 'address_list', 'target_list']
    
    if area_profile not in valid_profiles:
        errors.append(f"Invalid area profile '{area_profile}'. Valid: {valid_profiles}")
        return errors, warnings
    
    # Profile-specific validation
    if area_profile == 'modules':
        modules_cfg = area_config.get('modules', {})
        targets = modules_cfg.get('targets', [])
        
        if not targets:
            warnings.append("Modules profile specified but no targets configured")
    
    elif area_profile == 'address_list':
        addr_cfg = area_config.get('address_list', {})
        addr_file = addr_cfg.get('file') or addr_cfg.get('path')
        
        if not addr_file:
            errors.append("Address list profile requires 'file' or 'path' parameter")
        elif not Path(addr_file).exists():
            warnings.append(f"Address list file does not exist: {addr_file}")
    
    elif area_profile == 'target_list':
        target_cfg = area_config.get('target_list', {})
        targets = target_cfg.get('targets', [])
        
        if not targets:
            warnings.append("Target list profile specified but no targets configured")
    
    return errors, warnings


def validate_time_profile(config):
    """
    Validate time profile configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Tuple of (errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    time_profile = get_time_profile_name(config)
    fi_specifics = get_fi_specifics(config)
    time_config = fi_specifics.get('time', {})
    
    # Valid time profiles
    valid_profiles = ['uniform', 'poisson', 'microburst', 'mmpp2', 'ramp', 'trace']
    
    if time_profile not in valid_profiles:
        errors.append(f"Invalid time profile '{time_profile}'. Valid: {valid_profiles}")
        return errors, warnings
    
    # Profile-specific validation
    if time_profile == 'uniform':
        uniform_cfg = time_config.get('uniform', {})
        
        if 'duration' not in uniform_cfg:
            warnings.append("Uniform profile should specify 'duration' parameter")
    
    elif time_profile == 'poisson':
        poisson_cfg = time_config.get('poisson', {})
        
        if 'lambda' not in poisson_cfg:
            warnings.append("Poisson profile should specify 'lambda' parameter")
        
        if 'duration' not in poisson_cfg:
            warnings.append("Poisson profile should specify 'duration' parameter")
    
    elif time_profile == 'trace':
        trace_cfg = time_config.get('trace', {})
        trace_file = trace_cfg.get('file')
        
        if not trace_file:
            errors.append("Trace profile requires 'file' parameter")
        elif not Path(trace_file).exists():
            warnings.append(f"Trace file does not exist: {trace_file}")
    
    return errors, warnings


def validate_device_accessible(config):
    """
    Validate that FI device is accessible.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Tuple of (errors: List[str], warnings: List[str])
    """
    errors = []
    warnings = []
    
    device = get_fi_device(config)
    device_path = Path(device)
    
    # Check if device exists
    if not device_path.exists():
        warnings.append(f"FI device not found: {device} (may not be connected)")
    
    # Check if it's a character device (typical for serial ports)
    elif not device_path.is_char_device():
        warnings.append(f"FI device is not a character device: {device}")
    
    return errors, warnings


def validate_fi_config(config):
    """
    Perform comprehensive validation of FI configuration.
    
    This checks:
    - Valid area profile with required parameters
    - Valid time profile with required parameters
    - Device accessibility
    - Reasonable parameter values
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Tuple of (errors: List[str], warnings: List[str])
    """
    log_event('FI_CONFIG_VALIDATION_START')
    
    all_errors = []
    all_warnings = []
    
    # Validate area profile
    errors, warnings = validate_area_profile(config)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Validate time profile
    errors, warnings = validate_time_profile(config)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Validate device
    errors, warnings = validate_device_accessible(config)
    all_errors.extend(errors)
    all_warnings.extend(warnings)
    
    # Summary
    if all_errors:
        log_event('FI_CONFIG_VALIDATION_ERRORS',
                  error_count=len(all_errors),
                  errors=all_errors)
    
    if all_warnings:
        log_event('FI_CONFIG_VALIDATION_WARNINGS',
                  warning_count=len(all_warnings))
    
    if not all_errors and not all_warnings:
        log_event('FI_CONFIG_VALIDATION_PASSED')
    
    return all_errors, all_warnings