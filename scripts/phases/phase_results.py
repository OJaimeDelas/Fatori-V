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


def get_all_sessions(config, results_dir):
    """
    Get all session objects from results directory.
    
    Args:
        config: The loaded YAML configuration dictionary
        results_dir: Results directory path
    
    Returns:
        List of Session objects
    """
    # Create session manager
    session_manager = SessionManager(config, results_dir)
    
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
        # Step 1: Distribute generated files to appropriate locations
        import shutil
        log_event('RESULTS_GEN_FILES_DISTRIBUTING')
        
        gen_source_dir = cfg.ROOT_DIR / 'tmp' / 'generated'
        
        if gen_source_dir.exists():
            # Create run-level gen/ directory for non-benchmark-specific files
            run_gen_dir = context.results_dir / 'gen'
            run_gen_dir.mkdir(parents=True, exist_ok=True)
            
            copied_count = 0
            benchmark_configs_distributed = 0
            
            # Iterate through all generated files
            for gen_file in gen_source_dir.iterdir():
                if not gen_file.is_file():
                    continue
                
                # Check if this is a benchmark-specific config file
                # Format: bench_config_<benchmark_name>.h
                if gen_file.name.startswith('bench_config_') and gen_file.name.endswith('.h'):
                    # Extract benchmark name from filename
                    # Example: bench_config_hello_world.h -> hello_world
                    bench_name = gen_file.name.replace('bench_config_', '').replace('.h', '')
                    
                    # Copy to session-specific gen/ folder
                    session_gen_dir = context.results_dir / 'sessions' / bench_name / 'gen'
                    session_gen_dir.mkdir(parents=True, exist_ok=True)
                    
                    dest_file = session_gen_dir / gen_file.name
                    shutil.copy2(gen_file, dest_file)
                    benchmark_configs_distributed += 1
                else:
                    # Non-benchmark-specific files go to run-level gen/
                    dest_file = run_gen_dir / gen_file.name
                    shutil.copy2(gen_file, dest_file)
                    copied_count += 1
            
            log_event('RESULTS_GEN_FILES_DISTRIBUTED',
                      run_level_count=copied_count,
                      benchmark_configs_count=benchmark_configs_distributed)
        else:
            log_event('RESULTS_GEN_DIR_NOT_FOUND', gen_dir=str(gen_source_dir))
        
        # Step 1.5: Copy TCL files to results/gen/tcl/
        tcl_source_dir = cfg.ROOT_DIR / 'tmp' / 'tcl'
        
        if tcl_source_dir.exists():
            # Create gen/tcl/ directory
            tcl_dest_dir = context.results_dir / 'gen' / 'tcl'
            tcl_dest_dir.mkdir(parents=True, exist_ok=True)
            
            tcl_copied_count = 0
            
            # Copy all TCL files
            for tcl_file in tcl_source_dir.iterdir():
                if tcl_file.is_file() and tcl_file.suffix == '.tcl':
                    dest_file = tcl_dest_dir / tcl_file.name
                    shutil.copy2(tcl_file, dest_file)
                    tcl_copied_count += 1
            
            log_event('RESULTS_TCL_FILES_COPIED', count=tcl_copied_count)
        else:
            log_event('RESULTS_TCL_DIR_NOT_FOUND', tcl_dir=str(tcl_source_dir))
        
        # Step 2: Collect metrics from all sessions
        from scripts.results.reports_copier import copy_reports_to_results
        from scripts.results.vivado_parser_runner import parse_vivado_reports
        
        log_event('RESULTS_REPORTS_COPYING')
        if copy_reports_to_results(context.results_dir):
            log_event('RESULTS_REPORTS_COPY_SUCCESS')
            
            # Run vivado parser on copied reports
            log_event('RESULTS_PARSER_RUNNING')
            if parse_vivado_reports(context.results_dir):
                log_event('RESULTS_PARSER_SUCCESS')
            else:
                log_event('RESULTS_PARSER_FAILED')
        else:
            log_event('RESULTS_REPORTS_COPY_FAILED')
        
        # Step 3: Generate benchmark metrics table
        from scripts.results.bench_metrics_table import generate_bench_metrics_csv
        
        log_event('RESULTS_BENCH_METRICS_GENERATING')
        if generate_bench_metrics_csv(context.results_dir, context.config):
            log_event('RESULTS_BENCH_METRICS_SUCCESS')
        else:
            log_event('RESULTS_BENCH_METRICS_FAILED')
        
        # Step 4: Merge results tables and export to XLS
        from scripts.results.results_table_merger import merge_results_csvs
        
        log_event('RESULTS_MERGER_START')
        if merge_results_csvs(context.results_dir):
            log_event('RESULTS_MERGER_SUCCESS')
        else:
            log_event('RESULTS_MERGER_FAILED')
        
        log_event('RESULTS_PHASE_COMPLETE')
        return True
    
    except Exception as e:
        log_event('RESULTS_PHASE_EXCEPTION', error_message=str(e))
        import traceback


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