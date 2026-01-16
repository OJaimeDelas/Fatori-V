# =============================================================================
# FATORI-V • Phase Executor Base
# File: phase_executor.py
# -----------------------------------------------------------------------------
# Base class providing common functionality for all phase executors.
# =============================================================================

from abc import ABC, abstractmethod
from typing import Optional
from scripts.orchestration.run_context import RunContext
from scripts.logging.logger import log_event


class PhaseExecutor(ABC):
    """
    Abstract base class for phase executors.
    
    Provides common functionality for phase execution including
    pre/post execution hooks and error handling.
    """
    
    def __init__(self, phase_name: str):
        """
        Initialize phase executor.
        
        Args:
            phase_name: Name of the phase
        """
        self.phase_name = phase_name
    
    @abstractmethod
    def execute(self, context: RunContext) -> bool:
        """
        Execute the phase logic.
        
        This must be implemented by subclasses.
        
        Args:
            context: Run context with configuration and state
        
        Returns:
            Boolean indicating if phase succeeded
        """
        pass
    
    def pre_execute(self, context: RunContext):
        """
        Hook called before phase execution.
        
        Can be overridden by subclasses for pre-execution setup.
        
        Args:
            context: Run context
        """
        log_event('PHASE_EXECUTOR_PRE', phase_name=self.phase_name)
        
        # Create phase-specific directory
        phase_dir = context.get_phase_dir(self.phase_name)
        log_event('PHASE_DIR_CREATED', phase_dir=str(phase_dir))
    
    def post_execute(self, context: RunContext, success: bool):
        """
        Hook called after phase execution.
        
        Can be overridden by subclasses for post-execution cleanup.
        
        Args:
            context: Run context
            success: Whether phase execution succeeded
        """
        if success:
            log_event('PHASE_EXECUTOR_SUCCESS', phase_name=self.phase_name)
        else:
            log_event('PHASE_EXECUTOR_FAILED', phase_name=self.phase_name)
    
    def handle_error(self, error: Exception, context: RunContext) -> Optional[str]:
        """
        Handle errors during phase execution.
        
        Can be overridden by subclasses for custom error handling.
        
        Args:
            error: Exception that occurred
            context: Run context
        
        Returns:
            Error message string, or None to use default
        """
        log_event('PHASE_EXECUTOR_ERROR', 
                  phase_name=self.phase_name,
                  error_message=str(error))
        return str(error)
    
    def run(self, context: RunContext) -> bool:
        """
        Main entry point for phase execution with hooks.
        
        This wraps the execute() method with pre/post hooks and
        error handling.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating if phase succeeded
        """
        try:
            # Pre-execution hook
            self.pre_execute(context)
            
            # Execute phase logic
            success = self.execute(context)
            
            # Post-execution hook
            self.post_execute(context, success)
            
            return success
        
        except Exception as e:
            # Handle error
            error_msg = self.handle_error(e, context)
            if error_msg:
                context.run_state.mark_phase_failed(self.phase_name, error_msg)
            
            return False