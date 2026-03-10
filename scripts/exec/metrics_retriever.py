# =============================================================================
# FATORI-V • Execution • Metrics Retriever
# File: metrics_retriever.py
# -----------------------------------------------------------------------------
# Retrieves metrics.txt from architecture after benchmark execution.
# =============================================================================

import shutil
from pathlib import Path
from typing import Optional
import fatori_settings as cfg
from scripts.logging.logger import log_event


def get_metrics_file_path() -> Path:
    """
    Get path to metrics.txt in architecture.
    
    Returns:
        Path to metrics.txt file
    """
    # Metrics file is in iob_soc_V1.0/hardware/fpga/metrics.txt (directly under ROOT_DIR)
    metrics_path = cfg.ROOT_DIR / 'iob_soc_V1.0' / 'hardware' / 'fpga' / 'metrics.txt'
    
    return metrics_path


def retrieve_metrics_after_execution(session_dir: Path, bench_id: str) -> bool:
    """
    Retrieve metrics.txt from architecture after benchmark execution.
    
    This copies the metrics.txt file from the architecture directory
    to the session directory immediately after a benchmark completes.
    
    Args:
        session_dir: Path to session directory
        bench_id: Benchmark identifier for logging
    
    Returns:
        Boolean indicating if retrieval succeeded
    """
    source_path = get_metrics_file_path()
    dest_path = session_dir / 'metrics.txt'
    
    # Check if source exists
    if not source_path.exists():
        log_event('METRICS_RETRIEVAL_SOURCE_MISSING',
                  bench_id=bench_id,
                  source=str(source_path))
        return False
    
    try:
        # Copy metrics file to session directory
        shutil.copy2(source_path, dest_path)
        
        log_event('METRICS_RETRIEVED',
                  bench_id=bench_id,
                  source=str(source_path),
                  dest=str(dest_path))
        
        return True
    
    except Exception as e:
        log_event('METRICS_RETRIEVAL_FAILED',
                  bench_id=bench_id,
                  error_message=str(e))
        return False


def check_metrics_exist() -> bool:
    """
    Check if metrics.txt exists in architecture.
    
    Returns:
        Boolean indicating if metrics file exists
    """
    metrics_path = get_metrics_file_path()
    return metrics_path.exists()