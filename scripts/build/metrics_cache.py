# =============================================================================
# FATORI-V • Build System • Architecture Metrics Cache
# File: metrics_cache.py
# -----------------------------------------------------------------------------
# Cache architecture metrics to avoid re-parsing when running multiple benchmarks.
# =============================================================================

import json
import shutil
from pathlib import Path
from datetime import datetime
from scripts.logging.logger import log_event
from scripts.common.common_settings import *


class ArchitectureMetricsCache:
    """
    Cache for architecture-level metrics that don't change between benchmarks.
    
    Cached data includes:
    - Vivado reports (utilization, timing, power)
    - Generated files (headers, TCL scripts)
    - Pblock information
    - Build configuration hash
    
    This cache is valid as long as hardware configuration doesn't change.
    """
    
    def __init__(self, cache_dir):
        """
        Initialize metrics cache.
        
        Args:
            cache_dir: Directory to store cached metrics
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.manifest_file = self.cache_dir / 'metrics_manifest.json'
        self.reports_dir = self.cache_dir / 'reports'
        self.files_dir = self.cache_dir / 'files'
    
    def cache_metrics(self, metrics_data, config_hash):
        """
        Cache architecture metrics from build.
        
        Args:
            metrics_data: Dictionary with:
                - vivado_reports: Dict of {report_type: report_path}
                - generated_files: List of generated file paths
                - pblock_config: Pblock configuration dict
                - timing: Timing metrics dict
                - utilization: Utilization metrics dict
            config_hash: Hash of hardware configuration for validation
        """
        log_event('CACHE_METRICS_START')
        
        # Create cache directories
        self.reports_dir.mkdir(exist_ok=True)
        self.files_dir.mkdir(exist_ok=True)
        
        # Copy Vivado reports
        cached_reports = {}
        for report_type, report_path in metrics_data.get('vivado_reports', {}).items():
            source_path = Path(report_path)
            if source_path.exists():
                dest = self.reports_dir / source_path.name
                shutil.copy2(source_path, dest)
                cached_reports[report_type] = str(dest)
                log_event('FILE_CACHED', file_type=report_type, file_path=str(dest))
        
        # Copy generated files
        cached_files = []
        for file_path in metrics_data.get('generated_files', []):
            source_path = Path(file_path)
            if source_path.exists():
                dest = self.files_dir / source_path.name
                shutil.copy2(source_path, dest)
                cached_files.append(str(dest))
                log_event('FILE_CACHED', file_type='generated', file_path=str(dest))
        
        # Build manifest
        manifest = {
            'cached_at': datetime.now().isoformat(),
            'config_hash': config_hash,
            'metrics': {
                'timing': metrics_data.get('timing', {}),
                'utilization': metrics_data.get('utilization', {}),
                'pblock': metrics_data.get('pblock_config', {})
            },
            'cached_reports': cached_reports,
            'cached_files': cached_files
        }
        
        # Save manifest
        with self.manifest_file.open('w') as f:
            json.dump(manifest, f, indent=2)
        
        log_event('CACHE_METRICS_COMPLETE', cache_dir=str(self.cache_dir))
    
    def load_metrics(self, config_hash):
        """
        Load cached architecture metrics.
        
        Args:
            config_hash: Current hardware configuration hash for validation
        
        Returns:
            Dictionary with cached metrics, or None if cache invalid/missing
        """
        if not self.is_valid():
            log_event('CACHE_MISS', reason='Cache not found')
            return None
        
        # Load manifest
        with self.manifest_file.open('r') as f:
            manifest = json.load(f)
        
        # Validate configuration hash
        cached_hash = manifest.get('config_hash')
        if cached_hash != config_hash:
            log_event('CACHE_MISS', reason='Configuration changed')
            return None
        
        log_event('CACHE_HIT', cache_dir=str(self.cache_dir))
        
        return {
            'metrics': manifest.get('metrics', {}),
            'cached_reports': manifest.get('cached_reports', {}),
            'cached_files': manifest.get('cached_files', []),
            'cached_at': manifest.get('cached_at')
        }
    
    def is_valid(self):
        """
        Check if cache exists and is structurally valid.
        
        Returns:
            Boolean indicating if cache is valid
        """
        return (
            self.manifest_file.exists() and
            self.reports_dir.exists() and
            self.files_dir.exists()
        )
    
    def clear(self):
        """Clear the entire cache."""
        if self.cache_dir.exists():
            shutil.rmtree(self.cache_dir)
            log_event('CACHE_CLEARED', cache_dir=str(self.cache_dir))
    
    def get_cache_info(self):
        """
        Get information about current cache.
        
        Returns:
            Dictionary with cache metadata, or None if no cache
        """
        if not self.is_valid():
            return None
        
        with self.manifest_file.open('r') as f:
            manifest = json.load(f)
        
        return {
            'cached_at': manifest.get('cached_at'),
            'config_hash': manifest.get('config_hash'),
            'report_count': len(manifest.get('cached_reports', {})),
            'file_count': len(manifest.get('cached_files', []))
        }


def compute_hardware_config_hash(config):
    """
    Compute hash of hardware configuration for cache validation.
    
    This hash should change whenever hardware configuration changes
    (board, ISA extensions, FTM settings, etc.) but remain stable
    for different benchmarks.
    
    Args:
        config: The loaded YAML configuration dictionary
    
    Returns:
        String hash of hardware configuration
    """
    import hashlib
    
    # Extract hardware-relevant configuration
    hw_config = {
        'board': get_nested(config, KEY_RUN, KEY_RUN_HW, KEY_HW_BOARD),
        'isa_rv32m': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M),
        'isa_rv32c': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32C),
        'isa_rv32b': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32B),
        'ftm_register_mon': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_REG_MON),
        'ftm_logic_mon': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_LOGIC_MON),
        'ftm_regfile_ecc': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_RF_ECC),
        'ftm_regfile_we_glitch': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_RF_WE_GLITCH),
        'ftm_hardened_pc': get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_HARDENED_PC),
    }
    
    # Compute hash
    config_str = json.dumps(hw_config, sort_keys=True)
    hash_obj = hashlib.sha256(config_str.encode('utf-8'))
    return hash_obj.hexdigest()[:16]