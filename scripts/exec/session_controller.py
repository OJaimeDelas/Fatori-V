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
    2. Parallel launch of FI (if enabled) and benchmark
    3. Sync file coordination between processes
    4. Result collection from both processes
    
    The FI console and benchmark run in parallel as separate subprocesses.
    The FI console waits for the sync file (--wait-for-file) before starting injections.
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_info: BenchmarkInfo object
        session_manager: SessionManager instance
        fi_controller: Optional FI controller
    
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
    
    # Initialize session result
    session_result = SessionResult(
        session_id=session.session_id,
        benchmark_name=benchmark_info.name,
        execution_success=False,
        execution_timed_out=False
    )
    
    # Launch FI first if enabled (it will wait for sync file)
    fi_result = None
    fi_process_pid = None
    
    if benchmark_info.injection and fi_controller:
        logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] Launching fault injection subprocess...")
        
        try:
            # Start FI subprocess - it will wait for sync file before injecting
            # This is non-blocking - FI runs in background while benchmark executes
            fi_result = fi_controller.launch_async(
                benchmark_info.name,
                session,
                timeout_s=session.timeout_s
            )
            
            if fi_result is None:
                logger.log_event('ERROR', error_message="[FI-WAIT-DEBUG] FI launch returned None!")
                session_result.fi_launched = False
                session_result.fi_success = False
            else:
                fi_process_pid = fi_result.process.pid
                session_result.fi_launched = True
                logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] FI subprocess started with PID {fi_process_pid}")
        
        except Exception as e:
            logger.log_event('ERROR', error_message=f"[FI-WAIT-DEBUG] Exception during FI launch: {e}")
            import traceback
            logger.log_event('ERROR', error_message=f"Traceback: {traceback.format_exc()}")
            session_result.fi_launched = True
            session_result.fi_success = False
    
    # Execute benchmark (runs in parallel with FI)
    logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] Executing benchmark...")
    exec_result = execute_benchmark(config, benchmark_info, session)
    logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] Benchmark completed with success={exec_result.success}")
    
    # Update session result with benchmark execution status
    session_result.execution_success = exec_result.success
    session_result.execution_timed_out = exec_result.timed_out
    session_result.error_message = exec_result.error_message
    
    # Delete sync file to signal FI to stop gracefully
    # The benchmark has finished, so FI should detect the file is gone and stop
    if benchmark_info.injection and fi_result:
        from scripts.build.path_resolver import resolve_sync_file
        sync_file_path = resolve_sync_file()
        
        if sync_file_path.exists():
            logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] Deleting sync file to signal FI to stop: {sync_file_path}")
            try:
                sync_file_path.unlink()
                logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] Sync file deleted successfully")
            except Exception as e:
                logger.log_event('WARNING', warning_message=f"[FI-WAIT-DEBUG] Could not delete sync file: {e}")
        else:
            logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] Sync file already gone: {sync_file_path}")
    
    # CRITICAL: Wait for FI to complete before moving to next benchmark
    # Both benchmark AND FI must finish before continuing
    if benchmark_info.injection and fi_result:
        logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] BLOCKING: Waiting for FI subprocess (PID {fi_process_pid}) to complete...")
        logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] Current FI process state: poll()={fi_result.process.poll()}")
        
        try:
            # This MUST block until FI subprocess completes
            import time
            wait_start_time = time.time()
            
            fi_completion = fi_controller.wait_for_completion(fi_result)
            
            wait_duration = time.time() - wait_start_time
            logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] FI wait_for_completion returned after {wait_duration:.2f}s")
            logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] FI completion result: success={fi_completion.success}, timed_out={fi_completion.timed_out}, exit_code={fi_completion.exit_code}")
            
            session_result.fi_success = fi_completion.success
            
            if fi_completion.success:
                logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] FI completed successfully: {fi_completion.injection_count} injections")
            elif fi_completion.timed_out:
                logger.log_event('ERROR', error_message=f"[FI-WAIT-DEBUG] FI timed out after {session.timeout_s}s")
            else:
                logger.log_event('ERROR', error_message=f"[FI-WAIT-DEBUG] FI failed: {fi_completion.error_message}")
            
            # Verify FI process actually terminated
            final_poll = fi_result.process.poll()
            logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] After wait, FI process poll()={final_poll}")
            
            if final_poll is None:
                logger.log_event('WARNING', warning_message=f"[FI-WAIT-DEBUG] FI process (PID {fi_process_pid}) still running after wait_for_completion, forcing termination...")
                fi_result.process.terminate()
                try:
                    fi_result.process.wait(timeout=5)
                    logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] FI process terminated successfully")
                except subprocess.TimeoutExpired:
                    logger.log_event('WARNING', warning_message="[FI-WAIT-DEBUG] FI process did not terminate within 5s, sending SIGKILL...")
                    fi_result.process.kill()
                    fi_result.process.wait()
                    logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] FI process killed")
            else:
                logger.log_event('DEBUG', debug_message=f"[FI-WAIT-DEBUG] FI process properly terminated with exit code {final_poll}")
        
        except Exception as e:
            logger.log_event('ERROR', error_message=f"[FI-WAIT-DEBUG] Exception waiting for FI: {e}")
            import traceback
            logger.log_event('ERROR', error_message=f"[FI-WAIT-DEBUG] Traceback: {traceback.format_exc()}")
            session_result.fi_success = False
    elif benchmark_info.injection and not fi_result:
        logger.log_event('ERROR', error_message="[FI-WAIT-DEBUG] FI was enabled but fi_result is None/False - skipping wait")
    else:
        logger.log_event('DEBUG', debug_message="[FI-WAIT-DEBUG] No FI for this benchmark, continuing immediately")
    
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

    # Copy generated files to session gen/ directory
    from scripts.results.directory_manager import create_session_gen_directory
    import shutil
    
    session_gen_dir = create_session_gen_directory(session.session_dir)
    
    # Copy bench_config file from tmp/generated
    bench_config_src = cfg.TMP_GENERATED_DIR / f"bench_config_{benchmark_info.name}.h"
    if bench_config_src.exists():
        bench_config_dest = session_gen_dir / f"bench_config_{benchmark_info.name}.h"
        shutil.copy2(bench_config_src, bench_config_dest)
        logger.log_event('DEBUG', debug_message=f"Copied bench_config to session gen: {bench_config_dest}")
    
    # Move tpool file and cleanup gen/ directory if FI was enabled
    if benchmark_info.injection:
        import shutil
        
        # Move gen/tpool/last_tpool.yaml to session fi/ folder
        gen_tpool_dir = cfg.ROOT_DIR / 'gen' / 'tpool'
        tpool_file = gen_tpool_dir / 'last_tpool.yaml'
        
        if tpool_file.exists():
            session_fi_dir = session.session_dir / 'fi'
            session_fi_dir.mkdir(parents=True, exist_ok=True)
            dest_tpool_file = session_fi_dir / 'last_tpool.yaml'
            
            try:
                shutil.move(str(tpool_file), str(dest_tpool_file))
                logger.log_event('DEBUG', debug_message=f"Moved tpool file to {dest_tpool_file}")
            except Exception as e:
                logger.log_event('WARNING', warning_message=f"Failed to move tpool file: {e}")
        
        # Delete entire gen/ folder in ROOT_DIR
        gen_dir = cfg.ROOT_DIR / 'gen'
        if gen_dir.exists():
            try:
                shutil.rmtree(gen_dir)
                logger.log_event('DEBUG', debug_message=f"Deleted gen/ directory: {gen_dir}")
            except Exception as e:
                logger.log_event('WARNING', warning_message=f"Failed to delete gen/ directory: {e}")
    
    logger.log_event('SESSION_END', session_id=session.session_id, status=status)
    
    return session_result


def run_session_loop(config, benchmark_manager, fi_controller=None, results_dir=None):
    """
    Run execution loop for all enabled benchmarks.
    
    This is the main orchestrator for benchmark execution. It:
    1. Gets execution-ordered list of benchmarks
    2. Creates session manager with run-specific results directory
    3. Executes each benchmark as a session
    4. Collects all results
    5. Reports summary
    
    Args:
        config: The loaded YAML configuration dictionary
        benchmark_manager: BenchmarkManager instance
        fi_controller: Optional FI controller
        results_dir: Run-specific results directory (e.g., results/baseline_example_210126_0037/)
    
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
    
    # Create session manager with run-specific results directory
    session_manager = SessionManager(config, results_dir=results_dir)
    
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