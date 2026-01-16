# =============================================================================
# FATORI-V • Override System
# File: override_system.py
# -----------------------------------------------------------------------------
# Comprehensive override system for configuration values using dot notation.
# =============================================================================

import os
import yaml
from pathlib import Path
from copy import deepcopy
from typing import Dict, Any, List, Tuple
from scripts.logging import logger

def parse_dot_notation(path: str) -> List[str]:
    """
    Parse dot notation path into list of keys.
    
    Args:
        path: Dot notation path (e.g., "specifics.ibex.multiplier")
    
    Returns:
        List of keys
    """
    return path.split('.')


def get_value_by_path(config: Dict, path: str) -> Any:
    """
    Get value from config using dot notation path.
    
    Args:
        config: Configuration dictionary
        path: Dot notation path
    
    Returns:
        Value at path, or None if not found
    """
    keys = parse_dot_notation(path)
    current = config
    
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    
    return current


def set_value_by_path(config: Dict, path: str, value: Any) -> bool:
    """
    Set value in config using dot notation path.
    
    Creates intermediate dictionaries as needed.
    
    Args:
        config: Configuration dictionary (modified in place)
        path: Dot notation path
        value: Value to set
    
    Returns:
        Boolean indicating success
    """
    keys = parse_dot_notation(path)
    current = config
    
    # Navigate to parent of final key
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        elif not isinstance(current[key], dict):
            logger.log_event('WARNING', warning_message=f"Cannot set {path}: {key} is not a dictionary")
            return False
        current = current[key]
    
    # Set final value
    final_key = keys[-1]
    current[final_key] = value
    
    return True


def load_override_file(override_file: Path) -> Dict[str, Any]:
    """
    Load overrides from YAML file.
    
    Args:
        override_file: Path to override YAML file
    
    Returns:
        Dictionary mapping dot notation paths to values
    """
    override_file = Path(override_file)
    
    if not override_file.exists():
        logger.log_event('WARNING', warning_message=f"Override file not found: {override_file}")
        return {}
    
    try:
        with override_file.open('r') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return {}
        
        # Extract overrides section
        overrides = data.get('overrides', {})
        
        if not isinstance(overrides, dict):
            logger.log_event('WARNING', warning_message="Override file 'overrides' section must be a dictionary")
            return {}
        
        logger.log_event('DEBUG', debug_message=f"Loaded {len(overrides)} overrides from file")
        return overrides
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error loading override file: {e}")
        return {}


def load_environment_overrides(prefix: str = "FATORI_") -> Dict[str, Any]:
    """
    Load overrides from environment variables.
    
    Environment variables should be in format:
    FATORI_SPECIFICS_IBEX_MULTIPLIER=fast
    
    Converts to dot notation:
    specifics.ibex.multiplier: fast
    
    Args:
        prefix: Environment variable prefix to look for
    
    Returns:
        Dictionary mapping dot notation paths to values
    """
    overrides = {}
    
    for env_var, value in os.environ.items():
        if env_var.startswith(prefix):
            # Remove prefix and convert to dot notation
            path = env_var[len(prefix):].lower().replace('_', '.')
            
            # Try to parse value as YAML (handles booleans, numbers, etc.)
            try:
                parsed_value = yaml.safe_load(value)
            except:
                parsed_value = value
            
            overrides[path] = parsed_value
    
    if overrides:
        logger.log_event('DEBUG', debug_message=f"Loaded {len(overrides)} overrides from environment")
    
    return overrides


def apply_override_dict(config: Dict, overrides: Dict[str, Any]) -> int:
    """
    Apply dictionary of overrides to configuration.
    
    Args:
        config: Configuration dictionary (modified in place)
        overrides: Dictionary mapping dot notation paths to values
    
    Returns:
        Number of overrides successfully applied
    """
    applied_count = 0
    
    for path, value in overrides.items():
        if set_value_by_path(config, path, value):
            logger.log_event('DEBUG', debug_message=f"Override applied: {path} = {value}")
            applied_count += 1
        else:
            logger.log_event('WARNING', warning_message=f"Override failed: {path}")
    
    return applied_count


def apply_overrides(config: Dict, override_spec: Dict = None, 
                   override_file: Path = None, 
                   use_env: bool = True) -> Tuple[Dict, int]:
    """
    Apply overrides to configuration from multiple sources.
    
    Override precedence (lowest to highest):
    1. Environment variables
    2. Override file
    3. Override spec dictionary
    
    Args:
        config: Original configuration dictionary
        override_spec: Dictionary of overrides (dot notation paths)
        override_file: Path to override YAML file
        use_env: Whether to load environment overrides
    
    Returns:
        Tuple of (modified config, total overrides applied)
    """
    # Create deep copy to avoid modifying original
    modified_config = deepcopy(config)
    
    total_applied = 0
    
    logger.log_event('DEBUG', debug_message="Applying configuration overrides...")
    
    # 1. Environment variables (lowest precedence)
    if use_env:
        env_overrides = load_environment_overrides()
        if env_overrides:
            count = apply_override_dict(modified_config, env_overrides)
            total_applied += count
            logger.log_event('DEBUG', debug_message=f"Applied {count} environment overrides")
    
    # 2. Override file (medium precedence)
    if override_file:
        file_overrides = load_override_file(override_file)
        if file_overrides:
            count = apply_override_dict(modified_config, file_overrides)
            total_applied += count
            logger.log_event('DEBUG', debug_message=f"Applied {count} file overrides")
    
    # 3. Override spec (highest precedence)
    if override_spec:
        count = apply_override_dict(modified_config, override_spec)
        total_applied += count
        logger.log_event('DEBUG', debug_message=f"Applied {count} spec overrides")
    
    if total_applied > 0:
        logger.log_event('DEBUG', debug_message=f"Total overrides applied: {total_applied}")
    else:
        logger.log_event('DEBUG', debug_message="No overrides applied")
    
    return modified_config, total_applied


def create_override_file_template(output_path: Path):
    """
    Create a template override file with examples.
    
    Args:
        output_path: Path where template should be written
    """
    template = """# FATORI-V Override File Template
# Use dot notation to override any configuration value

overrides:
  # ISA Extensions
  # general.features.isa_extensions.RV32M: true
  # general.features.isa_extensions.RV32C: false
  
  # Ibex specifics
  # specifics.ibex.multiplier: "fast"
  # specifics.ibex.regfile: "latch"
  
  # Benchmarks
  # general.benchmarks.coremark.enable: true
  # general.benchmarks.coremark.fault_injection: false
  
  # Timeout
  # results.grab_timeout: 2000
  
  # Fault Manager
  # general.features.fault_manager: "off"
"""
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with output_path.open('w') as f:
        f.write(template)
    
    logger.log_event('DEBUG', debug_message=f"Created override template: {output_path}")