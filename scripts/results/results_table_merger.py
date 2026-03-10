# =============================================================================
# FATORI-V • Results • Results Table Merger
# File: results_table_merger.py
# -----------------------------------------------------------------------------
# Merges bench metrics and reports CSVs into combined results table with XLS export.
# =============================================================================

import csv
from pathlib import Path
from typing import List, Dict
from scripts.logging.logger import log_event


def read_csv_to_list(csv_path: Path) -> List[List[str]]:
    """
    Read CSV file into list of lists.
    
    Args:
        csv_path: Path to CSV file
    
    Returns:
        List of rows (each row is a list of values)
    """
    rows = []
    
    try:
        with csv_path.open('r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                rows.append(row)
    except Exception as e:
        log_event('ERROR', error_message=f"Error reading {csv_path}: {e}")
    
    return rows


def merge_results_csvs(results_dir: Path) -> bool:
    """
    Merge bench_metrics.csv and reports CSV into combined results table.
    
    Creates a single CSV file with two logical sections:
    - Benchmark Metrics (from bench_metrics.csv)
    - FPGA Reports (from vivado parser CSV)
    
    Also exports to XLS format with two sheets.
    
    Args:
        results_dir: Path to results directory
    
    Returns:
        Boolean indicating success
    """
    log_event('RESULTS_MERGER_START')
    
    # Locate input files
    bench_metrics_path = results_dir / 'sessions' / 'bench_metrics.csv'
    reports_dir = results_dir / 'reports'
    
    # Find reports CSV (name varies by board)
    reports_csv_path = None
    if reports_dir.exists():
        for csv_file in reports_dir.glob('*_metrics.csv'):
            reports_csv_path = csv_file
            break
    
    if not bench_metrics_path.exists():
        log_event('WARNING', warning_message=f"Bench metrics not found: {bench_metrics_path}")
        return False
    
    # Read bench metrics
    bench_metrics_rows = read_csv_to_list(bench_metrics_path)
    
    # Read reports metrics if available
    reports_rows = []
    if reports_csv_path and reports_csv_path.exists():
        reports_rows = read_csv_to_list(reports_csv_path)
    
    # Generate run ID from results directory name
    run_id = results_dir.name
    
    # Create combined CSV
    combined_csv_path = results_dir / f'{run_id}_results_table.csv'
    
    try:
        with combined_csv_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Write benchmark metrics section
            writer.writerow(['=== BENCHMARK METRICS ==='])
            writer.writerow([])
            for row in bench_metrics_rows:
                writer.writerow(row)
            
            writer.writerow([])
            writer.writerow([])
            
            # Write reports section if available
            if reports_rows:
                writer.writerow(['=== FPGA REPORTS ==='])
                writer.writerow([])
                for row in reports_rows:
                    writer.writerow(row)
        
        log_event('RESULTS_MERGER_CSV_SUCCESS', output=str(combined_csv_path))
        
        # Export to XLS with two sheets
        if export_to_xls(combined_csv_path, bench_metrics_rows, reports_rows, run_id):
            log_event('RESULTS_MERGER_XLS_SUCCESS')
        else:
            log_event('RESULTS_MERGER_XLS_FAILED')
        
        return True
    
    except Exception as e:
        log_event('ERROR', error_message=f"Error merging results: {e}")
        return False


def export_to_xls(csv_path: Path, bench_metrics_rows: List[List[str]], 
                  reports_rows: List[List[str]], run_id: str) -> bool:
    """
    Export combined results to XLS format with two sheets.
    
    Args:
        csv_path: Path to combined CSV file
        bench_metrics_rows: Benchmark metrics data
        reports_rows: Reports data
        run_id: Run identifier
    
    Returns:
        Boolean indicating success
    """
    try:
        import xlsxwriter
    except ImportError:
        log_event('DEBUG', debug_message="xlsxwriter not installed, skipping XLS export (pip install xlsxwriter to enable)")
        return False
    
    xls_path = csv_path.parent / f'{run_id}_results_table.xlsx'
    
    try:
        workbook = xlsxwriter.Workbook(str(xls_path))
        
        # Sheet 1: Benchmark Metrics
        if bench_metrics_rows:
            bench_sheet = workbook.add_worksheet('Benchmark Metrics')
            
            for row_idx, row in enumerate(bench_metrics_rows):
                for col_idx, value in enumerate(row):
                    # Force string type for values that might be dates (like "1-1-1")
                    # Check if value looks like it could be misinterpreted as date
                    if isinstance(value, str) and '-' in value and not value.startswith('0x'):
                        bench_sheet.write_string(row_idx, col_idx, value)
                    else:
                        bench_sheet.write(row_idx, col_idx, value)
        
        # Sheet 2: FPGA Reports
        if reports_rows:
            reports_sheet = workbook.add_worksheet('FPGA Reports')
            
            for row_idx, row in enumerate(reports_rows):
                for col_idx, value in enumerate(row):
                    # Force string type for values that might be dates
                    if isinstance(value, str) and '-' in value and not value.startswith('0x'):
                        reports_sheet.write_string(row_idx, col_idx, value)
                    else:
                        reports_sheet.write(row_idx, col_idx, value)
        
        workbook.close()
        
        log_event('XLS_EXPORT_SUCCESS', output=str(xls_path))
        return True
    
    except Exception as e:
        log_event('ERROR', error_message=f"Error exporting to XLS: {e}")
        return False