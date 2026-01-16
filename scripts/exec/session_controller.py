# =============================================================================
# FATORI-V • Execution • Session Controller
# File: session_controller.py
# -----------------------------------------------------------------------------
# Orchestrates execution loop across all enabled benchmarks with session management.
# =============================================================================

from dataclasses import dataclass
from typing import List, Optional
import fatori_settings as cfg
from scripts.exec.session_manager import SessionManager
from scripts.exec.benchmark_executor import execute_benchmark
from scripts.exec.sync_file_manager import wait_for_sync_file_deletion, cleanup_sync_file
from scripts.build.path_resolver import resolve_sync_file
from scripts.logging import logger


@dataclass
class SessionResult:
    """
    Result from a complete session (benchmark + FI if enabled).
    """
    session_id: int
    benchmark_name: str
    execution_success: bool
    execution_timed_out: bool
    fi_success: Optional[bool] = None    # None if FI not enabled
    fi_launched: bool = False             # Whether FI was actually launched
    error_message: Optional[str] = None
    
    def __str__(self):
        status = "success" if self.execution_success else "failed"
        fi_str = ""
        if self.fi_launched:
            fi_status = "success" if self.fi_success else "failed"
            fi_str = f", FI: {fi_status}"
        
        return f"Session {self.session_id} ({self.benchmark_name}): {status}{fi_str}"


def execute_session(config, benchmark_info, session_manager, fi_controller=None):
    """
    Execute a complete session for one benchmark.
    
    This handles:
    1. Session creation
    2. Benchmark execution
    3. Sync file coordination (if FI enabled)
    4. FI launch (if enabled and sync file deleted)
    5. Result collection
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_info: BenchmarkInfo object
        session_manager: SessionManager instance
        fi_controller: Optional FI controller (Phase 12)
    
    Returns:
        SessionResult object
    """
    # Create session
    session = session_manager.create_session(
        benchmark_name=benchmark_info.name,
        injection_enabled=benchmark_info.injection,
        timeout_s=benchmark_info.timeout_s
    )
    
    # Start session
    session_manager.start_session(session)
    
    logger.log_event('SESSION_START', session_id=session.session_id, benchmark=benchmark_info.name)
    
    # Execute benchmark
    logger.log_event('DEBUG', debug_message="Executing benchmark...")
    exec_result = execute_benchmark(config, benchmark_info, session)
    
    # Initialize session result
    session_result = SessionResult(
        session_id=session.session_id,
        benchmark_name=benchmark_info.name,
        execution_success=exec_result.success,
        execution_timed_out=exec_result.timed_out,
        error_message=exec_result.error_message
    )
    
    # Handle FI if enabled and benchmark succeeded
    if benchmark_info.injection and exec_result.success:
        logger.log_event('DEBUG', debug_message="Fault injection is enabled for this benchmark")
        
        # Get sync file path
        sync_path = resolve_sync_file()
        
        # Wait for sync file deletion (benchmark signals FI can begin)
        logger.log_event('DEBUG', debug_message="Waiting for benchmark to signal FI readiness...")
        sync_deleted = wait_for_sync_file_deletion(
            sync_path,
            timeout_s=60  # Give benchmark 60s to signal
        )
        
        if sync_deleted:
            logger.log_event('DEBUG', debug_message="Benchmark ready for FI")
            
            # Launch FI if controller is available
            if fi_controller:
                logger.log_event('DEBUG', debug_message="Launching fault injection...")
                
                try:
                    # Launch FI via controller
                    fi_result = fi_controller.launch(
                        benchmark_info.name,
                        session,
                        timeout_s=session.timeout_s
                    )
                    
                    session_result.fi_launched = True
                    session_result.fi_success = fi_result.success
                    
                    if fi_result.success:
                        logger.log_event('DEBUG', debug_message=f"FI completed: {fi_result.injection_count} injections")
                    else:
                        logger.log_event('ERROR', error_message=f"FI failed: {fi_result.error_message}")
                
                except Exception as e:
                    logger.log_event('ERROR', error_message=f"Exception during FI launch: {e}")
                    session_result.fi_launched = True
                    session_result.fi_success = False
            else:
                logger.log_event('WARNING', warning_message="FI controller not available, skipping FI launch")
                session_result.fi_launched = False
        else:
            logger.log_event('WARNING', warning_message="Sync file not deleted - benchmark may have failed initialization")
            session_result.fi_launched = False
            session_result.fi_success = False
        
        # Cleanup sync file
        cleanup_sync_file(sync_path)
    
    # Complete session
    if exec_result.success:
        if benchmark_info.injection and not session_result.fi_success:
            status = "failed"  # FI part failed
        else:
            status = "success"
    elif exec_result.timed_out:
        status = "timeout"
    else:
        status = "failed"
    
    session_manager.complete_session(session, status=status)
    
    # Save session info
    session_info = {
        'execution_result': {
            'success': exec_result.success,
            'timed_out': exec_result.timed_out,
            'exit_code': exec_result.exit_code,
            'metrics': exec_result.metrics,
        },
        'fi_launched': session_result.fi_launched,
        'fi_success': session_result.fi_success,
    }
    
    session_manager.save_session_info(session, session_info)
    
    logger.log_event('SESSION_END', session_id=session.session_id, status=status)
    
    return session_result


def run_session_loop(config, benchmark_manager, fi_controller=None):
    """
    Run execution loop for all enabled benchmarks.
    
    This is the main orchestrator for benchmark execution. It:
    1. Gets execution-ordered list of benchmarks
    2. Creates session manager
    3. Executes each benchmark as a session
    4. Collects all results
    5. Reports summary
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_manager: BenchmarkManager instance
        fi_controller: Optional FI controller (Phase 12)
    
    Returns:
        List of SessionResult objects
    """
    logger.log_event('EXECUTION_LOOP_START')
    
    # Get benchmarks to execute
    benchmarks = benchmark_manager.get_execution_order()
    
    if not benchmarks:
        logger.log_event('WARNING', warning_message="No benchmarks enabled for execution")
        return []
    
    logger.log_event('DEBUG', debug_message=f"Executing {len(benchmarks)} benchmark(s):")
    for i, bench in enumerate(benchmarks, 1):
        logger.log_event('DEBUG', debug_message=f"  {i}. {bench.name} (timeout: {bench.timeout_s}s, FI: {bench.injection})")
    
    # Create session manager
    session_manager = SessionManager(config)
    
    # Execute each benchmark
    results = []
    
    for i, benchmark_info in enumerate(benchmarks, 1):
        logger.log_event('DEBUG', debug_message=f"BENCHMARK {i}/{len(benchmarks)}: {benchmark_info.name}")
        
        try:
            # Execute session
            session_result = execute_session(
                config,
                benchmark_info,
                session_manager,
                fi_controller
            )
            
            results.append(session_result)
        
        except Exception as e:
            logger.log_event('ERROR', error_message=f"Exception during session execution: {e}")
            
            # Create failed result
            failed_result = SessionResult(
                session_id=-1,
                benchmark_name=benchmark_info.name,
                execution_success=False,
                execution_timed_out=False,
                error_message=str(e)
            )
            
            results.append(failed_result)
    
    # Print summary
    print_execution_summary(results)
    
    return results


def print_execution_summary(results):
    """
    Print summary of execution loop results.
    
    Args:
        results: List of SessionResult objects
    """
    if not results:
        logger.log_event('EXECUTION_LOOP_END', session_count=0)
        return
    
    # Count outcomes
    success_count = sum(1 for r in results if r.execution_success)
    failed_count = sum(1 for r in results if not r.execution_success)
    timeout_count = sum(1 for r in results if r.execution_timed_out)
    fi_count = sum(1 for r in results if r.fi_launched)
    fi_success_count = sum(1 for r in results if r.fi_launched and r.fi_success)
    
    logger.log_event('EXECUTION_LOOP_END', 
                     session_count=len(results),
                     success_count=success_count,
                     failed_count=failed_count,
                     timeout_count=timeout_count,
                     fi_count=fi_count,
                     fi_success_count=fi_success_count)