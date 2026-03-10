# =============================================================================
# FATORI-V • Execution • FI Command Builder
# File: fi_command_builder.py
# -----------------------------------------------------------------------------
# Builds fault injection console command from configuration.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.logging import logger


def get_fi_specifics(config):
    """
    Get fault injection specifics from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with FI specifics
    """
    return config.get('specifics', {}).get('fault_tolerance', {}).get('fault_injection', {})


def get_run_seed(config):
    """
    Get run seed from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Integer seed value
    """
    return config.get('run', {}).get('identification', {}).get('seed', 123456)


def get_fi_device(config):
    """
    Get FI device path from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with device path
    """
    return cfg.FI_DEVICE_DEFAULT


def get_fi_baudrate(config):
    """
    Get FI baudrate from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Integer with baudrate
    """
    return cfg.FI_BAUDRATE_DEFAULT


def get_fi_log_level(config):
    """
    Get FI log level from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with log level (minimal/normal/verbose)
    """
    results = config.get('general', {}).get('results', {})
    log_level = results.get('fi_log_level', 'normal')
    return log_level


def get_area_profile_name(config):
    """
    Get area profile name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with area profile name
    """
    general_fi = config.get('general', {}).get('fault_injection', {})
    return general_fi.get('area_profile', 'device')


def get_time_profile_name(config):
    """
    Get time profile name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with time profile name
    """
    general_fi = config.get('general', {}).get('fault_injection', {})
    return general_fi.get('time_profile', 'uniform')


def build_area_arguments(config, area_profile):
    """
    Build area-specific command line arguments.
    
    Constructs --area-args="key=value,key=value" format and special flags.
    
    Args:
        config: The loaded YAML configuration dictionary
        area_profile: Area profile name
    
    Returns:
        List of command line arguments for area configuration
    """
    fi_specifics = get_fi_specifics(config)
    area_config = fi_specifics.get('area', {})
    
    args = []
    area_args_dict = {}
    
    # Get common area arguments (under specifics.fault_tolerance.fault_injection.area)
    repeat = area_config.get('repeat', True)
    tpool_size = area_config.get('target_pool_size', 200)
    ratio = area_config.get('ratio', 0.5)
    strict = area_config.get('strict', False)
    seed = area_config.get('seed')
    
    # Add common arguments to area_args
    area_args_dict['repeat'] = 'true' if repeat else 'false'
    area_args_dict['tpool_size'] = str(tpool_size)
    area_args_dict['ratio'] = str(ratio)
    
    # Handle strict flag separately
    if strict:
        args.append('--ratio-strict')
    
    # Handle seed
    if seed is not None:
        args.extend(['--area-seed', str(seed)])
    else:
        # Use run seed
        run_seed = get_run_seed(config)
        args.extend(['--area-seed', str(run_seed)])
    
    # Get profile-specific arguments
    profile_config = area_config.get(area_profile, {})
    
    if area_profile == 'device':
        # Device profile
        mode = profile_config.get('mode', 'sequential')
        area_args_dict['mode'] = mode
    
    elif area_profile == 'modules':
        # Modules profile
        module_mode = profile_config.get('module_mode', 'weighted')
        target_mode = profile_config.get('target_mode', 'sequential')
        weights_str = profile_config.get('weights', '1-1-1')
        targets_dict = profile_config.get('targets', {})
        
        area_args_dict['module_mode'] = module_mode
        area_args_dict['target_mode'] = target_mode
        
        # Keep weights in dash-separated format (weights=1-1-1)
        area_args_dict['weights'] = weights_str
        
        # Get enabled targets - use is_enabled to handle "on"/"off" strings and booleans
        if isinstance(targets_dict, dict):
            from scripts.common.yaml_io.yaml_helpers import is_enabled
            enabled_targets = [name for name, value in targets_dict.items() if is_enabled(value)]
            if enabled_targets:
                targets_str = '+'.join(enabled_targets)
                area_args_dict['modules'] = targets_str
    
    elif area_profile == 'target_list':
        # Target list profile
        pool_file = profile_config.get('pool_file', '')
        if pool_file:
            area_args_dict['pool_file'] = pool_file
    
    # Build --area-args string with quotes
    if area_args_dict:
        area_args_str = ','.join(f"{k}={v}" for k, v in area_args_dict.items())
        args.extend(['--area-args', f'"{area_args_str}"'])
    
    return args


def build_time_arguments(config, time_profile):
    """
    Build time-specific command line arguments.
    
    Constructs --time-args="key=value,key=value" format and special flags.
    
    Args:
        config: The loaded YAML configuration dictionary
        time_profile: Time profile name
    
    Returns:
        List of command line arguments for time configuration
    """
    fi_specifics = get_fi_specifics(config)
    time_config = fi_specifics.get('time', {})
    
    args = []
    time_args_dict = {}
    
    # Handle seed
    seed = time_config.get('seed')
    if seed is not None:
        args.extend(['--time-seed', str(seed)])
    else:
        # Use run seed
        run_seed = get_run_seed(config)
        args.extend(['--time-seed', str(run_seed)])
    
    # Get profile-specific arguments
    profile_config = time_config.get(time_profile, {})
    
    if time_profile == 'uniform':
        # Uniform profile
        rate_hz = profile_config.get('rate_hz')
        period_s = profile_config.get('period_s')
        duration_s = profile_config.get('duration_s')
        
        if period_s is not None:
            time_args_dict['period_s'] = str(period_s)
        elif rate_hz is not None:
            time_args_dict['rate_hz'] = str(rate_hz)
        
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    elif time_profile == 'ramp':
        # Ramp profile
        start_rate_hz = profile_config.get('start_rate_hz')
        end_rate_hz = profile_config.get('end_rate_hz')
        duration_s = profile_config.get('duration_s')
        
        if start_rate_hz is not None:
            time_args_dict['start_rate_hz'] = str(start_rate_hz)
        if end_rate_hz is not None:
            time_args_dict['end_rate_hz'] = str(end_rate_hz)
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    elif time_profile == 'poisson':
        # Poisson profile
        rate_hz = profile_config.get('rate_hz')
        duration_s = profile_config.get('duration_s')
        
        if rate_hz is not None:
            time_args_dict['rate_hz'] = str(rate_hz)
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    elif time_profile == 'mmpp2':
        # MMPP2 profile
        low_hz = profile_config.get('low_hz')
        high_hz = profile_config.get('high_hz')
        p_low_to_high = profile_config.get('p_low_to_high')
        p_high_to_low = profile_config.get('p_high_to_low')
        start_state = profile_config.get('start_state')
        duration_s = profile_config.get('duration_s')
        
        if low_hz is not None:
            time_args_dict['low_hz'] = str(low_hz)
        if high_hz is not None:
            time_args_dict['high_hz'] = str(high_hz)
        if p_low_to_high is not None:
            time_args_dict['p_low_to_high'] = str(p_low_to_high)
        if p_high_to_low is not None:
            time_args_dict['p_high_to_low'] = str(p_high_to_low)
        if start_state is not None:
            time_args_dict['start_state'] = start_state
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    elif time_profile == 'trace':
        # Trace profile
        file_path = profile_config.get('file') or profile_config.get('path')
        mode = profile_config.get('mode')
        repeat = profile_config.get('repeat')
        duration_s = profile_config.get('duration_s')
        
        if file_path:
            time_args_dict['file'] = str(file_path)
        if mode:
            time_args_dict['mode'] = mode
        if repeat is not None:
            time_args_dict['repeat'] = str(repeat)
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    elif time_profile == 'microburst':
        # Microburst profile
        burst_rate_hz = profile_config.get('burst_rate_hz')
        idle_rate_hz = profile_config.get('idle_rate_hz')
        burst_duration_s = profile_config.get('burst_duration_s')
        idle_duration_s = profile_config.get('idle_duration_s')
        bursts = profile_config.get('bursts')
        duration_s = profile_config.get('duration_s')
        
        if burst_rate_hz is not None:
            time_args_dict['burst_rate_hz'] = str(burst_rate_hz)
        if idle_rate_hz is not None:
            time_args_dict['idle_rate_hz'] = str(idle_rate_hz)
        if burst_duration_s is not None:
            time_args_dict['burst_duration_s'] = str(burst_duration_s)
        if idle_duration_s is not None:
            time_args_dict['idle_duration_s'] = str(idle_duration_s)
        if bursts is not None:
            time_args_dict['bursts'] = str(bursts)
        if duration_s is not None:
            time_args_dict['duration_s'] = str(duration_s)
    
    # Build --time-args string with quotes
    if time_args_dict:
        time_args_str = ','.join(f"{k}={v}" for k, v in time_args_dict.items())
        args.extend(['--time-args', f'"{time_args_str}"'])
    
    return args


def build_fi_command(config, benchmark_name):
    """
    Build fault injection console command from configuration.
    
    Constructs the FI console command with all necessary parameters:
    - Device and communication settings
    - Area and time profiles
    - Seeds and debugging options
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark being executed
        output_log_path: Optional path where injection log should be written (deprecated, not used)
    
    Returns:
        String with complete FI command
    """
    logger.log_event('DEBUG', debug_message="Building FI command...")
    
    # Get basic FI parameters
    device = get_fi_device(config)
    baudrate = get_fi_baudrate(config)
    log_level = get_fi_log_level(config)
    
    # Get profiles
    area_profile = get_area_profile_name(config)
    time_profile = get_time_profile_name(config)
    
    logger.log_event('DEBUG', debug_message=f"  Device: {device}")
    logger.log_event('DEBUG', debug_message=f"  Baudrate: {baudrate}")
    logger.log_event('DEBUG', debug_message=f"  Area profile: {area_profile}")
    logger.log_event('DEBUG', debug_message=f"  Time profile: {time_profile}")
    
    # Build command as list with correct argument names
    cmd_parts = [
        'python3',
        'fi/fault_injection.py',
        '--dev', device,
        '--baud', str(baudrate),
        '--log-level', log_level,
        '--area', area_profile,
        '--time', time_profile,
    ]
    
    # Add global seed if specified
    run_seed = get_run_seed(config)
    if run_seed is not None:
        cmd_parts.extend(['--global-seed', str(run_seed)])
    
    # Add debug flag in dry-run mode to simulate hardware
    if cfg.DRY_RUN_MODE:
        cmd_parts.append('--debug')
        logger.log_event('DEBUG', debug_message="  Debug mode: enabled (dry-run)")
    
    # Add area-specific arguments
    area_args = build_area_arguments(config, area_profile)
    cmd_parts.extend(area_args)
    
    # Add time-specific arguments
    time_args = build_time_arguments(config, time_profile)
    cmd_parts.extend(time_args)
    
    # Add EBD file argument (essential configuration database)
    # Path is relative to ROOT_DIR where FI subprocess runs
    ebd_path = Path('iob_soc_V1.0') / 'hardware' / 'fpga' / 'iob_soc_iob_aes_ku040_db_g.ebd'
    cmd_parts.extend(['--ebd', str(ebd_path)])
    
    # Add system dict argument (merged system hierarchy)
    # Path is relative to ROOT_DIR where FI subprocess runs
    system_dict_path = Path('tmp') / 'generated' / 'system_dict_merged.yaml'
    cmd_parts.extend(['--system-dict', str(system_dict_path)])
    
    # Add sync file for benchmark coordination
    # Note: Firmware creates this sync file, not FATORI-V
    # FI subprocess runs from ROOT_DIR, so path is relative to ROOT_DIR
    from scripts.build.path_resolver import resolve_sync_file
    sync_path = resolve_sync_file()
    
    # Get path relative to ROOT_DIR (where FI subprocess executes)
    try:
        sync_path_for_fi = Path(sync_path).relative_to(cfg.ROOT_DIR)
    except ValueError:
        # If sync_path is not under ROOT_DIR, use absolute path as fallback
        sync_path_for_fi = Path(sync_path)
    
    cmd_parts.extend(['--wait-for-file', str(sync_path_for_fi)])
    
    # Convert to string
    cmd = ' '.join(cmd_parts)
    
    logger.log_event('DEBUG', debug_message=f"FI command: {cmd}")
    
    return cmd