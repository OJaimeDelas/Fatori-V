# =============================================================================
# FATORI-V • Results • Build Metrics Collector
# File: build_collector.py
# -----------------------------------------------------------------------------
# Collects metrics from FPGA build process and Vivado reports.
# =============================================================================

import re
from pathlib import Path
from typing import Dict, Optional
from scripts.build.path_resolver import resolve_reports_dir, resolve_builddir
import fatori_settings as cfg
from scripts.logging import logger


def find_timing_report(reports_dir):
    """
    Find Vivado timing report in reports directory.
    
    Args:
        reports_dir: Path to reports directory
    
    Returns:
        Path to timing report, or None if not found
    """
    reports_dir = Path(reports_dir)
    
    if not reports_dir.exists():
        logger.log_event('WARNING', warning_message=f"Reports directory not found: {reports_dir}")
        return None
    
    # Common timing report names
    patterns = ['*timing*.rpt', '*_timing.txt', 'timing_summary.rpt']
    
    for pattern in patterns:
        matches = list(reports_dir.glob(pattern))
        if matches:
            logger.log_event('DEBUG', debug_message=f"Found timing report: {matches[0]}")
            return matches[0]
    
    logger.log_event('WARNING', warning_message="No timing report found")
    return None


def find_utilization_report(reports_dir):
    """
    Find Vivado utilization report in reports directory.
    
    Args:
        reports_dir: Path to reports directory
    
    Returns:
        Path to utilization report, or None if not found
    """
    reports_dir = Path(reports_dir)
    
    if not reports_dir.exists():
        return None
    
    # Common utilization report names
    patterns = ['*utilization*.rpt', '*_util.txt', 'utilization_placed.rpt']
    
    for pattern in patterns:
        matches = list(reports_dir.glob(pattern))
        if matches:
            logger.log_event('DEBUG', debug_message=f"Found utilization report: {matches[0]}")
            return matches[0]
    
    logger.log_event('WARNING', warning_message="No utilization report found")
    return None


def parse_timing_metrics(timing_report_path):
    """
    Parse timing metrics from Vivado timing report.
    
    Extracts WNS (Worst Negative Slack) and TNS (Total Negative Slack).
    
    Args:
        timing_report_path: Path to timing report
    
    Returns:
        Dictionary with timing metrics
    """
    if not timing_report_path or not timing_report_path.exists():
        return {}
    
    try:
        with timing_report_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        metrics = {}
        
        # Parse WNS (Worst Negative Slack)
        wns_match = re.search(r'WNS[:\s]+([-\d.]+)', content, re.IGNORECASE)
        if wns_match:
            metrics['wns'] = float(wns_match.group(1))
        
        # Parse TNS (Total Negative Slack)
        tns_match = re.search(r'TNS[:\s]+([-\d.]+)', content, re.IGNORECASE)
        if tns_match:
            metrics['tns'] = float(tns_match.group(1))
        
        # Determine if timing was met (WNS >= 0)
        if 'wns' in metrics:
           metrics['timing_met'] = metrics['wns'] >= 0
        
        logger.log_event('DEBUG', debug_message=f"Timing metrics: WNS={metrics.get('wns', 'N/A')}, TNS={metrics.get('tns', 'N/A')}")
        
        return metrics
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error parsing timing report: {e}")
        return {}


def parse_utilization_metrics(util_report_path):
    """
    Parse resource utilization from Vivado utilization report.
    
    Extracts LUT, FF, BRAM, DSP usage.
    
    Args:
        util_report_path: Path to utilization report
    
    Returns:
        Dictionary with utilization metrics
    """
    if not util_report_path or not util_report_path.exists():
        return {}
    
    try:
        with util_report_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        metrics = {}
        
        # Parse LUT count
        lut_match = re.search(r'Slice\s+LUTs[:\s|]+(\d+)', content, re.IGNORECASE)
        if lut_match:
            metrics['lut_count'] = int(lut_match.group(1))
        
        # Parse FF count
        ff_match = re.search(r'Slice\s+Registers[:\s|]+(\d+)', content, re.IGNORECASE)
        if not ff_match:
            ff_match = re.search(r'Register\s+as\s+Flip\s+Flop[:\s|]+(\d+)', content, re.IGNORECASE)
        if ff_match:
            metrics['ff_count'] = int(ff_match.group(1))
        
        # Parse BRAM count
        bram_match = re.search(r'Block\s+RAM\s+Tile[:\s|]+(\d+)', content, re.IGNORECASE)
        if not bram_match:
            bram_match = re.search(r'RAMB\d+[:\s|]+(\d+)', content, re.IGNORECASE)
        if bram_match:
            metrics['bram_count'] = int(bram_match.group(1))
        
        # Parse DSP count
        dsp_match = re.search(r'DSPs?[:\s|]+(\d+)', content, re.IGNORECASE)
        if dsp_match:
            metrics['dsp_count'] = int(dsp_match.group(1))
        
        logger.log_event('DEBUG', debug_message=f"Utilization: LUTs={metrics.get('lut_count', 'N/A')}, "
                   f"FFs={metrics.get('ff_count', 'N/A')}, "
                   f"BRAMs={metrics.get('bram_count', 'N/A')}, "
                   f"DSPs={metrics.get('dsp_count', 'N/A')}")
        
        return metrics
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error parsing utilization report: {e}")
        return {}


def get_build_log_path():
    """
    Get path to build log file.
    
    Returns:
        Path to build.log
    """
    return cfg.TMP_DIR / "build.log"


def parse_build_duration(build_log_path):
    """
    Parse build duration from build log.
    
    Args:
        build_log_path: Path to build log
    
    Returns:
        Build duration in seconds, or None
    """
    if not build_log_path or not build_log_path.exists():
        return None
    
    try:
        with build_log_path.open('r', encoding='utf-8', errors='replace') as f:
            content = f.read()
        
        # Look for elapsed time patterns
        patterns = [
            r'Elapsed\s+time[:\s]+([\d.]+)\s*s',
            r'Build\s+time[:\s]+([\d.]+)\s*s',
            r'Total\s+duration[:\s]+([\d.]+)\s*s',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return float(match.group(1))
        
        return None
    
    except Exception as e:
        logger.log_event('WARNING', warning_message=f"Error parsing build duration: {e}")
        return None


def collect_build_metrics(config):
    """
    Collect comprehensive build metrics.
    
    This gathers metrics from:
    - Vivado timing reports (WNS, TNS)
    - Vivado utilization reports (LUTs, FFs, BRAMs, DSPs)
    - Build log (duration, errors, warnings)
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        Dictionary with BuildMetrics:
        {
            'timing': {
                'wns': float,
                'tns': float,
                'timing_met': bool
            },
            'utilization': {
                'lut_count': int,
                'ff_count': int,
                'bram_count': int,
                'dsp_count': int
            },
            'build_duration_s': float,
            'reports_available': bool
        }
    """
    logger.log_event('DEBUG', debug_message="Collecting build metrics...")
    
    metrics = {
        'timing': {},
        'utilization': {},
        'build_duration_s': None,
        'reports_available': False
    }
    
    # Find reports directory
    reports_dir = resolve_reports_dir()
    
    if not reports_dir.exists():
        logger.log_event('WARNING', warning_message=f"Reports directory not found: {reports_dir}")
        logger.log_event('WARNING', warning_message="Build metrics will be incomplete")
        return metrics
    
    metrics['reports_available'] = True
    
    # Parse timing report
    timing_report = find_timing_report(reports_dir)
    if timing_report:
        metrics['timing'] = parse_timing_metrics(timing_report)
    
    # Parse utilization report
    util_report = find_utilization_report(reports_dir)
    if util_report:
        metrics['utilization'] = parse_utilization_metrics(util_report)
    
    # Parse build duration
    build_log = get_build_log_path()
    if build_log.exists():
        duration = parse_build_duration(build_log)
        if duration:
            metrics['build_duration_s'] = duration
    
    logger.log_event('DEBUG', debug_message="Build metrics collection complete")
    
    return metrics