# =============================================================================
# FATORI-V • Results • YAML Copier
# File: yaml_copier.py
# -----------------------------------------------------------------------------
# Copies original and verified YAML files to results directory.
# =============================================================================

import shutil
from pathlib import Path
from typing import Optional
from scripts.logging.logger import log_event


def copy_original_yaml(yaml_path: Path, run_dir: Path) -> bool:
    """
    Copy original YAML file to results directory.
    
    Args:
        yaml_path: Path to original YAML file
        run_dir: Path to run directory
    
    Returns:
        Boolean indicating if copy succeeded
    """
    if not yaml_path.exists():
        log_event('YAML_COPY_SOURCE_MISSING', source=str(yaml_path))
        return False
    
    try:
        # Destination: results/<run_id>/<original_name>.yaml
        dest_path = run_dir / yaml_path.name
        
        shutil.copy2(yaml_path, dest_path)
        
        log_event('YAML_ORIGINAL_COPIED',
                  source=str(yaml_path),
                  dest=str(dest_path))
        
        return True
    
    except Exception as e:
        log_event('YAML_COPY_FAILED',
                  source=str(yaml_path),
                  error_message=str(e))
        return False


def save_verified_yaml(config: dict, run_dir: Path) -> bool:
    """
    Save verified YAML configuration to results directory.
    
    This preserves the original YAML format including "on"/"off" strings
    instead of normalizing to true/false.
    
    Args:
        config: Configuration dictionary (after validation corrections)
        run_dir: Path to run directory
    
    Returns:
        Boolean indicating if save succeeded
    """
    try:
        import yaml
        
        # Destination: results/<run_id>/verified_yaml.yaml
        dest_path = run_dir / 'verified_yaml.yaml'
        
        # Create custom dumper with bool representers
        class PreservingDumper(yaml.SafeDumper):
            pass
        
        # Register custom representer for booleans to output "on"/"off"
        def represent_bool_as_string(dumper, data):
            return dumper.represent_str('on' if data else 'off')
        
        # Register the representer for bool type
        PreservingDumper.add_representer(bool, represent_bool_as_string)
        
        with dest_path.open('w', encoding='utf-8') as f:
            yaml.dump(config, f, 
                     default_flow_style=False, 
                     sort_keys=False,
                     Dumper=PreservingDumper,
                     allow_unicode=True)
        
        log_event('YAML_VERIFIED_SAVED', dest=str(dest_path))
        
        return True
    
    except Exception as e:
        log_event('YAML_SAVE_FAILED',
                  dest=str(run_dir / 'verified_yaml.yaml'),
                  error_message=str(e))
        return False


def copy_yaml_files_to_results(yaml_path: Path, config: dict, run_dir: Path) -> bool:
    """
    Copy both original and verified YAML files to results directory.
    
    Args:
        yaml_path: Path to original YAML file
        config: Configuration dictionary (after validation)
        run_dir: Path to run directory
    
    Returns:
        Boolean indicating if both copies succeeded
    """
    original_ok = copy_original_yaml(yaml_path, run_dir)
    verified_ok = save_verified_yaml(config, run_dir)
    
    return original_ok and verified_ok