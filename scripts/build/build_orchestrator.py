# =============================================================================
# FATORI-V • Build System • Build Orchestrator
# File: build_orchestrator.py
# -----------------------------------------------------------------------------
# Orchestrates multi-step FPGA build process with error handling.
# =============================================================================

import fatori_settings as cfg
from scripts.build.build_settings import *
from scripts.build.make_executor import execute_make_command
from scripts.build.progress_tracker import BuildProgressTracker
from scripts.build.path_resolver import resolve_builddir
from scripts.build.error_handler import analyze_build_failure
from scripts.logging.logger import log_event


class BuildResult:
    """
    Container for build result information.
    """
    
    def __init__(self, success, step_completed, error_message=None, log_file=None):
        """
        Initialize build result.
        
        Args:
            success: Boolean indicating if build succeeded
            step_completed: Last step that completed successfully
            error_message: Error message if build failed
            log_file: Path to build log file
        """
        self.success = success
        self.step_completed = step_completed
        self.error_message = error_message
        self.log_file = log_file
        self.error_analysis = None
    
    def __str__(self):
        if self.success:
            return f"Build successful (completed: {self.step_completed})"
        else:
            return f"Build failed at {self.step_completed}: {self.error_message}"

def skip_build_for_execution_phase(config, benchmarks):
    """
    Skip build phase when using FULL_MAKE_BUILD strategy.
    
    When FULL_MAKE_BUILD is True, fpga-run does both build and execution.
    This means the BUILD phase should do nothing, and let the EXECUTION
    phase handle running fpga-run commands.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmarks: List of benchmark names
    
    Returns:
        BuildResult indicating build was skipped
    """
    log_event('BUILD_SKIP_FULL_STRATEGY',
              reason='fpga-run will be called in EXECUTION phase',
              benchmark_count=len(benchmarks))
    
    # Create log file for consistency
    log_file = cfg.TMP_DIR / "build.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    return BuildResult(
        success=True,
        step_completed='skipped_for_execution',
        log_file=log_file
    )

def execute_full_build_strategy(config, benchmarks, builddir, log_file):
    """
    Execute full build strategy: fpga-run per benchmark.
    
    This strategy calls 'make fpga-run' once per benchmark. Each call does
    complete build cycle: clean, setup, bitstream, firmware, run.
    
    Architecture metrics are cached from first benchmark build and reused
    for subsequent benchmarks to avoid re-parsing reports.
    
    Args:
        config: Run configuration dictionary
        benchmarks: List of benchmark names
        builddir: Build directory path
        log_file: Build log file path
    
    Returns:
        BuildResult object
    """
    from scripts.build.make_commands import build_fpga_run_command
    from scripts.build.metrics_cache import ArchitectureMetricsCache, compute_hardware_config_hash
    
    log_event('BUILD_STRATEGY_FULL', benchmark_count=len(benchmarks))
    
    # Initialize metrics cache
    cache_dir = cfg.TMP_DIR / 'metrics_cache'
    metrics_cache = ArchitectureMetricsCache(cache_dir)
    config_hash = compute_hardware_config_hash(config)
    
    # Initialize progress tracker
    tracker = BuildProgressTracker(benchmarks)
    
    architecture_metrics_cached = False
    
    for idx, benchmark_name in enumerate(benchmarks):
        log_event('BUILD_BENCHMARK_START', 
                  benchmark=benchmark_name,
                  number=idx + 1,
                  total=len(benchmarks))
        
        # Build command
        cmd = build_fpga_run_command(config, benchmark_name)
        
        # Execute build
        success, error_message, exit_code = execute_make_command(
            cmd,
            cwd=cfg.ARCHITECTURE_DIR,
            log_file=log_file,
            timeout=None
        )
        
        if not success:
            error_analysis = analyze_build_failure(log_file, error_message)
            return BuildResult(
                success=False,
                step_completed=f'fpga_run_{benchmark_name}',
                error_message=error_analysis.get('summary', 'Build failed'),
                log_file=log_file
            )
        
        # Cache architecture metrics from first successful build
        if idx == 0 and not architecture_metrics_cached:
            try:
                from scripts.reports.metrics_collector import collect_architecture_metrics
                log_event('COLLECT_ARCHITECTURE_METRICS')
                arch_metrics = collect_architecture_metrics(builddir)
                metrics_cache.cache_metrics(arch_metrics, config_hash)
                architecture_metrics_cached = True
            except Exception as e:
                log_event('WARNING', warning_message=f"Failed to cache metrics: {e}")
        
        tracker.complete_step(f'fpga_run_{benchmark_name}')
        log_event('BUILD_BENCHMARK_COMPLETE', benchmark=benchmark_name)
    
    log_event('BUILD_HARDWARE_COMPLETE', strategy='full')
    return BuildResult(
        success=True,
        step_completed='all',
        log_file=log_file
    )


def execute_split_build_strategy(config, benchmarks, builddir, log_file):
    """
    Execute split build strategy: fpga-bit-only + fpga-fw-run per benchmark.
    
    This strategy:
    1. Calls 'make fpga-bit-only' once to build bitstream
    2. Calls 'make fpga-fw-run' once per benchmark to build firmware and run
    
    Architecture metrics are cached after bitstream build and reused for all
    benchmark runs.
    
    Args:
        config: Run configuration dictionary
        benchmarks: List of benchmark names
        builddir: Build directory path
        log_file: Build log file path
    
    Returns:
        BuildResult object
    """
    from scripts.build.make_commands import build_fpga_bit_only_command, build_fpga_fw_run_command
    from scripts.build.metrics_cache import ArchitectureMetricsCache, compute_hardware_config_hash
    
    log_event('BUILD_STRATEGY_SPLIT', benchmark_count=len(benchmarks))
    
    # Initialize metrics cache
    cache_dir = cfg.TMP_DIR / 'metrics_cache'
    metrics_cache = ArchitectureMetricsCache(cache_dir)
    config_hash = compute_hardware_config_hash(config)
    
    # Initialize progress tracker
    steps = ['bitstream'] + benchmarks  # bitstream + firmware builds
    tracker = BuildProgressTracker(steps)
    
    # Step 1: Build bitstream
    log_event('BUILD_BITSTREAM_START')
    bitstream_cmd = build_fpga_bit_only_command(config)
    
    success, error_message, exit_code = execute_make_command(
        bitstream_cmd,
        cwd=cfg.ARCHITECTURE_DIR,
        log_file=log_file,
        timeout=None
    )
    
    if not success:
        error_analysis = analyze_build_failure(log_file, error_message)
        return BuildResult(
            success=False,
            step_completed='fpga_bit_only',
            error_message=error_analysis.get('summary', 'Bitstream build failed'),
            log_file=log_file
        )
    
    tracker.complete_step('fpga_bit_only')
    log_event('BUILD_BITSTREAM_COMPLETE')
    
    # Cache architecture metrics
    try:
        from scripts.reports.metrics_collector import collect_architecture_metrics
        log_event('COLLECT_ARCHITECTURE_METRICS')
        arch_metrics = collect_architecture_metrics(builddir)
        metrics_cache.cache_metrics(arch_metrics, config_hash)
    except Exception as e:
        log_event('WARNING', warning_message=f"Failed to cache metrics: {e}")
    
    # Step 2: Build and run firmware for each benchmark
    for idx, benchmark_name in enumerate(benchmarks):
        log_event('BUILD_FIRMWARE_START',
                  benchmark=benchmark_name,
                  number=idx + 1,
                  total=len(benchmarks))
        
        # Build command
        firmware_cmd = build_fpga_fw_run_command(config, benchmark_name)
        
        # Execute build
        success, error_message, exit_code = execute_make_command(
            firmware_cmd,
            cwd=cfg.ARCHITECTURE_DIR,
            log_file=log_file,
            timeout=None
        )
        
        if not success:
            error_analysis = analyze_build_failure(log_file, error_message)
            return BuildResult(
                success=False,
                step_completed=f'fpga_fw_run_{benchmark_name}',
                error_message=error_analysis.get('summary', 'Firmware build failed'),
                log_file=log_file
            )
        
        tracker.complete_step(f'fpga_fw_run_{benchmark_name}')
        log_event('BUILD_FIRMWARE_COMPLETE', benchmark=benchmark_name)
    
    log_event('BUILD_HARDWARE_COMPLETE', strategy='split')
    return BuildResult(
        success=True,
        step_completed='all',
        log_file=log_file
    )


def build_hardware(config, benchmarks):
    """
    Build FPGA hardware using appropriate strategy.
    
    Strategy selection based on cfg.FULL_MAKE_BUILD:
    - True: Use fpga-run per benchmark (full rebuild each time)
    - False: Use fpga-bit-only once, then fpga-fw-run per benchmark
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmarks: List of benchmark names to build/run
    
    Returns:
        BuildResult object with build status
    """
    log_event('BUILD_HARDWARE_START', 
              strategy='full' if cfg.FULL_MAKE_BUILD else 'split',
              benchmark_count=len(benchmarks))
    
    # Create build log file
    log_file = cfg.TMP_DIR / "build.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Execute build strategy
    if cfg.FULL_MAKE_BUILD:
        # Skip build - EXECUTION phase will call fpga-run
        return skip_build_for_execution_phase(config, benchmarks)
    else:
        # Split strategy: build bitstream now, firmware in execution
        return execute_split_build_strategy(config, benchmarks, builddir, log_file)