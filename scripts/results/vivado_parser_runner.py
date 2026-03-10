# =============================================================================
# FATORI-V • Results • Vivado Parser Runner
# File: vivado_parser_runner.py
# -----------------------------------------------------------------------------
# Runs vivado_report_system parser on copied reports directory.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from scripts.logging.logger import log_event


def detect_report_prefix(reports_dir: Path) -> str:
    """
    Auto-detect report file prefix from .rpt files in directory.

    Iterates through all .rpt files in sorted order and returns the prefix
    from the first file whose suffix matches a known standard report type.
    Sorting ensures deterministic results across filesystems.

    Args:
        reports_dir: Directory containing report files

    Returns:
        Common prefix string, or empty string if no reports found
    """
    # Find all .rpt files, sorted for deterministic ordering
    report_files = sorted(reports_dir.glob('*.rpt'))

    if not report_files:
        return ""

    # Known suffixes for standard design-level reports
    known_suffixes = [
        '_utilization.rpt',
        '_hierarchical_utilization.rpt',
        '_timing_summary.rpt',
        '_timing_paths.rpt',
        '_timing.rpt',
        '_power.rpt',
        '_clocks.rpt',
        '_clock_interaction.rpt',
        '_cdc.rpt',
        '_synchronizer_mtbf.rpt',
        '_bus_skew.rpt',
        '_methodology.rpt',
        '_drc.rpt',
    ]

    # Scan all files; return prefix from first file that matches a known suffix.
    # This skips pblock utility reports (_pblock_*_util.rpt) which share the
    # same prefix but are not parsed by vivado_report_system.
    for report_file in report_files:
        name = report_file.name
        for suffix in known_suffixes:
            if name.endswith(suffix):
                return name[:-len(suffix)]

    # Fallback: no known suffix matched; strip last underscore segment
    first_name = report_files[0].name
    if '_' in first_name:
        return first_name.rsplit('_', 1)[0]
    return first_name.replace('.rpt', '')


def run_vivado_parser(reports_dir: Path) -> bool:
    """
    Run Vivado parser directly on reports directory.
    
    This imports and calls the parser's main() function directly,
    generating <prefix>_metrics.csv with hardware metrics.
    
    Args:
        reports_dir: Path to reports directory (should be results/<run_id>/reports/)
    
    Returns:
        Boolean indicating if parser ran successfully
    """
    # Check if reports directory exists
    if not reports_dir.exists():
        log_event('VIVADO_PARSER_REPORTS_MISSING', reports_dir=str(reports_dir))
        return False
    
    # Detect report prefix
    prefix = detect_report_prefix(reports_dir)
    
    if not prefix:
        log_event('VIVADO_PARSER_NO_REPORTS', reports_dir=str(reports_dir))
        return False
    
    try:
        log_event('VIVADO_PARSER_START',
                  reports_dir=str(reports_dir),
                  prefix=prefix)
        
        # Import parser module
        from scripts.reports.parser import vivado_report_system
        
        # Call parser directly (no subprocess)
        # Returns 0 on success, 1 on failure
        exit_code = vivado_report_system.main(
            str(reports_dir),  # input_dir
            prefix,             # prefix
            str(reports_dir)    # output_dir (same as input)
        )
        
        # Check if successful
        if exit_code == 0:
            # Parser creates <prefix>_metrics.csv in output directory
            output_file = reports_dir / f'{prefix}_metrics.csv'
            if output_file.exists():
                log_event('VIVADO_PARSER_SUCCESS',
                          output=str(output_file),
                          prefix=prefix)
                return True
            else:
                log_event('VIVADO_PARSER_NO_OUTPUT',
                          expected=str(output_file))
                return False
        else:
            log_event('VIVADO_PARSER_FAILED',
                      exit_code=exit_code)
            return False
    
    except ImportError as e:
        log_event('VIVADO_PARSER_IMPORT_ERROR',
                  error_message=str(e))
        return False
    
    except Exception as e:
        log_event('VIVADO_PARSER_EXCEPTION',
                  error_message=str(e))
        import traceback
        log_event('VIVADO_PARSER_TRACEBACK',
                  traceback=traceback.format_exc())
        return False


def parse_vivado_reports(run_dir: Path) -> bool:
    """
    Run Vivado parser on reports in run directory.
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Boolean indicating if parsing succeeded
    """
    reports_dir = run_dir / 'reports'
    return run_vivado_parser(reports_dir)