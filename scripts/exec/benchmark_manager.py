# =============================================================================
# FATORI-V • Execution • Benchmark Manager
# File: benchmark_manager.py
# -----------------------------------------------------------------------------
# Central manager for all benchmark operations during execution.
# =============================================================================

from typing import List, Optional
from scripts.exec.benchmark_discovery import (
    BenchmarkInfo,
    discover_benchmarks,
    filter_enabled_benchmarks,
    filter_by_category,
    has_fi_benchmarks
)
from scripts.exec.benchmark_config import extract_benchmark_configs
from scripts.exec.benchmark_validator import validate_benchmarks
from scripts.exec.benchmark_orderer import order_benchmarks
from scripts.logging.logger import log_event


class BenchmarkManager:
    """
    Central manager for benchmark operations.
    
    This class provides a unified interface for:
    - Discovering benchmarks from configuration
    - Validating benchmark setups
    - Ordering benchmarks for execution
    - Querying benchmark information
    - Managing execution state
    """
    
    def __init__(self, config):
        """
        Initialize benchmark manager with configuration.
        
        Args:
            config: The loaded YAML configuration dictionary
        """
        self.config = config
        self._all_benchmarks = None
        self._enabled_benchmarks = None
        self._execution_order = None
        self._configs = None
        
        log_event('BENCHMARK_MANAGER_INITIALIZED')
    
    def discover_all(self):
        """
        Discover all benchmarks from configuration.
        
        This includes both enabled and disabled benchmarks.
        Results are cached for subsequent calls.
        
        Returns:
            List of BenchmarkInfo objects
        """
        if self._all_benchmarks is None:
            self._all_benchmarks = discover_benchmarks(self.config)
        
        return self._all_benchmarks
    
    def get_enabled(self):
        """
        Get list of enabled benchmarks.
        
        Returns:
            List of BenchmarkInfo objects (only enabled)
        """
        if self._enabled_benchmarks is None:
            all_benchmarks = self.discover_all()
            self._enabled_benchmarks = filter_enabled_benchmarks(all_benchmarks)
        
        return self._enabled_benchmarks
    
    def get_by_name(self, name):
        """
        Get a specific benchmark by name.
        
        Args:
            name: Benchmark name
        
        Returns:
            BenchmarkInfo object, or None if not found
        """
        all_benchmarks = self.discover_all()
        
        for bench in all_benchmarks:
            if bench.name.lower() == name.lower():
                return bench
        
        log_event('BENCHMARK_NOT_FOUND', benchmark_name=name)
        return None
    
    def get_by_category(self, category):
        """
        Get all benchmarks of a specific category.
        
        Args:
            category: Category name (e.g., "coremark", "fatori_stress")
        
        Returns:
            List of BenchmarkInfo objects matching category
        """
        all_benchmarks = self.discover_all()
        return filter_by_category(all_benchmarks, category)
    
    def get_execution_order(self, strategy='yaml_sequence'):
        """
        Get benchmarks in execution order.
        
        This returns enabled benchmarks ordered according to the
        specified strategy. Results are cached per strategy.
        
        Args:
            strategy: Ordering strategy (default: 'yaml_sequence')
        
        Returns:
            List of BenchmarkInfo objects in execution order
        """
        # Check cache
        if self._execution_order is not None:
            return self._execution_order
        
        # Get enabled benchmarks and order them
        enabled = self.get_enabled()
        self._execution_order = order_benchmarks(enabled, strategy=strategy)
        
        return self._execution_order
    
    def has_fi_enabled(self):
        """
        Check if any enabled benchmark has fault injection enabled.
        
        Returns:
            Boolean indicating if FI is used
        """
        enabled = self.get_enabled()
        return has_fi_benchmarks(enabled)
    
    def validate_all(self):
        """
        Validate all enabled benchmarks.
        
        This performs comprehensive validation of benchmark configurations
        and directories.
        
        Returns:
            Tuple of (errors: List[str], warnings: List[str])
        """
        errors, warnings = validate_benchmarks(self.config)
        return errors, warnings
    
    def get_configs(self):
        """
        Get extracted configurations for all benchmarks.
        
        Returns:
            Dictionary mapping benchmark names to their configurations
        """
        if self._configs is None:
            self._configs = extract_benchmark_configs(self.config)
        
        return self._configs
    
    def get_config_for(self, benchmark_name):
        """
        Get configuration for a specific benchmark.
        
        Args:
            benchmark_name: Name of the benchmark
        
        Returns:
            Configuration dictionary, or empty dict if not found
        """
        configs = self.get_configs()
        return configs.get(benchmark_name, {})
    
    def get_summary(self):
        """
        Get summary of benchmark manager state.
        
        Returns:
            Dictionary with summary information
        """
        all_benchmarks = self.discover_all()
        enabled = self.get_enabled()
        
        # Count by category
        category_counts = {}
        for bench in enabled:
            category_counts[bench.category] = category_counts.get(bench.category, 0) + 1
        
        # Count FI-enabled
        fi_count = sum(1 for b in enabled if b.injection)
        
        summary = {
            'total_benchmarks': len(all_benchmarks),
            'enabled_benchmarks': len(enabled),
            'disabled_benchmarks': len(all_benchmarks) - len(enabled),
            'fi_enabled_count': fi_count,
            'categories': category_counts,
            'has_fi': self.has_fi_enabled()
        }
        
        return summary
    
    def print_summary(self):
        """
        Print a formatted summary to the logger.
        """
        summary = self.get_summary()
        
        log_event('BENCHMARK_SUMMARY',
                  total_benchmarks=summary['total_benchmarks'],
                  enabled_benchmarks=summary['enabled_benchmarks'],
                  disabled_benchmarks=summary['disabled_benchmarks'],
                  fi_enabled_count=summary['fi_enabled_count'],
                  categories=summary['categories'])