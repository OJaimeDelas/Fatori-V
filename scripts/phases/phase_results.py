# =============================================================================
# FATORI-V • Results Phase Executor
# File: phase_results.py
# -----------------------------------------------------------------------------
# Executes results collection and packaging phase.
# =============================================================================

from pathlib import Path
from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.results.session_collector import collect_all_session_metrics
from scripts.results.build_collector import collect_build_metrics
from scripts.results.metrics_aggregator import MetricsAggregator
from scripts.results.summary_generator import generate_run_summary
from scripts.results.excel_exporter import export_to_excel
from scripts.results.csv_exporter import export_all_csvs
from scripts.results.results_packager import package_results
from scripts.results.results_validator import validate_results
from scripts.exec.session_manager import SessionManager
from scripts.logging.logger import log_event
import fatori_settings as cfg


def get_all_sessions(results_dir: Path):
    """
    Get all session objects from results directory.
    
    Args:
        results_dir: Results directory path
    
    Returns:
        List of Session objects
    """
    # Create session manager
    session_manager = SessionManager()
    
    # Get all sessions
    all_sessions = session_manager.get_all_sessions()
    
    log_event('RESULTS_SESSIONS_FOUND', session_count=len(all_sessions))
    
    return all_sessions


def execute_results_phase(context: RunContext) -> bool:
    """
    Execute results phase.
    
    This collects all metrics, generates reports, and packages results:
    1. Collect session metrics from all benchmark executions
    2. Collect build metrics from Vivado reports
    3. Aggregate metrics across all sessions
    4. Generate text summary report
    5. Export to Excel workbook (if available)
    6. Export to CSV files
    7. Package complete results directory
    8. Validate results package
    
    Args:
        context: Run context with configuration and results
    
    Returns:
        Boolean indicating if results phase succeeded
    """
    log_event('RESULTS_PHASE_START')
    
    try:
        # Step 1: Collect session metrics
        log_event('RESULTS_SESSION_COLLECTION_START')
        
        sessions = get_all_sessions(context.results_dir)
        
        if not sessions:
            log_event('RESULTS_NO_SESSIONS')
            session_metrics = []
        else:
            session_metrics = collect_all_session_metrics(sessions)
            log_event('RESULTS_SESSION_METRICS_COLLECTED', count=len(session_metrics))
        
        # Step 2: Collect build metrics
        log_event('RESULTS_BUILD_COLLECTION_START')
        build_metrics = collect_build_metrics(context.config)
        
        if build_metrics.get('reports_available'):
            log_event('RESULTS_BUILD_METRICS_COLLECTED')
        else:
            log_event('RESULTS_BUILD_METRICS_UNAVAILABLE')
        
        # Step 3: Aggregate metrics
        log_event('RESULTS_AGGREGATION_START')
        aggregator = MetricsAggregator()
        
        # Add session metrics
        for metrics in session_metrics:
            aggregator.add_session_metrics(metrics)
        
        # Add build metrics
        aggregator.add_build_metrics(build_metrics)
        
        # Compute aggregates
        aggregates = aggregator.compute_aggregates()
        log_event('RESULTS_AGGREGATION_COMPLETE', 
                  session_count=aggregates.get('session_count', 0))
        
        # Step 4: Generate summary report
        log_event('RESULTS_SUMMARY_GENERATION_START')
        summary_text = generate_run_summary(context.config, aggregator)
        summary_path = context.results_dir / "run_summary.txt"
        with summary_path.open('w', encoding='utf-8') as f:
            f.write(summary_text)
        log_event('RESULTS_SUMMARY_GENERATED', summary_path=str(summary_path))
        
        # Step 5: Export to Excel
        log_event('RESULTS_EXCEL_EXPORT_START')
        excel_path = context.results_dir / "metrics.xlsx"
        if export_to_excel(aggregator, excel_path, context.config):
            log_event('RESULTS_EXCEL_EXPORTED', excel_path=str(excel_path))
        else:
            log_event('RESULTS_EXCEL_EXPORT_FAILED')
        
        # Step 6: Export to CSV
        log_event('RESULTS_CSV_EXPORT_START')
        csv_results = export_all_csvs(aggregator, context.results_dir)
        log_event('RESULTS_CSV_EXPORTED', csv_count=len(csv_results))
        
        # Step 7: Validate results package
        log_event('RESULTS_VALIDATION_START')
        is_valid, errors, warnings = validate_results(context.results_dir)
        
        if not is_valid:
            log_event('RESULTS_VALIDATION_FAILED', 
                      error_count=len(errors),
                      errors=errors)
        else:
            log_event('RESULTS_VALIDATION_PASSED')
        
        if warnings:
            log_event('RESULTS_VALIDATION_WARNINGS',
                      warning_count=len(warnings))
        
        # Step 8: Final summary
        log_event('RESULTS_PHASE_SUMMARY',
                  results_dir=str(context.results_dir),
                  session_count=len(session_metrics),
                  build_metrics_available=build_metrics.get('reports_available', False),
                  excel_generated=excel_path.exists(),
                  csv_count=len(csv_results))
        
        return True
    
    except Exception as e:
        log_event('RESULTS_PHASE_EXCEPTION', error_message=str(e))
        import traceback
        log_event('RESULTS_TRACEBACK', traceback=traceback.format_exc())
        return False


class ResultsPhaseExecutor(PhaseExecutor):
    """
    Executor for results phase.
    """
    
    def __init__(self):
        super().__init__("results")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute results phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_results_phase(context)
    
    def post_execute(self, context: RunContext, success: bool):
        """
        Post-execution hook for results phase.
        
        Args:
            context: Run context
            success: Whether results phase succeeded
        """
        super().post_execute(context, success)
        
        if success:
            log_event('RESULTS_PACKAGE_COMPLETE', 
                      results_dir=str(context.results_dir))