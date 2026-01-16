# =============================================================================
# FATORI-V • CLI Override Applicator
# File: override_applicator.py
# -----------------------------------------------------------------------------
# Applies command-line argument overrides to configuration.
# =============================================================================

from copy import deepcopy
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.common.common_settings import *
from scripts.logging.logger import log_event


def apply_log_level_override(config, log_level):
    """
    Apply log level override to configuration.
    
    Args:
        config: Configuration dictionary
        log_level: Log level string (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Modified configuration
    """
    # Store in results section for later use
    if KEY_RESULTS not in config:
        config[KEY_RESULTS] = {}
    
    config[KEY_RESULTS]['log_level'] = log_level
    
    log_event('OVERRIDE_LOG_LEVEL', log_level=log_level)
    
    return config


def apply_grab_timeout_override(config, grab_timeout):
    """
    Apply board grab timeout override.
    
    Args:
        config: Configuration dictionary
        grab_timeout: Timeout in seconds
    
    Returns:
        Modified configuration
    """
    # Set in run.execution section
    if KEY_RUN not in config:
        config[KEY_RUN] = {}
    if KEY_RUN_EXECUTION not in config[KEY_RUN]:
        config[KEY_RUN][KEY_RUN_EXECUTION] = {}
    
    config[KEY_RUN][KEY_RUN_EXECUTION]['grab_timeout'] = grab_timeout
    
    log_event('OVERRIDE_GRAB_TIMEOUT', grab_timeout_s=grab_timeout)
    
    return config


def apply_make_jobs_override(config, make_jobs):
    """
    Apply make jobs override.
    
    Args:
        config: Configuration dictionary
        make_jobs: Number of parallel jobs
    
    Returns:
        Modified configuration
    """
    # Set in run.hardware section
    if KEY_RUN not in config:
        config[KEY_RUN] = {}
    if KEY_RUN_HW not in config[KEY_RUN]:
        config[KEY_RUN][KEY_RUN_HW] = {}
    
    config[KEY_RUN][KEY_RUN_HW]['make_jobs'] = make_jobs
    
    log_event('OVERRIDE_MAKE_JOBS', make_jobs=make_jobs)
    
    return config


def apply_no_clean_override(config):
    """
    Apply no-clean override to skip clean step.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Modified configuration
    """
    # Set in run.hardware section
    if KEY_RUN not in config:
        config[KEY_RUN] = {}
    if KEY_RUN_HW not in config[KEY_RUN]:
        config[KEY_RUN][KEY_RUN_HW] = {}
    
    config[KEY_RUN][KEY_RUN_HW]['skip_clean'] = True
    
    log_event('OVERRIDE_SKIP_CLEAN', skip_clean=True)
    
    return config


def apply_no_fi_override(config):
    """
    Disable all fault injection in configuration.
    
    Args:
        config: Configuration dictionary
    
    Returns:
        Modified configuration
    """
    # Disable FI for all benchmarks
    benchmarks = get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, default={})
    
    for bench_name, bench_config in benchmarks.items():
        if isinstance(bench_config, dict):
            bench_config[KEY_BENCH_INJECTION] = False
    
    log_event('OVERRIDE_FI_DISABLED')
    
    return config


def apply_cli_overrides(config, cli_args):
    """
    Apply all CLI argument overrides to configuration.
    
    This creates a modified copy of the configuration with
    CLI overrides applied.
    
    Args:
        config: Original configuration dictionary
        cli_args: Parsed CLI arguments namespace
    
    Returns:
        Modified configuration dictionary
    """
    # Create deep copy to avoid modifying original
    modified_config = deepcopy(config)
    
    log_event('CLI_OVERRIDES_START')
    
    # Log level
    if cli_args.log_level:
        modified_config = apply_log_level_override(modified_config, cli_args.log_level)
    
    # Grab timeout
    if cli_args.grab_timeout:
        modified_config = apply_grab_timeout_override(modified_config, cli_args.grab_timeout)
    
    # Make jobs
    if cli_args.make_jobs:
        modified_config = apply_make_jobs_override(modified_config, cli_args.make_jobs)
    
    # No clean
    if cli_args.no_clean:
        modified_config = apply_no_clean_override(modified_config)
    
    # No FI
    if cli_args.no_fi:
        modified_config = apply_no_fi_override(modified_config)
    
    log_event('CLI_OVERRIDES_APPLIED')
    
    return modified_config