# =============================================================================
# FATORI-V • Results • Session Results Generator
# File: session_results_generator.py
# -----------------------------------------------------------------------------
# Generates bench_results CSV/XLSX for individual sessions.
# =============================================================================

import csv
from pathlib import Path
from typing import Dict, List, Optional
from scripts.logging.logger import log_event


def parse_metrics_txt(metrics_path: Path) -> Dict:
    """
    Parse metrics.txt file and extract key metrics.
    
    Args:
        metrics_path: Path to metrics.txt file
    
    Returns:
        Dictionary with parsed metrics
    """
    metrics = {}
    
    if not metrics_path.exists():
        return metrics
    
    try:
        with metrics_path.open('r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if ':' in line:
                    key, value = line.split(':', 1)
                    metrics[key.strip()] = value.strip()
        
        return metrics
    
    except Exception as e:
        log_event('SESSION_RESULTS_PARSE_ERROR',
                  metrics_path=str(metrics_path),
                  error_message=str(e))
        return metrics


def generate_session_results_csv(session_dir: Path, bench_id: str) -> bool:
    """
    Generate bench_results_<bench_id>.csv for a session.
    
    Args:
        session_dir: Path to session directory
        bench_id: Benchmark identifier
    
    Returns:
        Boolean indicating if generation succeeded
    """
    metrics_path = session_dir / 'metrics.txt'
    output_path = session_dir / f'bench_results_{bench_id}.csv'
    
    # Parse metrics
    metrics = parse_metrics_txt(metrics_path)
    
    if not metrics:
        log_event('SESSION_RESULTS_NO_METRICS',
                  bench_id=bench_id,
                  session_dir=str(session_dir))
        return False
    
    try:
        # Write CSV with metrics
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Header
            writer.writerow(['Metric', 'Value'])
            
            # Data rows
            for key, value in metrics.items():
                writer.writerow([key, value])
        
        log_event('SESSION_RESULTS_CSV_GENERATED',
                  bench_id=bench_id,
                  output=str(output_path))
        
        return True
    
    except Exception as e:
        log_event('SESSION_RESULTS_CSV_FAILED',
                  bench_id=bench_id,
                  error_message=str(e))
        return False


def generate_session_results_xlsx(session_dir: Path, bench_id: str) -> bool:
    """
    Generate bench_results_<bench_id>.xlsx for a session.
    
    This creates an Excel version of the CSV file.
    
    Args:
        session_dir: Path to session directory
        bench_id: Benchmark identifier
    
    Returns:
        Boolean indicating if generation succeeded
    """
    try:
        import openpyxl
        from openpyxl import Workbook
    except ImportError:
        log_event('SESSION_RESULTS_XLSX_UNAVAILABLE', bench_id=bench_id)
        return False
    
    metrics_path = session_dir / 'metrics.txt'
    output_path = session_dir / f'bench_results_{bench_id}.xlsx'
    
    # Parse metrics
    metrics = parse_metrics_txt(metrics_path)
    
    if not metrics:
        return False
    
    try:
        # Create workbook
        wb = Workbook()
        ws = wb.active
        ws.title = 'Metrics'
        
        # Header
        ws.append(['Metric', 'Value'])
        
        # Data rows
        for key, value in metrics.items():
            ws.append([key, value])
        
        # Save
        wb.save(str(output_path))
        
        log_event('SESSION_RESULTS_XLSX_GENERATED',
                  bench_id=bench_id,
                  output=str(output_path))
        
        return True
    
    except Exception as e:
        log_event('SESSION_RESULTS_XLSX_FAILED',
                  bench_id=bench_id,
                  error_message=str(e))
        return False


def generate_all_session_results(run_dir: Path) -> int:
    """
    Generate results files for all sessions in run directory.
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        Number of sessions processed
    """
    sessions_dir = run_dir / 'sessions'
    
    if not sessions_dir.exists():
        log_event('SESSION_RESULTS_NO_SESSIONS_DIR', run_dir=str(run_dir))
        return 0
    
    count = 0
    for session_path in sessions_dir.iterdir():
        if session_path.is_dir():
            bench_id = session_path.name
            
            # Generate CSV
            csv_ok = generate_session_results_csv(session_path, bench_id)
            
            # Generate XLSX
            xlsx_ok = generate_session_results_xlsx(session_path, bench_id)
            
            if csv_ok or xlsx_ok:
                count += 1
    
    log_event('SESSION_RESULTS_GENERATION_COMPLETE', session_count=count)
    
    return count