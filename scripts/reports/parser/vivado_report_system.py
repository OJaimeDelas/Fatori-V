# =============================================================================
# FATORI-V • FI Report Parsing System
# File: vivado_report_system.py
# -----------------------------------------------------------------------------
# Main entry point for Vivado report parsing and CSV export
# =============================================================================

import os
import sys
import csv

# Add project root to path for logger import
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from scripts.logging.logger import log_event

# Add parsers directory to path for imports (no __init__.py approach)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'parsers'))

# Import all parser modules

# Import all parser modules
import common
import parse_utilization
import parse_hierarchical_utilization
import parse_timing
import parse_timing_detail
import parse_timing_paths
import parse_power
import parse_clocks
import parse_clock_interaction
import parse_cdc
import parse_synchronizer_mtbf
import parse_bus_skew
import parse_methodology
import parse_drc


def main(input_dir, prefix, output_dir):
    """
    Main orchestrator for parsing Vivado reports and generating CSV
    
    Args:
        input_dir: Directory containing report files
        prefix: Common prefix of report files (e.g., 'design_device')
        output_dir: Directory where CSV output will be saved
    
    Flow:
        1. Verify input directory exists
        2. Create output directory if needed
        3. Parse each report type (skip if missing)
        4. Collect common metadata across all reports
        5. Generate CSV file with all metrics
    """
    
    log_event('PARSER_START', reports_dir=input_dir)
    log_event('INFO', info_message=f"Report prefix: {prefix}")
    log_event('INFO', info_message=f"Output directory: {output_dir}")
    
    # Verify input directory exists
    if not os.path.isdir(input_dir):
        log_event('ERROR_DIRECTORY_NOT_FOUND', dir_path=input_dir)
        return 1
    
    # Create output directory if needed
    os.makedirs(output_dir, exist_ok=True)
    
    # Storage for all parsed data
    # Structure: {report_name: [(metric_id, value), ...]}
    all_reports_data = {}
    
    # Common metadata extracted from reports (design name, device, etc.)
    common_data = {}
    
    # Parse each report type
    log_event('INFO', info_message="Parsing Vivado reports")
    
    # 1. Utilization - overall resource usage
    parse_report(
        input_dir, prefix, "_utilization.rpt",
        parse_utilization.parse,
        "Utilization", all_reports_data, common_data
    )
    
    # 2. Hierarchical Utilization - per-module breakdown (critical for FT)
    parse_report(
        input_dir, prefix, "_hierarchical_utilization.rpt",
        parse_hierarchical_utilization.parse,
        "Hierarchical_Util", all_reports_data, common_data
    )
    
    # 3. Timing Summary - WNS, WHS, constraint status
    parse_report(
        input_dir, prefix, "_timing_summary.rpt",
        parse_timing.parse,
        "Timing", all_reports_data, common_data
    )
    
    # 4. Timing Paths - critical path analysis
    parse_report(
        input_dir, prefix, "_timing_paths.rpt",
        parse_timing_paths.parse,
        "Timing_Paths", all_reports_data, common_data
    )
    
    # 4b. Timing Detail - single critical path with detailed breakdown
    parse_report(
        input_dir, prefix, "_timing.rpt",
        parse_timing_detail.parse,
        "Timing_Detail", all_reports_data, common_data
    )
    
    # 5. Power - consumption breakdown
    parse_report(
        input_dir, prefix, "_power.rpt",
        parse_power.parse,
        "Power", all_reports_data, common_data
    )
    
    # 6. Clocks - clock domain info
    parse_report(
        input_dir, prefix, "_clocks.rpt",
        parse_clocks.parse,
        "Clocks", all_reports_data, common_data
    )
    
    # 7. Clock Interaction - inter-domain timing
    parse_report(
        input_dir, prefix, "_clock_interaction.rpt",
        parse_clock_interaction.parse,
        "Clock_Interaction", all_reports_data, common_data
    )
    
    # 8. CDC - clock domain crossing safety
    parse_report(
        input_dir, prefix, "_cdc.rpt",
        parse_cdc.parse,
        "CDC", all_reports_data, common_data
    )
    
    # 9. Synchronizer MTBF - reliability metrics
    parse_report(
        input_dir, prefix, "_synchronizer_mtbf.rpt",
        parse_synchronizer_mtbf.parse,
        "Sync_MTBF", all_reports_data, common_data
    )
    
    # 10. Bus Skew - bus timing analysis
    parse_report(
        input_dir, prefix, "_bus_skew.rpt",
        parse_bus_skew.parse,
        "Bus_Skew", all_reports_data, common_data
    )
    
    # 11. Methodology - design quality warnings
    parse_report(
        input_dir, prefix, "_methodology.rpt",
        parse_methodology.parse,
        "Methodology", all_reports_data, common_data
    )
    
    # 12. DRC - design rule checks
    parse_report(
        input_dir, prefix, "_drc.rpt",
        parse_drc.parse,
        "DRC", all_reports_data, common_data
    )
    
    # Generate CSV output if any reports were parsed
    if all_reports_data:
        output_file = os.path.join(output_dir, f"{prefix}_metrics.csv")
        generate_csv(output_file, common_data, all_reports_data)
        
        # Calculate total metrics
        total_metrics = sum(len(data) for data in all_reports_data.values())
        log_event('PARSER_COMPLETE', metric_count=total_metrics)
        log_event('INFO', info_message=f"Processed {len(all_reports_data)} reports, extracted {len(common_data)} parameters")
        return 0
    else:
        log_event('ERROR', error_message="No reports found. CSV file not created")
        log_event('INFO', info_message="Check that report files exist with correct prefix")
        return 1


def parse_report(input_dir, prefix, suffix, parser_func, report_name, 
                 all_data, common_data):
    """
    Attempt to parse a single report type with better diagnostics
    
    Args:
        input_dir: Directory containing reports
        prefix: File prefix
        suffix: File suffix (e.g., '_utilization.rpt')
        parser_func: Parser function to call
        report_name: Name for this report in output
        all_data: Dictionary to store parsed data
        common_data: Dictionary to store common metadata
    
    Logic:
        - Check if file exists
        - If yes: call parser, store results, update common data
        - If no: log message and continue
        - Show metrics extracted count
    """
    filepath = os.path.join(input_dir, f"{prefix}{suffix}")
    report_file = f"{prefix}{suffix}"
    
    if os.path.exists(filepath):
        log_event('PARSER_REPORT_PARSED', report_type=report_name, report_file=report_file)
        try:
            # Call parser function
            data, common_info = parser_func(filepath)
            # Store results
            all_data[report_name] = data
            common_data.update(common_info)
            
            # Show metrics count
            if data and len(data) > 0:
                log_event('INFO', info_message=f"  Extracted {len(data)} metrics from {report_name}")
            else:
                log_event('WARNING', warning_message=f"No metrics extracted from {report_name} (empty result)")
                
        except Exception as e:
            log_event('PARSER_ERROR_PARSE_FAILED', report_file=report_file, error_message=str(e))
            import traceback
            if "--debug" in sys.argv:
                log_event('DEBUG', debug_message="Traceback:")
                traceback.print_exc()
            # Store empty data so report appears in output
            all_data[report_name] = []
    else:
        log_event('PARSER_ERROR_REPORT_MISSING', report_type=report_file)

def generate_csv(output_file, common_data, all_reports_data):
    """
    Generate CSV file with all parsed metrics (Excel-optimized)
    
    Args:
        output_file: Path to output CSV file
        common_data: Dictionary of common info (design, device, etc.)
        all_reports_data: Dictionary mapping report names to metric lists
    
    CSV Structure:
        Row 1: Report names (repeated for each column pair)
        Row 2: Column headers (Parameter/Value for common, Metric/Value for reports)
        Row 3+: Data rows
        
        Columns:
        [Common Param][Common Val][Report1 ID][Report1 Val][Report2 ID][Report2 Val]...
    
    Excel Compatibility:
        - UTF-8 BOM for proper character encoding
        - Proper quoting for fields with commas
        - Warning about empty reports
    """
    
    log_event('INFO', info_message="Generating CSV file")
    
    # Check for empty reports and warn
    empty_reports = []
    for report_name, data_list in all_reports_data.items():
        if not data_list or len(data_list) == 0:
            empty_reports.append(report_name)
    
    if empty_reports:
        log_event('WARNING', warning_message=f"{len(empty_reports)} report(s) have no data: {', '.join(empty_reports)}")
    
    # Calculate maximum number of rows needed
    max_data_rows = len(common_data)
    for data_list in all_reports_data.values():
        max_data_rows = max(max_data_rows, len(data_list))
    
    # Open CSV file for writing with UTF-8 BOM for Excel compatibility
    with open(output_file, 'w', newline='', encoding='utf-8-sig') as csvfile:
        writer = csv.writer(csvfile, quoting=csv.QUOTE_MINIMAL)
        
        # Row 1: Report section headers
        row1 = ["Common Info", ""]  # Common info spans 2 columns
        for report_name in all_reports_data.keys():
            row1.extend([report_name, ""])  # Each report spans 2 columns
        writer.writerow(row1)
        
        # Row 2: Column headers
        row2 = ["Parameter", "Value"]  # Common columns
        for report_name in all_reports_data.keys():
            row2.extend(["Metric ID", "Value"])  # Report columns
        writer.writerow(row2)
        
        # Data rows
        # Convert common_data dict to list for indexing
        common_items = list(common_data.items())
        
        # Convert all_reports_data to list of lists for indexing
        reports_lists = {}
        for report_name, data_list in all_reports_data.items():
            reports_lists[report_name] = data_list
        
        # Write data rows
        for row_idx in range(max_data_rows):
            row_data = []
            
            # Common data (first 2 columns)
            if row_idx < len(common_items):
                param_name, param_value = common_items[row_idx]
                row_data.extend([param_name, param_value])
            else:
                row_data.extend(["", ""])  # Empty cells
            
            # Each report's data (2 columns per report)
            for report_name in all_reports_data.keys():
                data_list = reports_lists[report_name]
                if row_idx < len(data_list):
                    metric_id, value = data_list[row_idx]
                    # Clean up text fields - truncate if too long
                    metric_id_clean = str(metric_id)[:100]
                    value_clean = str(value)[:200]
                    row_data.extend([metric_id_clean, value_clean])
                else:
                    row_data.extend(["", ""])  # Empty cells
            
            writer.writerow(row_data)
    
    log_event('INFO', info_message=f"Rows written: {max_data_rows + 2} ({len(empty_reports)} empty reports)")
    log_event('INFO', info_message="CSV file saved with UTF-8 BOM encoding for Excel compatibility")

if __name__ == "__main__":
    # Check for help or debug flags
    if "--help" in sys.argv or "-h" in sys.argv:
        print("Usage: python vivado_report_system.py <input_dir> <prefix> <output_dir> [--debug]")
        print()
        print("Arguments:")
        print("  <input_dir>   Directory containing Vivado report files")
        print("  <prefix>      Common prefix of report files")
        print("  <output_dir>  Directory where CSV output will be saved")
        print()
        print("Options:")
        print("  --debug       Show detailed error traces for failed parsers")
        print()
        print("Example:")
        print("  python vivado_report_system.py ./reports design_device ./output")
        print()
        print("Expected files:")
        print("  <prefix>_utilization.rpt")
        print("  <prefix>_hierarchical_utilization.rpt")
        print("  <prefix>_timing_summary.rpt")
        print("  <prefix>_timing.rpt")
        print("  <prefix>_timing_paths.rpt")
        print("  <prefix>_power.rpt")
        print("  <prefix>_clocks.rpt")
        print("  <prefix>_clock_interaction.rpt")
        print("  <prefix>_cdc.rpt")
        print("  <prefix>_synchronizer_mtbf.rpt")
        print("  <prefix>_bus_skew.rpt")
        print("  <prefix>_methodology.rpt")
        print("  <prefix>_drc.rpt")
        print()
        print("Output: CSV file (no external dependencies required)")
        print("  - Opens directly in Excel, LibreOffice, or Google Sheets")
        print("  - UTF-8 encoded with BOM for Excel compatibility")
        sys.exit(0)
    
    # Parse command line arguments (ignore --debug flag)
    args = [arg for arg in sys.argv[1:] if not arg.startswith('--')]
    
    if len(args) == 3:
        input_directory = args[0]
        file_prefix = args[1]
        output_directory = args[2]
    else:
        # Show usage
        print("Usage: python vivado_report_system.py <input_dir> <prefix> <output_dir> [--debug]")
        print()
        print("Use --help for detailed information")
        sys.exit(1)
    
    # Run main function
    exit_code = main(input_directory, file_prefix, output_directory)
    sys.exit(exit_code)