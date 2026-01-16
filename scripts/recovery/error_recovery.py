# =============================================================================
# FATORI-V • Error Recovery System
# File: error_recovery.py
# -----------------------------------------------------------------------------
# Provides error recovery strategies and suggestions.
# =============================================================================

import re
from pathlib import Path
from typing import Dict, Optional, List
from scripts.orchestration.run_context import RunContext
from scripts.logging.logger import log_event


class ErrorRecoveryManager:
    """
    Manages error recovery strategies.
    
    Provides suggestions and automatic recovery for common errors.
    """
    
    def __init__(self):
        """Initialize error recovery manager."""
        self.recovery_attempts = {}
        
        log_event('ERROR_RECOVERY_MANAGER_INITIALIZED')
    
    def handle_phase_error(self, phase: str, error: Exception, context: RunContext):
        """
        Handle error in a phase.
        
        Args:
            phase: Phase name where error occurred
            error: Exception that was raised
            context: Run context
        """
        log_event('PHASE_ERROR_HANDLING', phase=phase, error_message=str(error))
        
        # Get suggestions
        suggestions = self.suggest_recovery(phase, error, context)
        
        if suggestions:
            log_event('RECOVERY_SUGGESTIONS_AVAILABLE',
                      phase=phase,
                      suggestion_count=len(suggestions))
            for i, suggestion in enumerate(suggestions, 1):
                log_event('RECOVERY_SUGGESTION', number=i, suggestion=suggestion)
        
        # Try automatic recovery
        if self.attempt_auto_recovery(phase, error, context):
            log_event('AUTO_RECOVERY_SUCCESS', phase=phase)
        else:
            log_event('AUTO_RECOVERY_NOT_AVAILABLE', phase=phase)
    
    def suggest_recovery(self, phase: str, error: Exception, context: RunContext) -> List[str]:
        """
        Generate recovery suggestions based on error.
        
        Args:
            phase: Phase name
            error: Exception
            context: Run context
        
        Returns:
            List of suggestion strings
        """
        suggestions = []
        error_str = str(error).lower()
        
        # Build phase errors
        if phase == "build":
            if "timing" in error_str:
                suggestions.append("Check timing constraints in TCL files")
                suggestions.append("Consider reducing clock frequency")
                suggestions.append("Review critical paths in timing report")
            
            elif "resource" in error_str or "lut" in error_str:
                suggestions.append("Design may be too large for target FPGA")
                suggestions.append("Try disabling some features")
                suggestions.append("Check utilization report for details")
            
            else:
                suggestions.append("Check Vivado logs in build directory")
                suggestions.append("Verify all input files are present")
                suggestions.append("Try running 'make clean' manually")
        
        # Execution phase errors
        elif phase == "execution":
            if "timeout" in error_str:
                suggestions.append("Increase GRAB_TIMEOUT in configuration")
                suggestions.append("Check board connection and power")
                suggestions.append("Verify UART settings match hardware")
            
            elif "device" in error_str or "serial" in error_str:
                suggestions.append("Check board is connected via USB")
                suggestions.append("Verify device path (e.g., /dev/ttyUSB0)")
                suggestions.append("Check user has permissions for serial port")
            
            else:
                suggestions.append("Check console output logs")
                suggestions.append("Verify benchmark programs are valid")
        
        # Generation phase errors
        elif phase == "generation":
            suggestions.append("Check input YAML files exist")
            suggestions.append("Verify system_dict.yaml is valid")
            suggestions.append("Check pblock configuration if using FI")
        
        # Validation phase errors
        elif phase == "validation":
            suggestions.append("Review configuration YAML for errors")
            suggestions.append("Check validation error messages")
            suggestions.append("Refer to configuration documentation")
        
        # File movement phase errors
        elif phase == "file_movement":
            if "permission" in error_str:
                suggestions.append("Check file permissions in architecture directory")
                suggestions.append("Verify user has write access")
            
            suggestions.append("Check architecture directory structure exists")
            suggestions.append("Verify locations.yaml files are present")
        
        # Generic suggestions
        if not suggestions:
            suggestions.append("Check log files for detailed error information")
            suggestions.append("Try running with --log-level DEBUG for more details")
            suggestions.append("Review the results directory for clues")
        
        return suggestions
    
    def attempt_auto_recovery(self, phase: str, error: Exception, context: RunContext) -> bool:
        """
        Attempt automatic error recovery.
        
        Args:
            phase: Phase name
            error: Exception
            context: Run context
        
        Returns:
            Boolean indicating if recovery succeeded
        """
        # Track recovery attempts to avoid loops
        key = f"{phase}:{type(error).__name__}"
        
        if key in self.recovery_attempts:
            log_event('AUTO_RECOVERY_ALREADY_ATTEMPTED', key=key)
            return False
        
        self.recovery_attempts[key] = True
        
        # Implement specific recovery strategies
        error_str = str(error).lower()
        
        # File permission errors - try changing permissions
        if "permission" in error_str:
            log_event('AUTO_RECOVERY_ATTEMPT', strategy='fix_permissions')
            # In a real implementation, might try chmod operations
            return False
        
        # Timeout errors - could try increasing timeout
        if "timeout" in error_str:
            log_event('AUTO_RECOVERY_NOT_POSSIBLE', reason='timeout_error')
            return False
        
        # Most errors cannot be auto-recovered
        return False