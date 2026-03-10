# =============================================================================
# FATORI-V • Execution • FI Controller
# File: fi_controller.py
# -----------------------------------------------------------------------------
# Central controller for fault injection operations.
# =============================================================================

from typing import Optional
from scripts.exec.fi_command_builder import build_fi_command, get_fi_log_level
from scripts.exec.fi_launcher import launch_fi, FIResult
from scripts.exec.fi_collector import collect_fi_output
from scripts.exec.fi_validator import validate_fi_config
from scripts.common.yaml_io.yaml_helpers import is_fi_enabled_for_benchmark
from scripts.logging.logger import log_event


class FIController:
    """
    Central controller for fault injection operations.
    
    This class provides a unified interface for:
    - Checking if FI is enabled
    - Validating FI configuration
    - Building FI commands
    - Launching FI campaigns
    - Collecting FI output
    """
    
    def __init__(self, config):
        """
        Initialize FI controller with configuration.
        
        Args:
            config: The loaded YAML configuration dictionary
        """
        self.config = config
        self._validation_performed = False
        self._validation_errors = []
        self._validation_warnings = []
        
        log_event('FI_CONTROLLER_INITIALIZED')
    
    def is_fi_enabled(self, benchmark_name):
        """
        Check if fault injection is enabled for a benchmark.
        
        Args:
            benchmark_name: Name of the benchmark
        
        Returns:
            Boolean indicating if FI is enabled
        """
        return is_fi_enabled_for_benchmark(self.config, benchmark_name)
    
    def validate(self):
        """
        Validate FI configuration.
        
        This performs comprehensive validation and caches results.
        Subsequent calls return cached results.
        
        Returns:
            Tuple of (errors: List[str], warnings: List[str])
        """
        if not self._validation_performed:
            self._validation_errors, self._validation_warnings = validate_fi_config(self.config)
            self._validation_performed = True
        
        return self._validation_errors, self._validation_warnings
    
    def has_validation_errors(self):
        """
        Check if validation found any errors.
        
        Returns:
            Boolean indicating if errors exist
        """
        errors, _ = self.validate()
        return len(errors) > 0
    
    def build_command(self, benchmark_name, output_log_path=None):
        """
        Build FI command for a benchmark.
        
        Args:
            benchmark_name: Name of benchmark
            output_log_path: Optional path for output log
        
        Returns:
            String with FI command
        """
        return build_fi_command(self.config, benchmark_name, output_log_path)
    
    def launch(self, benchmark_name, session, timeout_s=None):
        """
        Launch fault injection for a benchmark session.
        
        This is the main entry point for FI execution.
        
        Args:
            benchmark_name: Name of benchmark being executed
            session: Session object
            timeout_s: Optional timeout override
        
        Returns:
            FIResult object
        """
        # Check if FI is enabled
        if not self.is_fi_enabled(benchmark_name):
            log_event('FI_NOT_ENABLED', benchmark_name=benchmark_name)
            return FIResult(
                success=False,
                timed_out=False,
                exit_code=-1,
                error_message="FI not enabled for this benchmark"
            )
        
        # Validate configuration if not done already
        errors, warnings = self.validate()
        
        if errors:
            log_event('FI_LAUNCH_VALIDATION_FAILED', 
                      error_count=len(errors),
                      first_error=errors[0])
            return FIResult(
                success=False,
                timed_out=False,
                exit_code=-1,
                error_message=f"Validation failed: {errors[0]}"
            )
        
        # Launch FI
        return launch_fi(self.config, benchmark_name, session, timeout_s)
    
    def collect_output(self, session):
        """
        Collect FI output from a session.
        
        Args:
            session: Session object
        
        Returns:
            Dictionary with FI output data
        """
        return collect_fi_output(session.session_dir)
    
    def get_log_level(self):
        """
        Get configured FI log level.
        
        Returns:
            String with log level
        """
        return get_fi_log_level(self.config)
    
    def launch_async(self, benchmark_name, session, timeout_s=None):
        """
        Launch fault injection asynchronously for parallel execution with benchmark.
        
        This starts the FI console as a background subprocess that will wait for
        the sync file before beginning injections. The benchmark should be started
        after this call returns.
        
        The FI subprocess waits for: tmp/sync/fatori_benchmark_ready
        
        Workflow:
        1. This method starts FI subprocess (non-blocking)
        2. FI subprocess waits for sync file
        3. Caller starts benchmark (which creates/deletes sync file)
        4. FI subprocess begins injections when sync file appears
        5. Caller uses wait_for_completion() to collect results
        
        Args:
            benchmark_name: Name of benchmark being executed
            session: Session object
            timeout_s: Optional timeout override
        
        Returns:
            FIAsyncHandle object with process handle and metadata,
            or None if FI is not enabled or validation fails
        """
        # Check if FI is enabled
        if not self.is_fi_enabled(benchmark_name):
            log_event('FI_NOT_ENABLED', benchmark_name=benchmark_name)
            return None
        
        # Validate configuration if not done already
        errors, warnings = self.validate()
        
        if errors:
            log_event('FI_LAUNCH_VALIDATION_FAILED', 
                      error_count=len(errors),
                      first_error=errors[0])
            return None
        
        # Import here to avoid circular dependency
        from scripts.exec.fi_launcher import launch_fi_async
        
        # Launch FI asynchronously
        return launch_fi_async(self.config, benchmark_name, session, timeout_s)
    
    def wait_for_completion(self, fi_handle):
        """
        Wait for asynchronously launched FI to complete and collect results.
        
        This blocks until the FI subprocess finishes, then collects
        and returns the FI results.
        
        Args:
            fi_handle: FIAsyncHandle from launch_async()
        
        Returns:
            FIResult object with completion status and statistics
        """
        if fi_handle is None:
            return FIResult(
                success=False,
                timed_out=False,
                exit_code=-1,
                error_message="No FI handle provided"
            )
        
        # Import here to avoid circular dependency
        from scripts.exec.fi_launcher import wait_for_fi_completion
        
        # Wait for FI to complete and get results
        return wait_for_fi_completion(fi_handle)