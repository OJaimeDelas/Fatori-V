# =============================================================================
# FATORI-V • Run Controller
# File: run_controller.py
# -----------------------------------------------------------------------------
# Main controller that orchestrates complete FATORI-V workflow execution.
# =============================================================================

from pathlib import Path
from typing import Optional
from scripts.orchestration.run_setup import setup_run
from scripts.orchestration.run_validation import validate_run
from scripts.orchestration.run_context import RunContext
from scripts.orchestration.run_phases import (
    RunPhase,
    PHASE_ORDER,
    PHASE_DESCRIPTIONS,
    get_phase_description
)
from scripts.logging.logger import log_event

class RunController:
    """
    Main controller for FATORI-V workflow execution.
    
    This orchestrates the complete workflow from configuration
    validation through results packaging.
    """
    
    def __init__(self, yaml_path: Path, log_level: str = None, config: dict = None):
        """
        Initialize run controller.
        
        Args:
            yaml_path: Path to configuration YAML file
            log_level: Optional log level override
            config: Optional pre-loaded configuration (for CLI overrides)
        """
        self.yaml_path = Path(yaml_path)
        self.log_level = log_level
        self.config_override = config  # Store for use in setup
        self.context: Optional[RunContext] = None
        
        log_event('CONTROLLER_INITIALIZED', yaml_path=str(yaml_path))
    
    def setup(self) -> RunContext:
        """
        Setup run environment.
        
        This loads configuration, creates results directory,
        and initializes the run context.
        
        Returns:
            RunContext object
        
        Raises:
            ValueError: If setup fails
        """
        log_event('RUN_SETUP_START')
        
        # Run setup (may use pre-loaded config if available)
        if self.config_override:
            # Use pre-loaded config (with CLI overrides already applied)
            config = self.config_override
            # Still need to create results directory
            from scripts.orchestration.run_setup import create_results_directory
            results_dir = create_results_directory(config)
        else:
            # Load config and setup normally
            config, results_dir = setup_run(self.yaml_path, self.log_level)
        
        # Create run context
        context = RunContext(config, results_dir, self.yaml_path)
        
        # Start run state tracking
        context.run_state.start_run()
        
        log_event('RUN_SETUP_COMPLETE')
        
        return context
    
    def run_phase(self, phase_name: str, context: RunContext) -> bool:
        """
        Execute a single phase.
        
        This is a placeholder that will be implemented with actual
        phase execution logic.
        
        Args:
            phase_name: Name of phase to execute
            context: Run context
        
        Returns:
            Boolean indicating if phase succeeded
        """
        log_event('PHASE_START', phase_name=phase_name, description=get_phase_description(phase_name))
        
        # Mark phase as started
        context.run_state.start_phase(phase_name)
        
        try:
            # Phase-specific execution
            success = self._execute_phase(phase_name, context)
            
            if success:
                # Mark phase as complete
                context.run_state.mark_phase_complete(phase_name)
                log_event('PHASE_SUCCESS', phase_name=phase_name)
            else:
                # Mark phase as failed
                error_msg = "Phase execution returned failure"
                context.run_state.mark_phase_failed(phase_name, error_msg)
                log_event('PHASE_FAILED', phase_name=phase_name, error_message=error_msg)           
            
            return success
        
        except Exception as e:
            # Mark phase as failed
            error_msg = str(e)
            context.run_state.mark_phase_failed(phase_name, error_msg)
            log_event('PHASE_EXCEPTION', phase_name=phase_name, error_message=error_msg)

            return False
    
    def _execute_phase(self, phase_name: str, context: RunContext) -> bool:
        """
        Internal method to execute phase-specific logic.
        
        This delegates to phase-specific executor modules.
        
        Args:
            phase_name: Phase to execute
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        # Import phase executors
        from scripts.phases.phase_validation import execute_validation_phase
        from scripts.phases.phase_generation import execute_generation_phase
        from scripts.phases.phase_file_movement import execute_file_movement_phase
        from scripts.phases.phase_build import execute_build_phase
        
        # Validation phase
        if phase_name == RunPhase.VALIDATION:
            return execute_validation_phase(context)
        
        # Generation phase
        elif phase_name == RunPhase.GENERATION:
            return execute_generation_phase(context)
        
        # File movement phase
        elif phase_name == RunPhase.FILE_MOVEMENT:
            return execute_file_movement_phase(context)
        
        # Build phase
        elif phase_name == RunPhase.BUILD:
            return execute_build_phase(context)
        
        # Execution phase
        elif phase_name == RunPhase.EXECUTION:
            from scripts.phases.phase_execution import execute_execution_phase
            return execute_execution_phase(context)
        
        # Results phase
        elif phase_name == RunPhase.RESULTS:
            from scripts.phases.phase_results import execute_results_phase
            return execute_results_phase(context)
        
        else:
            log_event('ERROR_UNKNOWN_PHASE', phase_name=phase_name)
            return False
    
    def execute(self) -> bool:
        """
        Execute complete workflow.
        
        Runs all phases in order. RESULTS phase always runs even if earlier phases fail
        or if user interrupts (Ctrl+C), to ensure cleanup and reporting complete.
        
        Returns:
            Boolean indicating if run succeeded
        """
        try:
            # Setup
            self.context = self.setup()
            
            # Track if any phase failed or was interrupted
            any_phase_failed = False
            failed_phase = None
            interrupted_phase = None
            
            # Execute phases in order
            for phase_name in PHASE_ORDER:
                try:
                    success = self.run_phase(phase_name, self.context)
                    
                    if not success:
                        log_event('RUN_FAILED_AT_PHASE', phase_name=phase_name)
                        any_phase_failed = True
                        if failed_phase is None:
                            failed_phase = phase_name
                        
                        # Continue to RESULTS phase even if earlier phases failed
                        # This ensures metrics aggregation and cleanup happen
                        if phase_name != RunPhase.RESULTS:
                            continue
                        else:
                            # RESULTS phase failed - stop now
                            return False
                
                except KeyboardInterrupt:
                    # User interrupted with Ctrl+C
                    log_event('RUN_INTERRUPTED', phase_name=phase_name)
                    
                    # Mark interrupted phase as failed
                    error_msg = "User interrupt (Ctrl+C)"
                    self.context.run_state.mark_phase_failed(phase_name, error_msg)
                    
                    interrupted_phase = phase_name
                    any_phase_failed = True
                    if failed_phase is None:
                        failed_phase = phase_name
                    
                    # Skip to RESULTS phase unless we're already there
                    if phase_name != RunPhase.RESULTS:
                        log_event('RUN_SKIPPING_TO_RESULTS_AFTER_INTERRUPT')
                        break
                    else:
                        # Interrupted during RESULTS phase
                        return False
            
            # If interrupted before RESULTS, run RESULTS phase now for cleanup
            if interrupted_phase and interrupted_phase != RunPhase.RESULTS:
                log_event('RUN_EXECUTING_RESULTS_AFTER_INTERRUPT')
                try:
                    self.run_phase(RunPhase.RESULTS, self.context)
                except KeyboardInterrupt:
                    # Double Ctrl+C during RESULTS - abort immediately
                    log_event('RUN_DOUBLE_INTERRUPT_ABORTING')
                    return False
                except Exception as e:
                    # RESULTS phase failed but don't crash
                    log_event('ERROR_RESULTS_PHASE_EXCEPTION', error_message=str(e))
            
            # Mark run as complete
            self.context.mark_complete()
            
            if any_phase_failed:
                termination = 'interrupted' if interrupted_phase else 'failed'
                log_event('RUN_COMPLETED_WITH_FAILURES', 
                         first_failed_phase=failed_phase,
                         termination_type=termination)
                return False
            else:
                log_event('RUN_COMPLETED_SUCCESS')
                return True
        
        except KeyboardInterrupt:
            # Ctrl+C during setup - no context yet, just exit
            log_event('RUN_INTERRUPTED_DURING_SETUP')
            return False
        
        except Exception as e:
            # Unexpected exception - try to run RESULTS for cleanup
            log_event('ERROR_RUN_EXCEPTION', error_message=str(e))
            
            if self.context:
                try:
                    log_event('RUN_EXECUTING_RESULTS_AFTER_EXCEPTION')
                    self.run_phase(RunPhase.RESULTS, self.context)
                except Exception:
                    # RESULTS failed too - don't crash further
                    pass
            
            return False
        
        finally:
            # Cleanup
            if self.context:
                self.cleanup(self.context)
    
    def cleanup(self, context: RunContext):
        """
        Perform cleanup after run completes or fails.
        
        Restores architecture/ and benchmarks/ directories from backup,
        ensuring clean state for next run.
        
        Args:
            context: Run context
        """
        log_event('CLEANUP_START')
        
        # Restore architecture and benchmarks from backup
        from scripts.orchestration.arch_restore import restore_architecture_from_backup
        from scripts.build.backup_manager import cleanup_backup_dir
        
        restore_success = restore_architecture_from_backup()
        if restore_success:
            log_event('CLEANUP_ARCH_RESTORED')
            # Clean backup directory after successful restore
            cleanup_backup_dir()
        else:
            log_event('WARNING', warning_message="Architecture restore failed during cleanup")
        
        # Print summary
        summary = context.get_summary()
        log_event('RUN_SUMMARY',
                  results_dir=summary['results_dir'],
                  duration=summary['elapsed_seconds'],
                  completed_phases=len(summary['completed_phases']),
                  total_phases=len(PHASE_ORDER))
        
        if summary['failed_phases']:
            log_event('RUN_SUMMARY_FAILED_PHASES', failed_phases=list(summary['failed_phases'].keys()))
    
    def handle_error(self, error: Exception, context: Optional[RunContext] = None):
        """
        Handle errors during execution.
        
        Args:
            error: Exception that occurred
            context: Optional run context
        """
        log_event('RUN_ERROR', error_message=str(error))
        
        if context:
            log_event('RUN_ERROR_PHASE', phase_name=context.run_state.get_current_phase())
            