# =============================================================================
# FATORI-V • Build System • Make Command Builder
# File: make_commands.py
# -----------------------------------------------------------------------------
# Constructs make commands with proper flags and parameters.
# =============================================================================

import fatori_settings as cfg
from config.constants import BENCHMARK_DIR_RELATIVE_BASE
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import get_isa_extension_state
from scripts.mapping.board_mapping import get_make_board_name
from scripts.mapping.isa_mapping import get_isa_make_flags
from scripts.exec.requirements_parser import get_benchmark_flags
from scripts.build.path_resolver import (
    resolve_vivado_input,
    resolve_benchmark_dir,
)
from scripts.logging.logger import log_event


def get_board_from_config(config):
    """
    Extract board name from configuration and convert to make BOARD value.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String suitable for make BOARD= parameter
    """
    board_yaml = get_nested(config, KEY_RUN, KEY_RUN_HW, KEY_HW_BOARD, default=None)
    board_make = get_make_board_name(board_yaml)
    return board_make


def get_isa_flags_from_config(config):
    """
    Extract ISA-related make flags from configuration.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        List of make flag strings (e.g., ["USE_MUL_DIV=1", "USE_COMPRESSED=1"])
    """
    rv32m_enabled = get_isa_extension_state(config, KEY_ISA_RV32M)
    rv32c_enabled = get_isa_extension_state(config, KEY_ISA_RV32C)
    flags = get_isa_make_flags(rv32m_enabled, rv32c_enabled)
    return flags


def format_make_parameter(name, value):
    """
    Format a make parameter as NAME=value.
    
    Args:
        name: Parameter name
        value: Parameter value
    
    Returns:
        Formatted string "NAME=value"
    """
    if ' ' in str(value):
        return f'{name}="{value}"'
    else:
        return f'{name}={value}'


def build_fpga_run_command(config, benchmark_name, grab_timeout=None):
    """
    Build 'make fpga-run' command for complete build+run cycle.
    
    This target does everything: clean, setup, ibex-setup, build bitstream,
    build firmware, program FPGA, and run benchmark. Use this when building
    different hardware configurations or running single benchmarks.
    
    Command format:
    make fpga-run BOARD=<board> BENCHMARK_DIR=<path> GRAB_TIMEOUT=<t>
         VIVADO_INPUT=<path> [USE_MUL_DIV=1] [USE_COMPRESSED=1] [LLIB="..."]
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark to run
        grab_timeout: Timeout in seconds for UART grab (default: from config or 1000)
    
    Returns:
        String containing the make command
    """
    cmd_parts = ["make", cfg.MAKE_FPGA_RUN]
    
    # Add BOARD parameter
    board = get_board_from_config(config)
    cmd_parts.append(format_make_parameter("BOARD", board))
    
    # Add BENCHMARK_DIR parameter (relative path to benchmark)
    benchmark_dir = resolve_benchmark_dir(benchmark_name)
    cmd_parts.append(format_make_parameter("BENCHMARK_DIR", benchmark_dir))
    
    # Add GRAB_TIMEOUT parameter (always use default, not from config)
    # This is for board acquisition timeout, not benchmark execution timeout
    grab_timeout = cfg.BOARD_GRAB_TIMEOUT_DEFAULT
    cmd_parts.append(format_make_parameter("GRAB_TIMEOUT", grab_timeout))
    
    # Add VIVADO_INPUT parameter
    vivado_input = resolve_vivado_input()
    cmd_parts.append(format_make_parameter("VIVADO_INPUT", vivado_input))
    
    # Add ISA flags (USE_MUL_DIV, USE_COMPRESSED)
    isa_flags = get_isa_flags_from_config(config)
    cmd_parts.extend(isa_flags)
    
    # Add all custom flags from requirements.yaml
    custom_flags = get_benchmark_flags(benchmark_name)
    for flag_name, flag_value in custom_flags.items():
        cmd_parts.append(format_make_parameter(flag_name, flag_value))
    
    cmd = " ".join(cmd_parts)
    log_event('MAKE_CMD_BUILT',
              command_type='fpga_run',
              benchmark=benchmark_name,
              command=cmd)
    return cmd


def build_fpga_bit_only_command(config):
    """
    Build 'make fpga-bit-only' command for bitstream-only build.
    
    This target does: clean, setup, ibex-setup, and builds only the FPGA
    bitstream without firmware. Use this with fpga-fw-run when running
    multiple benchmarks on same hardware configuration.
    
    Command format:
    make fpga-bit-only BOARD=<board> VIVADO_INPUT=<path> 
         [USE_MUL_DIV=1] [USE_COMPRESSED=1]
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String containing the make command
    """
    cmd_parts = ["make", cfg.MAKE_FPGA_BIT_ONLY]
    
    # Add BOARD parameter
    board = get_board_from_config(config)
    cmd_parts.append(format_make_parameter("BOARD", board))
    
    # Add VIVADO_INPUT parameter (relative path to TCL directory)
    vivado_input = resolve_vivado_input()
    cmd_parts.append(format_make_parameter("VIVADO_INPUT", vivado_input))
    
    # Add ISA flags (USE_MUL_DIV, USE_COMPRESSED)
    isa_flags = get_isa_flags_from_config(config)
    cmd_parts.extend(isa_flags)
    
    cmd = " ".join(cmd_parts)
    log_event('MAKE_CMD_BUILT', command_type='fpga_bit_only', command=cmd)
    return cmd


def build_fpga_fw_run_command(config, benchmark_name, grab_timeout=None):
    """
    Build 'make fpga-fw-run' command for firmware build and run.
    
    This target does: clean software, build firmware, program FPGA, and run
    benchmark. It reuses the existing bitstream. Use this after fpga-bit-only
    when running multiple benchmarks on same hardware.
    
    Command format:
    make fpga-fw-run BOARD=<board> BENCHMARK_DIR=<path> GRAB_TIMEOUT=<t>
         VIVADO_INPUT=<path> [LLIB="..."]
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_name: Name of the benchmark to run
        grab_timeout: Timeout in seconds for UART grab (default: from config or 1000)
    
    Returns:
        String containing the make command
    """
    cmd_parts = ["make", cfg.MAKE_FPGA_FW_RUN]
    
    # Add BOARD parameter
    board = get_board_from_config(config)
    cmd_parts.append(format_make_parameter("BOARD", board))
    
    # Add BENCHMARK_DIR parameter (relative path to benchmark)
    benchmark_dir = resolve_benchmark_dir(benchmark_name)
    cmd_parts.append(format_make_parameter("BENCHMARK_DIR", benchmark_dir))
    
    # Add GRAB_TIMEOUT parameter (always use default, not from config)
    # This is for board acquisition timeout, not benchmark execution timeout
    grab_timeout = cfg.BOARD_GRAB_TIMEOUT_DEFAULT
    cmd_parts.append(format_make_parameter("GRAB_TIMEOUT", grab_timeout))
    
    # Add VIVADO_INPUT parameter
    vivado_input = resolve_vivado_input()
    cmd_parts.append(format_make_parameter("VIVADO_INPUT", vivado_input))
    
    # Add all custom flags from requirements.yaml
    custom_flags = get_benchmark_flags(benchmark_name)
    for flag_name, flag_value in custom_flags.items():
        cmd_parts.append(format_make_parameter(flag_name, flag_value))
        
    cmd = " ".join(cmd_parts)
    log_event('MAKE_CMD_BUILT',
              command_type='fpga_fw_run',
              benchmark=benchmark_name,
              command=cmd)
    return cmd


def get_build_strategy():
    """
    Get the current build strategy from settings.
    
    Returns:
        String: 'full' if FULL_MAKE_BUILD=True, 'split' otherwise
    """
    return 'full' if cfg.FULL_MAKE_BUILD else 'split'


def build_commands_for_strategy(config, benchmarks):
    """
    Build all make commands based on current build strategy.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmarks: List of benchmark names to run
    
    Returns:
        Dictionary with command structure based on strategy:
        
        If FULL_MAKE_BUILD=True (full strategy):
        {
            'strategy': 'full',
            'commands': [
                {'benchmark': 'coremark', 'command': 'make fpga-run ...'},
                {'benchmark': 'dhrystone', 'command': 'make fpga-run ...'},
            ]
        }
        
        If FULL_MAKE_BUILD=False (split strategy):
        {
            'strategy': 'split',
            'bitstream_command': 'make fpga-bit-only ...',
            'firmware_commands': [
                {'benchmark': 'coremark', 'command': 'make fpga-fw-run ...'},
                {'benchmark': 'dhrystone', 'command': 'make fpga-fw-run ...'},
            ]
        }
    """
    strategy = get_build_strategy()
    
    if strategy == 'full':
        # Full build per benchmark
        commands = []
        for benchmark_name in benchmarks:
            cmd = build_fpga_run_command(config, benchmark_name)
            commands.append({
                'benchmark': benchmark_name,
                'command': cmd
            })
        
        return {
            'strategy': 'full',
            'commands': commands
        }
    
    else:
        # Split: bitstream once, then firmware per benchmark
        bitstream_cmd = build_fpga_bit_only_command(config)
        
        firmware_commands = []
        for benchmark_name in benchmarks:
            cmd = build_fpga_fw_run_command(config, benchmark_name)
            firmware_commands.append({
                'benchmark': benchmark_name,
                'command': cmd
            })
        
        return {
            'strategy': 'split',
            'bitstream_command': bitstream_cmd,
            'firmware_commands': firmware_commands
        }