# =============================================================================
# FATORI-V • Execution • FI Command Builder
# File: fi_command_builder.py
# -----------------------------------------------------------------------------
# Builds fault injection console commands from YAML configuration.
# =============================================================================

from typing import Dict, Any, List
import fatori_settings as cfg
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_nested
from scripts.logging import logger


def get_fi_specifics(config):
    """
    Extract fault_injection specifics from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with FI specifics
    """
    fi_specifics = get_nested(config, KEY_SPECIFICS, KEY_SPEC_FI, default={})
    return fi_specifics if isinstance(fi_specifics, dict) else {}


def get_area_profile_name(config):
    """
    Get area profile name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with area profile name (device, modules, address_list, target_list)
    """
    fi_specifics = get_fi_specifics(config)
    area_config = fi_specifics.get('area', {})
    
    # Profile can be specified directly or inferred from presence of sub-keys
    profile = area_config.get('profile', 'device')
    
    return str(profile).lower()


def get_time_profile_name(config):
    """
    Get time profile name from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with time profile name (uniform, poisson, microburst, etc.)
    """
    fi_specifics = get_fi_specifics(config)
    time_config = fi_specifics.get('time', {})
    
    # Profile can be specified directly
    profile = time_config.get('profile', 'uniform')
    
    return str(profile).lower()


def build_area_arguments(config, area_profile):
    """
    Build area-specific command line arguments.
    
    Args:
        config: The loaded YAML configuration dictionary
        area_profile: Area profile name
    
    Returns:
        List of command line arguments for area configuration
    """
    fi_specifics = get_fi_specifics(config)
    area_config = fi_specifics.get('area', {})
    
    args = []
    
    if area_profile == 'device':
        # Device profile - entire device, no additional args needed
        # Just need mode if specified
        device_cfg = area_config.get('device', {})
        mode = device_cfg.get('mode', 'sequential')
        args.extend(['--area-mode', mode])
    
    elif area_profile == 'modules':
        # Modules profile - specific module targets
        modules_cfg = area_config.get('modules', {})
        
        # Get targets list
        targets = modules_cfg.get('targets', [])
        if isinstance(targets, dict):
            # Format: {module_name: enabled}
            targets = [name for name, enabled in targets.items() if enabled]
        
        if targets:
            targets_str = ','.join(str(t) for t in targets)
            args.extend(['--area-targets', targets_str])
        
        # Get mode
        mode = modules_cfg.get('mode', 'sequential')
        args.extend(['--area-mode', mode])
    
    elif area_profile == 'address_list':
        # Address list profile - specific addresses from file
        addr_cfg = area_config.get('address_list', {})
        
        # Get address list file path
        addr_file = addr_cfg.get('file') or addr_cfg.get('path')
        if addr_file:
            args.extend(['--area-addresses', str(addr_file)])
        
        # Get mode
        mode = addr_cfg.get('mode', 'sequential')
        args.extend(['--area-mode', mode])
    
    elif area_profile == 'target_list':
        # Target list profile - similar to modules but different semantics
        target_cfg = area_config.get('target_list', {})
        
        # Get targets
        targets = target_cfg.get('targets', [])
        if isinstance(targets, dict):
            targets = [name for name, enabled in targets.items() if enabled]
        
        if targets:
            targets_str = ','.join(str(t) for t in targets)
            args.extend(['--area-targets', targets_str])
        
        # Get mode
        mode = target_cfg.get('mode', 'sequential')
        args.extend(['--area-mode', mode])
    
    return args


def build_time_arguments(config, time_profile):
    """
    Build time-specific command line arguments.
    
    Args:
        config: The loaded YAML configuration dictionary
        time_profile: Time profile name
    
    Returns:
        List of command line arguments for time configuration
    """
    fi_specifics = get_fi_specifics(config)
    time_config = fi_specifics.get('time', {})
    
    args = []
    
    if time_profile == 'uniform':
        # Uniform time distribution
        uniform_cfg = time_config.get('uniform', {})
        
        # Start time (when to begin injections)
        if 'start' in uniform_cfg:
            args.extend(['--time-start', str(uniform_cfg['start'])])
        
        # Duration (how long to inject)
        if 'duration' in uniform_cfg:
            args.extend(['--time-duration', str(uniform_cfg['duration'])])
        
        # Period (time between injections)
        if 'period' in uniform_cfg:
            args.extend(['--time-period', str(uniform_cfg['period'])])
    
    elif time_profile == 'poisson':
        # Poisson process time distribution
        poisson_cfg = time_config.get('poisson', {})
        
        # Lambda (rate parameter)
        if 'lambda' in poisson_cfg:
            args.extend(['--time-lambda', str(poisson_cfg['lambda'])])
        
        # Duration
        if 'duration' in poisson_cfg:
            args.extend(['--time-duration', str(poisson_cfg['duration'])])
    
    elif time_profile == 'microburst':
        # Microburst time distribution
        burst_cfg = time_config.get('microburst', {})
        
        # Burst count
        if 'count' in burst_cfg:
            args.extend(['--time-burst-count', str(burst_cfg['count'])])
        
        # Burst duration
        if 'duration' in burst_cfg:
            args.extend(['--time-burst-duration', str(burst_cfg['duration'])])
        
        # Inter-burst delay
        if 'delay' in burst_cfg:
            args.extend(['--time-burst-delay', str(burst_cfg['delay'])])
    
    elif time_profile == 'mmpp2':
        # MMPP2 (2-state Markov modulated Poisson process)
        mmpp2_cfg = time_config.get('mmpp2', {})
        
        # Parameters as comma-separated string
        if 'params' in mmpp2_cfg:
            params = mmpp2_cfg['params']
            if isinstance(params, (list, tuple)):
                params_str = ','.join(str(p) for p in params)
            else:
                params_str = str(params)
            args.extend(['--time-mmpp2-params', params_str])
    
    elif time_profile == 'ramp':
        # Ramp profile (linearly increasing rate)
        ramp_cfg = time_config.get('ramp', {})
        
        # Start rate
        if 'start' in ramp_cfg:
            args.extend(['--time-ramp-start', str(ramp_cfg['start'])])
        
        # End rate
        if 'end' in ramp_cfg:
            args.extend(['--time-ramp-end', str(ramp_cfg['end'])])
        
        # Duration
        if 'duration' in ramp_cfg:
            args.extend(['--time-ramp-duration', str(ramp_cfg['duration'])])
    
    elif time_profile == 'trace':
        # Trace-based profile (from file)
        trace_cfg = time_config.get('trace', {})
        
        # Trace file path
        if 'file' in trace_cfg:
            args.extend(['--time-trace-file', str(trace_cfg['file'])])
    
    return args


def get_sem_clock_hz(config):
    """
    Get SEM clock frequency from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Integer with SEM clock frequency in Hz
    """
    fi_specifics = get_fi_specifics(config)
    
    # Check if sem_clk_hz is specified in config
    sem_clk = fi_specifics.get('sem_clk_hz')
    
    if sem_clk is not None:
        return int(sem_clk)
    
    # Fall back to default
    return cfg.FI_SEM_CLK_HZ


def get_fi_device(config):
    """
    Get FI device path from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with device path (e.g., /dev/ttyUSB1)
    """
    fi_specifics = get_fi_specifics(config)
    
    # Check if device is specified
    device = fi_specifics.get('device')
    
    if device is not None:
        return str(device)
    
    # Fall back to default
    return cfg.FI_DEVICE_DEFAULT


def get_fi_baudrate(config):
    """
    Get FI serial baudrate from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Integer with baudrate
    """
    fi_specifics = get_fi_specifics(config)
    
    # Check if baudrate is specified
    baudrate = fi_specifics.get('baudrate')
    
    if baudrate is not None:
        return int(baudrate)
    
    # Fall back to default
    return cfg.FI_BAUDRATE_DEFAULT


def get_fi_log_level(config):
    """
    Get FI log level from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String with log level (debug, info, warning, error)
    """
    # Check results section for FI log level
    results_config = get_nested(config, KEY_GENERAL, KEY_GEN_RESULTS, default={})
    log_level = results_config.get('fi_log_level')
    
    if log_level:
        return str(log_level).lower()
    
    # Fall back to default
    return cfg.FI_LOG_LEVEL_DEFAULT


def build_fi_command(config, benchmark_name, output_log_path=None):
    """
    Build complete FI console command from configuration.
    
    This constructs the full command line for launching the external
    FI console with all parameters derived from YAML configuration.
    
    Command structure:
    python3 fi/fi_console.py \\
      --device /dev/ttyUSB1 \\
      --baudrate 1250000 \\
      --sem-clk 50000000 \\
      --log-level info \\
      --area-profile modules \\
      --area-targets alu,controller,decoder \\
      --time-profile uniform \\
      --time-start 0 \\
      --time-duration 1000000 \\
      --output injection_log.txt
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of benchmark being executed (for logging)
        output_log_path: Path where injection log should be written
    
    Returns:
        String with complete command
    """
    logger.log_event('DEBUG', debug_message="Building FI command...")
    
    # Get basic FI parameters
    device = get_fi_device(config)
    baudrate = get_fi_baudrate(config)
    sem_clk = get_sem_clock_hz(config)
    log_level = get_fi_log_level(config)
    
    # Get profiles
    area_profile = get_area_profile_name(config)
    time_profile = get_time_profile_name(config)
    
    logger.log_event('DEBUG', debug_message=f"  Device: {device}")
    logger.log_event('DEBUG', debug_message=f"  Baudrate: {baudrate}")
    logger.log_event('DEBUG', debug_message=f"  SEM clock: {sem_clk} Hz")
    logger.log_event('DEBUG', debug_message=f"  Area profile: {area_profile}")
    logger.log_event('DEBUG', debug_message=f"  Time profile: {time_profile}")
    
    # Build command as list
    cmd_parts = [
        'python3',
        'fi/fi_console.py',
        '--device', device,
        '--baudrate', str(baudrate),
        '--sem-clk', str(sem_clk),
        '--log-level', log_level,
        '--area-profile', area_profile,
        '--time-profile', time_profile,
    ]
    
    # Add area-specific arguments
    area_args = build_area_arguments(config, area_profile)
    cmd_parts.extend(area_args)
    
    # Add time-specific arguments
    time_args = build_time_arguments(config, time_profile)
    cmd_parts.extend(time_args)
    
    # Add output log path if specified
    if output_log_path:
        cmd_parts.extend(['--output', str(output_log_path)])
    
    # Convert to string
    cmd = ' '.join(cmd_parts)
    
    logger.log_event('DEBUG', debug_message=f"FI command: {cmd}")
    
    return cmd