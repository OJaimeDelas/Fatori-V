# =============================================================================
# FATORI-V • Build System • Path Resolver
# File: path_resolver.py
# -----------------------------------------------------------------------------
# Resolves build-related paths for make commands and file operations.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.logging.logger import log_event


def resolve_builddir():
    """
    Resolve path to the build directory (iob_soc_V1.0/).
    
    This is where make commands are executed.
    
    Returns:
        Path object to build directory
    """
    return cfg.BUILDDIR


def resolve_vivado_input():
    """
    Resolve relative path to VIVADO_INPUT directory for make commands.
    
    This should be the TCL directory relative to the build directory.
    From iob_soc_V1.0/, the path is ../tmp/tcl/
    
    Returns:
        String with relative path suitable for VIVADO_INPUT parameter
    """
    # From builddir to tmp/tcl is: ../tmp/tcl
    return "../tmp/tcl"


def resolve_benchmark_dir(benchmark_name):
    """
    Resolve relative path to benchmark directory for make commands.
    
    From iob_soc_V1.0/, benchmarks are at: ../../benchmarks/<n>/
    
    Args:
        benchmark_name: Name of the benchmark
    
    Returns:
        String with relative path suitable for BENCHMARK_DIR parameter
    """
    # From builddir to benchmarks is: ../../benchmarks/<n>
    return f"../../benchmarks/{benchmark_name}"


def resolve_sync_file():
    """
    Resolve path to sync file used for UART synchronization.
    
    The sync file is in tmp/sync/ and is used to coordinate between
    FPGA runs and the monitoring system.
    
    Returns:
        Path object to sync file
    """
    sync_dir = cfg.TMP_SYNC_DIR
    sync_dir.mkdir(parents=True, exist_ok=True)
    return sync_dir / "sync_file.sync"


def resolve_reports_dir():
    """
    Resolve path to Vivado reports directory.
    
    Reports are generated during FPGA synthesis and placed in:
    builddir/hardware/fpga/reports/
    
    Returns:
        Path object to reports directory
    """
    builddir = resolve_builddir()
    reports_dir = builddir / cfg.REPORTS_DIR_RELATIVE
    return reports_dir


def resolve_architecture_dir():
    """
    Resolve path to architecture directory.
    
    This is where all architecture files are organized.
    
    Returns:
        Path object to architecture directory
    """
    return cfg.ARCHITECTURE_DIR


def resolve_generated_dir():
    """
    Resolve path to generated files directory.
    
    This is where all generated files are placed before allocation.
    
    Returns:
        Path object to generated directory
    """
    return cfg.TMP_GENERATED_DIR


def resolve_tcl_dir():
    """
    Resolve path to TCL files directory.
    
    This is where generated TCL scripts are placed before allocation.
    
    Returns:
        Path object to TCL directory
    """
    return cfg.TMP_TCL_DIR


def resolve_backup_dir():
    """
    Resolve path to backup directory.
    
    This is where file backups are stored before allocation.
    
    Returns:
        Path object to backup directory
    """
    return cfg.TMP_BACKUP_DIR


def get_builddir_relative_path(target_path):
    """
    Get relative path from builddir to a target path.
    
    This is useful for constructing make command parameters that need
    to reference files relative to the build directory.
    
    Args:
        target_path: Absolute path to target
    
    Returns:
        String with relative path from builddir to target
    """
    builddir = resolve_builddir()
    target_path = Path(target_path)
    
    try:
        relative = target_path.relative_to(builddir)
        return str(relative)
    except ValueError:
        # If not under builddir, compute relative path
        try:
            relative = Path(target_path).relative_to(cfg.ROOT_DIR)
            # Go up from builddir to root, then down to target
            up_levels = len(builddir.relative_to(cfg.ROOT_DIR).parts)
            relative_str = "../" * up_levels + str(relative)
            return relative_str
        except ValueError:
            # If all else fails, return absolute path
            log_event('PATH_RESOLVE_WARNING',
                      builddir=str(builddir),
                      target_path=str(target_path))
            return str(target_path.absolute())