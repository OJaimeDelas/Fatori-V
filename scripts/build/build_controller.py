# =============================================================================
# FATORI-V • Build System • Build Controller
# File: build_controller.py
# -----------------------------------------------------------------------------
# Main controller that integrates file allocation with build orchestration.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.build.file_allocator import allocate_files
from scripts.build.build_orchestrator import build_hardware, BuildResult
from scripts.build.build_settings import CLEAN_BEFORE_BUILD, RUN_IBEX_SETUP
from scripts.logging.logger import log_event


def run_build_phase(config, allocate_only=False, skip_clean=None, skip_ibex_setup=None):
    """
    Main entry point for build phase.
    
    This orchestrates the complete build process:
    1. Allocate generated and static files to architecture
    2. Build FPGA hardware bitstream
    3. Handle errors and report status
    
    Args:
        config: The loaded YAML configuration dictionary
        allocate_only: If True, only allocate files without building
        skip_clean: Override CLEAN_BEFORE_BUILD setting (None uses default)
        skip_ibex_setup: Override RUN_IBEX_SETUP setting (None uses default)
    
    Returns:
        Dictionary with build results:
        {
            'success': bool,
            'allocated_files': dict,
            'build_result': BuildResult or None
        }
    """
    log_event('BUILD_PHASE_START')
    
    results = {
        'success': False,
        'allocated_files': None,
        'build_result': None
    }
    
    # Step 1: File Allocation
    log_event('BUILD_FILE_ALLOCATION_START')
    
    try:
        allocated_files = allocate_files(config, backup_enabled=True)
        results['allocated_files'] = allocated_files
        
        total_allocated = sum(len(files) for files in allocated_files.values())
        log_event('BUILD_FILES_ALLOCATED', file_count=total_allocated)
        
    except Exception as e:
        log_event('BUILD_FILE_ALLOCATION_ERROR', error_message=str(e))
        return results
    
    # If allocate_only, stop here
    if allocate_only:
        log_event('BUILD_ALLOCATION_ONLY_COMPLETE')
        results['success'] = True
        return results
    
    # Step 2: Hardware Build
    log_event('BUILD_HARDWARE_START')
    
    # Determine skip flags
    if skip_clean is None:
        skip_clean = not CLEAN_BEFORE_BUILD
    
    if skip_ibex_setup is None:
        skip_ibex_setup = not RUN_IBEX_SETUP
    
    try:
        build_result = build_hardware(
            config,
            skip_clean=skip_clean,
            skip_ibex_setup=skip_ibex_setup
        )
        
        results['build_result'] = build_result
        results['success'] = build_result.success
        
        # Report build status
        if build_result.success:
            log_event('BUILD_PHASE_SUCCESS')
        else:
            log_event('BUILD_PHASE_FAILED',
                      step_completed=build_result.step_completed,
                      error_message=build_result.error_message)
            
            # Print error analysis if available
            if build_result.error_analysis:
                analysis = build_result.error_analysis
                
                if analysis['errors']:
                    log_event('BUILD_ERRORS_DETECTED',
                              error_count=len(analysis['errors']),
                              first_errors=analysis['errors'][:5])
                
                if analysis['suggestions']:
                    log_event('BUILD_SUGGESTIONS_AVAILABLE',
                              suggestions=analysis['suggestions'])
            
            if build_result.log_file:
                log_event('BUILD_LOG_AVAILABLE', log_file=str(build_result.log_file))
        
        return results
    
    except Exception as e:
        log_event('BUILD_ORCHESTRATION_ERROR', error_message=str(e))
        results['success'] = False
        return results


def get_build_status(config):
    """
    Check if a bitstream exists for the current configuration.
    
    This doesn't trigger a build, just checks if build artifacts exist.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with status information:
        {
            'bitstream_exists': bool,
            'bitstream_path': Path or None
        }
    """
    from scripts.build.path_resolver import resolve_builddir
    
    builddir = resolve_builddir()
    
    # Look for bitstream file in expected location
    # Typically: hardware/fpga/vivado/<board>/top_system.bit
    from scripts.mapping.board_mapping import get_make_board_name
    from scripts.common.common_settings import KEY_RUN, KEY_RUN_HW, KEY_HW_BOARD
    from scripts.common.yaml_io.yaml_helpers import get_nested
    
    board_yaml = get_nested(config, KEY_RUN, KEY_RUN_HW, KEY_HW_BOARD, default=None)
    board_make = get_make_board_name(board_yaml)
    
    bitstream_path = builddir / "hardware" / "fpga" / "vivado" / board_make / "top_system.bit"
    
    exists = bitstream_path.exists()
    
    return {
        'bitstream_exists': exists,
        'bitstream_path': bitstream_path if exists else None
    }