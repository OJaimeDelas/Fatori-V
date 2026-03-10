# =============================================================================
# FATORI-V • Results • Run Results Generator
# File: run_results_generator.py
# -----------------------------------------------------------------------------
# Generates run_results CSV/XLSX with 2 sheets (metrics + vivado).
# =============================================================================

import csv
from pathlib import Path
from typing import Dict, List, Optional
from scripts.logging.logger import log_event


def collect_all_session_metrics(run_dir: Path) -> List[Dict]:
    """
    Collect metrics from all sessions.
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        List of dictionaries with session metrics
    """
    sessions_dir = run_dir / 'sessions'
    all_metrics = []
    
    if not sessions_dir.exists():
        return all_metrics
    
    for session_path in sessions_dir.iterdir():
        if session_path.is_dir():
            bench_id = session_path.name
            metrics_path = session_path / 'metrics.txt'
            
            if metrics_path.exists():
                metrics = {'benchmark': bench_id}
                
                with metrics_path.open('r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if ':' in line:
                            key, value = line.split(':', 1)
                            metrics[key.strip()] = value.strip()
                
                all_metrics.append(metrics)
    
    return all_metrics


def load_vivado_metrics(run_dir: Path) -> List[Dict]:
    """
    Load parsed vivado metrics from reports/parsed_reports.csv.
    
    Args:
        run_dir: Path to run directory
    
    Returns:
        List of dictionaries with vivado metrics
    """
    parsed_path = run_dir / 'reports' / 'parsed_reports.csv'
    
    if not parsed_path.exists():
        log_event('RUN_RESULTS_NO_VIVADO_METRICS', parsed_path=str(parsed_path))
        return []
    
    try:
        with parsed_path.open('r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            return list(reader)
    
    except Exception as e:
        log_event('RUN_RESULTS_VIVADO_LOAD_ERROR', error_message=str(e))
        return []


def generate_run_results_csv(run_dir: Path, run_id: str) -> bool:
    """
    Generate run_results_<run_id>.csv with 2 sheets.
    
    Since CSV doesn't support multiple sheets, we create a single file
    with clear section headers.
    
    Args:
        run_dir: Path to run directory
        run_id: Run identifier
    
    Returns:
        Boolean indicating if generation succeeded
    """
    output_path = run_dir / f'run_results_{run_id}.csv'
    
    # Collect metrics
    session_metrics = collect_all_session_metrics(run_dir)
    vivado_metrics = load_vivado_metrics(run_dir)
    
    try:
        with output_path.open('w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Sheet 1: Session Metrics
            writer.writerow(['=== SESSION METRICS ==='])
            writer.writerow([])
            
            if session_metrics:
                # Get all unique keys
                all_keys = set()
                for m in session_metrics:
                    all_keys.update(m.keys())
                all_keys = sorted(all_keys)
                
                # Write header
                writer.writerow(all_keys)
                
                # Write data
                for metrics in session_metrics:
                    writer.writerow([metrics.get(k, '') for k in all_keys])
            else:
                writer.writerow(['No session metrics available'])
            
            # Separator
            writer.writerow([])
            writer.writerow([])
            
            # Sheet 2: Vivado Metrics
            writer.writerow(['=== VIVADO HARDWARE METRICS ==='])
            writer.writerow([])
            
            if vivado_metrics:
                # Get keys from first row
                keys = list(vivado_metrics[0].keys())
                
                # Write header
                writer.writerow(keys)
                
                # Write data
                for metrics in vivado_metrics:
                    writer.writerow([metrics.get(k, '') for k in keys])
            else:
                writer.writerow(['No vivado metrics available'])
        
        log_event('RUN_RESULTS_CSV_GENERATED', output=str(output_path))
        return True
    
    except Exception as e:
        log_event('RUN_RESULTS_CSV_FAILED', error_message=str(e))
        return False


def generate_run_results_xlsx(run_dir: Path, run_id: str) -> bool:
    """
    Generate run_results_<run_id>.xlsx with 2 sheets.
    
    Sheet 1: Session metrics
    Sheet 2: Vivado hardware metrics
    
    Args:
        run_dir: Path to run directory
        run_id: Run identifier
    
    Returns:
        Boolean indicating if generation succeeded
    """
    try:
        import openpyxl
        from openpyxl import Workbook
    except ImportError:
        log_event('RUN_RESULTS_XLSX_UNAVAILABLE')
        return False
    
    output_path = run_dir / f'run_results_{run_id}.xlsx'
    
    # Collect metrics
    session_metrics = collect_all_session_metrics(run_dir)
    vivado_metrics = load_vivado_metrics(run_dir)
    
    try:
        # Create workbook
        wb = Workbook()
        
        # Sheet 1: Session Metrics
        ws1 = wb.active
        ws1.title = 'Session Metrics'
        
        if session_metrics:
            # Get all unique keys
            all_keys = set()
            for m in session_metrics:
                all_keys.update(m.keys())
            all_keys = sorted(all_keys)
            
            # Write header
            ws1.append(all_keys)
            
            # Write data
            for metrics in session_metrics:
                ws1.append([metrics.get(k, '') for k in all_keys])
        else:
            ws1.append(['No session metrics available'])
        
        # Sheet 2: Vivado Metrics
        ws2 = wb.create_sheet('Vivado Metrics')
        
        if vivado_metrics:
            # Get keys from first row
            keys = list(vivado_metrics[0].keys())
            
            # Write header
            ws2.append(keys)
            
            # Write data
            for metrics in vivado_metrics:
                ws2.append([metrics.get(k, '') for k in keys])
        else:
            ws2.append(['No vivado metrics available'])
        
        # Save
        wb.save(str(output_path))
        
        log_event('RUN_RESULTS_XLSX_GENERATED', output=str(output_path))
        return True
    
    except Exception as e:
        log_event('RUN_RESULTS_XLSX_FAILED', error_message=str(e))
        return False


def generate_run_results(run_dir: Path, run_id: str) -> bool:
    """
    Generate both CSV and XLSX run results files.
    
    Args:
        run_dir: Path to run directory
        run_id: Run identifier
    
    Returns:
        Boolean indicating if at least one file was generated
    """
    csv_ok = generate_run_results_csv(run_dir, run_id)
    xlsx_ok = generate_run_results_xlsx(run_dir, run_id)
    
    return csv_ok or xlsx_ok