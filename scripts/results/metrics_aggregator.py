# =============================================================================
# FATORI-V • Results • Metrics Aggregator
# File: metrics_aggregator.py
# -----------------------------------------------------------------------------
# Aggregates metrics across all sessions and computes statistics.
# =============================================================================

from typing import List, Dict
from scripts.results.metrics_computer import (
    compute_error_detection_rate,
    compute_fi_coverage,
    compute_success_rate,
    compute_average_duration
)
from scripts.logging.logger import log_event


class MetricsAggregator:
    """
    Aggregates and computes statistics across all sessions.
    
    This class collects metrics from multiple sources and computes
    aggregate statistics, success rates, FI coverage, etc.
    """
    
    def __init__(self):
        """Initialize metrics aggregator."""
        self.session_metrics = []
        self.build_metrics = {}
        self._aggregates = None
        
        log_event('METRICS_AGGREGATOR_INITIALIZED')
    
    def add_session_metrics(self, session_metrics):
        """
        Add metrics from a single session.
        
        Args:
            session_metrics: Dictionary with session metrics
        """
        self.session_metrics.append(session_metrics)
        
        # Clear cached aggregates
        self._aggregates = None
    
    def add_build_metrics(self, build_metrics):
        """
        Add metrics from build process.
        
        Args:
            build_metrics: Dictionary with build metrics
        """
        self.build_metrics = build_metrics
        
        # Clear cached aggregates
        self._aggregates = None
    
    def get_session_count(self):
        """Get total number of sessions."""
        return len(self.session_metrics)
    
    def get_sessions_by_benchmark(self):
        """
        Group sessions by benchmark name.
        
        Returns:
            Dictionary mapping benchmark names to lists of session metrics
        """
        by_benchmark = {}
        
        for metrics in self.session_metrics:
            bench_name = metrics.get('benchmark_name', 'unknown')
            
            if bench_name not in by_benchmark:
                by_benchmark[bench_name] = []
            
            by_benchmark[bench_name].append(metrics)
        
        return by_benchmark
    
    def compute_aggregates(self):
        """
        Compute aggregate statistics across all sessions.
        
        This computes:
        - Overall success rates
        - Average durations
        - FI statistics
        - Per-benchmark statistics
        
        Returns:
            Dictionary with aggregate metrics
        """
        if self._aggregates is not None:
            return self._aggregates
        
        log_event('METRICS_AGGREGATION_COMPUTING')
        
        aggregates = {}
        
        # Overall statistics
        aggregates['session_count'] = len(self.session_metrics)
        
        # Success rates
        success_metrics = compute_success_rate(self.session_metrics)
        aggregates['success'] = success_metrics
        
        # Duration statistics
        avg_duration = compute_average_duration(self.session_metrics)
        if avg_duration:
            aggregates['average_duration_s'] = avg_duration
        
        # Total duration
        total_duration = sum(m.get('duration_s', 0) for m in self.session_metrics)
        aggregates['total_duration_s'] = total_duration
        
        # FI statistics
        fi_sessions = [m for m in self.session_metrics if m.get('injection_enabled')]
        if fi_sessions:
            aggregates['fi_enabled_count'] = len(fi_sessions)
            
            # Error detection rate
            detection_metrics = compute_error_detection_rate(fi_sessions)
            aggregates['fi_detection'] = detection_metrics
            
            # FI coverage
            coverage_metrics = compute_fi_coverage(fi_sessions)
            aggregates['fi_coverage'] = coverage_metrics
        else:
            aggregates['fi_enabled_count'] = 0
        
        # Per-benchmark statistics
        by_benchmark = self.get_sessions_by_benchmark()
        per_benchmark = {}
        
        for bench_name, bench_sessions in by_benchmark.items():
            bench_stats = {
                'session_count': len(bench_sessions),
                'success_count': sum(1 for m in bench_sessions if m.get('success')),
                'average_duration': compute_average_duration(bench_sessions),
            }
            
            # Average benchmark score if available
            scores = [m.get('benchmark_score') for m in bench_sessions if m.get('benchmark_score')]
            if scores:
                bench_stats['average_score'] = sum(scores) / len(scores)
            
            per_benchmark[bench_name] = bench_stats
        
        aggregates['per_benchmark'] = per_benchmark
        
        # Build metrics summary
        if self.build_metrics:
            build_summary = {}
            
            # Timing
            timing = self.build_metrics.get('timing', {})
            if timing:
                build_summary['wns'] = timing.get('wns')
                build_summary['timing_met'] = timing.get('timing_met', False)
            
            # Utilization
            util = self.build_metrics.get('utilization', {})
            if util:
                build_summary['lut_count'] = util.get('lut_count')
                build_summary['ff_count'] = util.get('ff_count')
                build_summary['bram_count'] = util.get('bram_count')
                build_summary['dsp_count'] = util.get('dsp_count')
            
            # Build duration
            build_summary['build_duration_s'] = self.build_metrics.get('build_duration_s')
            
            aggregates['build'] = build_summary
        
        # Cache aggregates
        self._aggregates = aggregates
        
        log_event('METRICS_AGGREGATION_COMPLETE')
        
        return aggregates
    
    def get_summary_dict(self):
        """
        Get comprehensive summary dictionary.
        
        Returns:
            Dictionary with all metrics (sessions + aggregates + build)
        """
        summary = {
            'session_metrics': self.session_metrics,
            'build_metrics': self.build_metrics,
            'aggregates': self.compute_aggregates()
        }
        
        return summary