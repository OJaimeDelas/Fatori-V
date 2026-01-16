# =============================================================================
# FATORI-V • Configuration • Log Levels
# File: log_levels.py
# -----------------------------------------------------------------------------
# Event enable/disable configuration for each log level.
# User-editable: Change True/False values to control output per level.
# =============================================================================

# =============================================================================
# MINIMAL - Only essential run lifecycle and errors
# =============================================================================

MINIMAL = {
    # Run lifecycle
    'RUN_START': {'console': True, 'file': True},
    'RUN_END': {'console': True, 'file': True},
    'RUN_FAILED': {'console': True, 'file': True},
    'RUN_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_GENERAL': {'console': True, 'file': True},
    'RUN_COMPLETED_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_AT_PHASE': {'console': True, 'file': True},
    'RUN_INTERRUPTED': {'console': True, 'file': True},
    'RUN_SETUP_START': {'console': False, 'file': False},
    'RUN_SETUP_COMPLETE': {'console': False, 'file': False},
    'FATORI_START': {'console': True, 'file': True},
    'FATORI_END': {'console': True, 'file': True},
    
    # Phase lifecycle
    'PHASE_START': {'console': True, 'file': True},
    'PHASE_END': {'console': True, 'file': True},
    'PHASE_FAILED': {'console': True, 'file': True},
    'PHASE_SUCCESS': {'console': False, 'file': False},
    'PHASE_EXCEPTION': {'console': True, 'file': True},
    
    # Validation
    'VALIDATION_START': {'console': False, 'file': False},
    'VALIDATION_END': {'console': False, 'file': False},
    'VALIDATION_ERROR': {'console': True, 'file': True},
    'VALIDATION_WARNING': {'console': False, 'file': False},
    'VALIDATION_ERROR_MISSING_FIELD': {'console': True, 'file': True},
    'VALIDATION_ERROR_INVALID_VALUE': {'console': True, 'file': True},
    'VALIDATION_WARNING_DEPRECATED': {'console': False, 'file': False},
    'VALIDATION_AUTO_CORRECTION': {'console': False, 'file': False},
    'VALIDATION_COMPLETE_NO_ISSUES': {'console': False, 'file': False},
    'VALIDATION_PHASE_EXECUTING': {'console': False, 'file': False},
    'VALIDATION_PHASE_PASSED': {'console': False, 'file': False},
    'VALIDATION_PHASE_FAILED': {'console': True, 'file': True},
    'VALIDATION_PHASE_WARNINGS': {'console': False, 'file': False},
    'VALIDATION_PHASE_EXECUTING': {'console': False, 'file': False},
    'VALIDATION_PHASE_PASSED': {'console': False, 'file': False},
    'VALIDATION_PHASE_WARNINGS': {'console': False, 'file': False},
    
    'DRY_RUN_MODE_ENABLED': {'console': True, 'file': True},
    'DRY_RUN_COMMAND': {'console': True, 'file': True},

    # Generation
    'GENERATION_PHASE_EXECUTING': {'console': False, 'file': False},
    'GENERATION_PHASE_COMPLETE': {'console': False, 'file': False},
    'GENERATION_START': {'console': False, 'file': False},
    'GENERATION_END': {'console': False, 'file': False},
    'FILE_GENERATED': {'console': False, 'file': False},
    'SVH_GENERATION': {'console': False, 'file': False},
    'TCL_GENERATION': {'console': False, 'file': False},
    'FEATURES_GENERATION_START': {'console': False, 'file': False},
    'FEATURES_GENERATION_END': {'console': False, 'file': False},
    'FTM_GENERATION_START': {'console': False, 'file': False},
    'FTM_GENERATION_END': {'console': False, 'file': False},
    'GENERATION_PHASE_ERROR': {'console': True, 'file': True},
    'GENERATION_PHASE_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_MASTER_START': {'console': False, 'file': False},
    'GENERATION_STEP1_START': {'console': False, 'file': False},
    'GENERATION_STEP2_START': {'console': False, 'file': False},
    'GENERATION_STEP3_START': {'console': False, 'file': False},
    'GENERATION_STEP4_START': {'console': False, 'file': False},
    'GENERATION_VALIDATION_SUCCESS': {'console': False, 'file': False},
    'ERROR_GENERATION_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_SVH_COMPLETE': {'console': False, 'file': False},
    'GENERATION_PBLOCK_TCL_COMPLETE': {'console': False, 'file': False},
    'GENERATION_SYSTEM_DICT_START': {'console': False, 'file': False},
    'GENERATION_METRICS_CONFIG_START': {'console': False, 'file': False},
    'GENERATION_SYSTEM_INTEGRATION_COMPLETE': {'console': False, 'file': False},
    'GENERATION_COMPLETE': {'console': False, 'file': False},
    
    # File movement
    'FILE_MOVEMENT_START': {'console': False, 'file': False},
    'FILE_MOVEMENT_END': {'console': False, 'file': False},
    'FILE_ALLOCATED': {'console': False, 'file': False},
    'FILE_BACKUP': {'console': False, 'file': False},
    'FILE_COPY': {'console': False, 'file': False},
    'FILE_MOVEMENT_PHASE_EXECUTING': {'console': False, 'file': False},
    'FILE_MOVEMENT_COMPLETE': {'console': False, 'file': False},
    'FILE_MOVEMENT_NO_FILES': {'console': True, 'file': True},
    'FILE_MOVEMENT_ERROR': {'console': True, 'file': True},
    'TCL_INPUTS_COPIED': {'console': False, 'file': False},
    
    # Build
    'BUILD_START': {'console': False, 'file': False},
    'BUILD_END': {'console': False, 'file': False},
    'BUILD_STEP': {'console': False, 'file': False},
    'BUILD_ERROR': {'console': True, 'file': True},
    'BUILD_VIVADO_SYNTHESIS_START': {'console': False, 'file': False},
    'BUILD_VIVADO_IMPLEMENTATION_START': {'console': False, 'file': False},
    'BUILD_BITSTREAM_START': {'console': False, 'file': False},
    'MAKE_COMMAND_EXECUTING': {'console': False, 'file': False},
    'MAKE_COMMAND_SUCCESS': {'console': False, 'file': False},
    'MAKE_COMMAND_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_VIVADO_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_MAKE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXECUTING': {'console': False, 'file': False},
    'BUILD_PHASE_CONFIG': {'console': False, 'file': False},
    'BUILD_PHASE_SUCCESS': {'console': False, 'file': False},
    'BUILD_PHASE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXCEPTION': {'console': True, 'file': True},
    'BUILD_ERRORS_SUMMARY': {'console': True, 'file': True},
    'BUILD_LOG_LOCATION': {'console': True, 'file': True},
    'BUILD_BITSTREAM_READY': {'console': False, 'file': False},
    
    # Execution
    'EXECUTION_START': {'console': False, 'file': False},
    'EXECUTION_END': {'console': False, 'file': False},
    'BENCHMARK_START': {'console': False, 'file': False},
    'BENCHMARK_END': {'console': False, 'file': False},
    'BENCHMARK_OUTPUT': {'console': False, 'file': False},
    'BENCHMARK_ERROR': {'console': True, 'file': True},
    'BENCHMARK_TIMEOUT': {'console': True, 'file': True},
    'SESSION_START': {'console': False, 'file': False},
    'SESSION_COMPLETE': {'console': False, 'file': False},
    'SESSION_FAILED': {'console': True, 'file': True},
    'BENCHMARK_DISCOVERY': {'console': False, 'file': False},
    'FI_LAUNCH': {'console': False, 'file': False},
    'FI_COMPLETE': {'console': False, 'file': False},
    'FI_ERROR': {'console': True, 'file': True},
    'CONSOLE_OUTPUT': {'console': False, 'file': False},
    'EXECUTION_PHASE_START': {'console': False, 'file': False},
    'BENCHMARKS_DISCOVERING': {'console': False, 'file': False},
    'BENCHMARKS_DISCOVERED': {'console': False, 'file': False},
    'BENCHMARKS_VALIDATION_FAILED': {'console': True, 'file': True},
    'BENCHMARKS_VALIDATION_WARNINGS': {'console': False, 'file': False},
    'BENCHMARKS_NONE_ENABLED': {'console': True, 'file': True},
    'FI_ENABLED': {'console': False, 'file': False},
    'FI_DISABLED': {'console': False, 'file': False},
    'FI_VALIDATION_FAILED': {'console': True, 'file': True},
    'FI_VALIDATION_WARNINGS': {'console': False, 'file': False},
    'BENCHMARKS_EXECUTION_START': {'console': False, 'file': False},
    'EXECUTION_NO_RESULTS': {'console': True, 'file': True},
    'EXECUTION_SUMMARY': {'console': False, 'file': False},
    'EXECUTION_ALL_FAILED': {'console': True, 'file': True},
    'EXECUTION_PHASE_COMPLETE': {'console': False, 'file': False},
    'EXECUTION_PHASE_EXCEPTION': {'console': True, 'file': True},
    'EXECUTION_TRACEBACK': {'console': True, 'file': True},
    'EXECUTION_DATA_READY': {'console': False, 'file': False},
    
    # Pblocks
    'PBLOCK_CONFIG_CREATED': {'console': False, 'file': False},
    'PBLOCK_GENERATION_START': {'console': False, 'file': False},
    'PBLOCK_GENERATION_END': {'console': False, 'file': False},
    'PBLOCK_GENERATION_COMPLETE': {'console': False, 'file': False},
    'PBLOCK_MODULE_PROCESSED': {'console': False, 'file': False},
    'PBLOCK_TCL_GENERATED': {'console': False, 'file': False},
    
    # Results
    'RESULTS_START': {'console': False, 'file': False},
    'RESULTS_END': {'console': False, 'file': False},
    'RESULTS_SUMMARY': {'console': True, 'file': True},
    'RESULTS_FILE_CREATED': {'console': False, 'file': False},
    'RESULTS_METRICS_COLLECTED': {'console': False, 'file': False},
    
    # Parser
    'PARSER_START': {'console': False, 'file': False},
    'PARSER_REPORT_PARSED': {'console': False, 'file': False},
    'PARSER_COMPLETE': {'console': False, 'file': False},
    'PARSER_ERROR_REPORT_MISSING': {'console': True, 'file': True},
    'PARSER_ERROR_PARSE_FAILED': {'console': True, 'file': True},
    'PARSER_METRICS_EXTRACTED': {'console': False, 'file': False},
    
    # CLI/UI
    'CLI_DRY_RUN_START': {'console': False, 'file': False},
    'CLI_CONFIG_SUMMARY': {'console': False, 'file': False},
    'CLI_FILES_TO_GENERATE': {'console': False, 'file': False},
    'CLI_BANNER': {'console': False, 'file': False},
    'CLI_OVERRIDE_APPLIED': {'console': False, 'file': False},
    
    # Override system
    'OVERRIDE_START': {'console': False, 'file': False},
    'OVERRIDE_APPLIED': {'console': False, 'file': False},
    'OVERRIDE_VALIDATION': {'console': False, 'file': False},
    
    # Recovery
    'RECOVERY_STATE_SAVED': {'console': False, 'file': False},
    'RECOVERY_STATE_LOADED': {'console': False, 'file': False},
    'RECOVERY_RESUME_START': {'console': False, 'file': False},
    
    # Mapping
    'MAPPING_BOARD': {'console': False, 'file': False},
    'MAPPING_ISA': {'console': False, 'file': False},
    
    # Cleanup
    'CLEANUP_START': {'console': False, 'file': False},
    'CLEANUP_END': {'console': False, 'file': False},
    'CLEANUP_TMP_DIR': {'console': False, 'file': False},
    
    # Setup
    'SETUP_START': {'console': False, 'file': False},
    'SETUP_END': {'console': False, 'file': False},
    'SETUP_DIRECTORIES': {'console': False, 'file': False},
    'SETUP_LOGGING': {'console': False, 'file': False},
    'SETUP_ENVIRONMENT_CHECK': {'console': False, 'file': False},
    
    # System/Environment
    'ENVIRONMENT_VALIDATION_START': {'console': False, 'file': False},
    'ENVIRONMENT_VALIDATION_END': {'console': False, 'file': False},
    'DIRECTORY_CREATED': {'console': False, 'file': False},
    'CONFIG_LOADED': {'console': False, 'file': False},
    
    # Multi-run
    'MULTI_RUN_START': {'console': False, 'file': False},
    'MULTI_RUN_PROGRESS': {'console': False, 'file': False},
    'MULTI_RUN_END': {'console': False, 'file': False},
    
    # Errors and warnings
    'ERROR': {'console': True, 'file': True},
    'ERROR_FATAL': {'console': True, 'file': True},
    'ERROR_RECOVERABLE': {'console': True, 'file': True},
    'ERROR_FILE_NOT_FOUND': {'console': True, 'file': True},
    'ERROR_PERMISSION_DENIED': {'console': True, 'file': True},
    'ERROR_INVALID_CONFIG': {'console': True, 'file': True},
    'ERROR_IMPORT_FAILED': {'console': True, 'file': True},
    'WARNING': {'console': False, 'file': False},
    'INFO': {'console': False, 'file': False},
    'DEBUG': {'console': False, 'file': False},
}

# =============================================================================
# NORMAL - Standard operation (default)
# =============================================================================

NORMAL = {
    # Run lifecycle
    'RUN_START': {'console': True, 'file': True},
    'RUN_END': {'console': True, 'file': True},
    'RUN_FAILED': {'console': True, 'file': True},
    'RUN_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_GENERAL': {'console': True, 'file': True},
    'RUN_COMPLETED_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_AT_PHASE': {'console': True, 'file': True},
    'RUN_INTERRUPTED': {'console': True, 'file': True},
    'RUN_SETUP_START': {'console': True, 'file': True},
    'RUN_SETUP_COMPLETE': {'console': True, 'file': True},
    'FATORI_START': {'console': True, 'file': True},
    'FATORI_END': {'console': True, 'file': True},
    
    # Phase lifecycle
    'PHASE_START': {'console': True, 'file': True},
    'PHASE_END': {'console': True, 'file': True},
    'PHASE_FAILED': {'console': True, 'file': True},
    'PHASE_SUCCESS': {'console': True, 'file': True},
    'PHASE_EXCEPTION': {'console': True, 'file': True},
    
    # Validation
    'VALIDATION_START': {'console': True, 'file': True},
    'VALIDATION_END': {'console': True, 'file': True},
    'VALIDATION_ERROR': {'console': True, 'file': True},
    'VALIDATION_WARNING': {'console': True, 'file': True},
    'VALIDATION_ERROR_MISSING_FIELD': {'console': True, 'file': True},
    'VALIDATION_ERROR_INVALID_VALUE': {'console': True, 'file': True},
    'VALIDATION_WARNING_DEPRECATED': {'console': True, 'file': True},
    'VALIDATION_AUTO_CORRECTION': {'console': False, 'file': False},
    'VALIDATION_COMPLETE_NO_ISSUES': {'console': False, 'file': False},
    'VALIDATION_PHASE_EXECUTING': {'console': True, 'file': True},
    'VALIDATION_PHASE_PASSED': {'console': True, 'file': True},
    'VALIDATION_PHASE_FAILED': {'console': True, 'file': True},
    'VALIDATION_PHASE_WARNINGS': {'console': True, 'file': True},
    'VALIDATION_PHASE_EXECUTING': {'console': True, 'file': True},
    'VALIDATION_PHASE_PASSED': {'console': True, 'file': True},
    'VALIDATION_PHASE_WARNINGS': {'console': True, 'file': True},
    
    'DRY_RUN_MODE_ENABLED': {'console': True, 'file': True},
    'DRY_RUN_COMMAND': {'console': True, 'file': True},

    # Generation
    'GENERATION_START': {'console': True, 'file': True},
    'GENERATION_END': {'console': True, 'file': True},
    'FILE_GENERATED': {'console': False, 'file': True},
    'SVH_GENERATION': {'console': False, 'file': True},
    'TCL_GENERATION': {'console': False, 'file': True},
    'FEATURES_GENERATION_START': {'console': True, 'file': True},
    'FEATURES_GENERATION_END': {'console': True, 'file': True},
    'FTM_GENERATION_START': {'console': True, 'file': True},
    'FTM_GENERATION_END': {'console': True, 'file': True},
    'GENERATION_PHASE_ERROR': {'console': True, 'file': True},
    'GENERATION_PHASE_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_MASTER_START': {'console': True, 'file': True},
    'GENERATION_STEP1_START': {'console': True, 'file': True},
    'GENERATION_STEP2_START': {'console': True, 'file': True},
    'GENERATION_STEP3_START': {'console': True, 'file': True},
    'GENERATION_STEP4_START': {'console': True, 'file': True},
    'GENERATION_VALIDATION_SUCCESS': {'console': True, 'file': True},
    'ERROR_GENERATION_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_SVH_COMPLETE': {'console': True, 'file': True},
    'GENERATION_PBLOCK_TCL_COMPLETE': {'console': True, 'file': True},
    'GENERATION_SYSTEM_DICT_START': {'console': True, 'file': True},
    'GENERATION_METRICS_CONFIG_START': {'console': True, 'file': True},
    'GENERATION_SYSTEM_INTEGRATION_COMPLETE': {'console': True, 'file': True},
    'GENERATION_COMPLETE': {'console': True, 'file': True},
    
    # File movement
    'FILE_MOVEMENT_START': {'console': True, 'file': True},
    'FILE_MOVEMENT_END': {'console': True, 'file': True},
    'FILE_ALLOCATED': {'console': False, 'file': True},
    'FILE_BACKUP': {'console': False, 'file': True},
    'FILE_COPY': {'console': False, 'file': True},
    'FILE_MOVEMENT_PHASE_EXECUTING': {'console': True, 'file': True},
    'FILE_MOVEMENT_COMPLETE': {'console': True, 'file': True},
    'FILE_MOVEMENT_NO_FILES': {'console': True, 'file': True},
    'FILE_MOVEMENT_ERROR': {'console': True, 'file': True},
    'TCL_INPUTS_COPIED': {'console': True, 'file': True},
    
    # Build
    'BUILD_START': {'console': True, 'file': True},
    'BUILD_END': {'console': True, 'file': True},
    'BUILD_STEP': {'console': True, 'file': True},
    'BUILD_ERROR': {'console': True, 'file': True},
    'BUILD_VIVADO_SYNTHESIS_START': {'console': True, 'file': True},
    'BUILD_VIVADO_IMPLEMENTATION_START': {'console': True, 'file': True},
    'BUILD_BITSTREAM_START': {'console': True, 'file': True},
    'MAKE_COMMAND_EXECUTING': {'console': True, 'file': True},
    'MAKE_COMMAND_SUCCESS': {'console': True, 'file': True},
    'MAKE_COMMAND_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_VIVADO_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_MAKE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXECUTING': {'console': True, 'file': True},
    'BUILD_PHASE_CONFIG': {'console': True, 'file': True},
    'BUILD_PHASE_SUCCESS': {'console': True, 'file': True},
    'BUILD_PHASE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXCEPTION': {'console': True, 'file': True},
    'BUILD_ERRORS_SUMMARY': {'console': True, 'file': True},
    'BUILD_LOG_LOCATION': {'console': True, 'file': True},
    'BUILD_BITSTREAM_READY': {'console': True, 'file': True},
    
    # Execution
    'EXECUTION_START': {'console': True, 'file': True},
    'EXECUTION_END': {'console': True, 'file': True},
    'BENCHMARK_START': {'console': True, 'file': True},
    'BENCHMARK_END': {'console': True, 'file': True},
    'BENCHMARK_OUTPUT': {'console': False, 'file': True},
    'BENCHMARK_ERROR': {'console': True, 'file': True},
    'BENCHMARK_TIMEOUT': {'console': True, 'file': True},
    'SESSION_START': {'console': True, 'file': True},
    'SESSION_COMPLETE': {'console': True, 'file': True},
    'SESSION_FAILED': {'console': True, 'file': True},
    'BENCHMARK_DISCOVERY': {'console': True, 'file': True},
    'FI_LAUNCH': {'console': True, 'file': True},
    'FI_COMPLETE': {'console': True, 'file': True},
    'FI_ERROR': {'console': True, 'file': True},
    'CONSOLE_OUTPUT': {'console': False, 'file': True},
    'EXECUTION_PHASE_START': {'console': True, 'file': True},
    'BENCHMARKS_DISCOVERING': {'console': True, 'file': True},
    'BENCHMARKS_DISCOVERED': {'console': True, 'file': True},
    'BENCHMARKS_VALIDATION_FAILED': {'console': True, 'file': True},
    'BENCHMARKS_VALIDATION_WARNINGS': {'console': True, 'file': True},
    'BENCHMARKS_NONE_ENABLED': {'console': True, 'file': True},
    'FI_ENABLED': {'console': True, 'file': True},
    'FI_DISABLED': {'console': True, 'file': True},
    'FI_VALIDATION_FAILED': {'console': True, 'file': True},
    'FI_VALIDATION_WARNINGS': {'console': True, 'file': True},
    'BENCHMARKS_EXECUTION_START': {'console': True, 'file': True},
    'EXECUTION_NO_RESULTS': {'console': True, 'file': True},
    'EXECUTION_SUMMARY': {'console': True, 'file': True},
    'EXECUTION_ALL_FAILED': {'console': True, 'file': True},
    'EXECUTION_PHASE_COMPLETE': {'console': True, 'file': True},
    'EXECUTION_PHASE_EXCEPTION': {'console': True, 'file': True},
    'EXECUTION_TRACEBACK': {'console': True, 'file': True},
    'EXECUTION_DATA_READY': {'console': True, 'file': True},
    
    # Pblocks
    'PBLOCK_CONFIG_CREATED': {'console': True, 'file': True},
    'PBLOCK_GENERATION_START': {'console': True, 'file': True},
    'PBLOCK_GENERATION_END': {'console': True, 'file': True},
    'PBLOCK_GENERATION_COMPLETE': {'console': True, 'file': True},
    'PBLOCK_MODULE_PROCESSED': {'console': False, 'file': True},
    'PBLOCK_TCL_GENERATED': {'console': True, 'file': True},
    
    # Results
    'RESULTS_START': {'console': True, 'file': True},
    'RESULTS_END': {'console': True, 'file': True},
    'RESULTS_SUMMARY': {'console': True, 'file': True},
    'RESULTS_FILE_CREATED': {'console': True, 'file': True},
    'RESULTS_METRICS_COLLECTED': {'console': True, 'file': True},
    
    # Parser
    'PARSER_START': {'console': True, 'file': True},
    'PARSER_REPORT_PARSED': {'console': True, 'file': True},
    'PARSER_COMPLETE': {'console': True, 'file': True},
    'PARSER_ERROR_REPORT_MISSING': {'console': True, 'file': True},
    'PARSER_ERROR_PARSE_FAILED': {'console': True, 'file': True},
    'PARSER_METRICS_EXTRACTED': {'console': True, 'file': True},
    
    # CLI/UI
    'CLI_DRY_RUN_START': {'console': True, 'file': True},
    'CLI_CONFIG_SUMMARY': {'console': True, 'file': True},
    'CLI_FILES_TO_GENERATE': {'console': True, 'file': True},
    'CLI_BANNER': {'console': True, 'file': True},
    'CLI_OVERRIDE_APPLIED': {'console': True, 'file': True},
    
    # Override system
    'OVERRIDE_START': {'console': True, 'file': True},
    'OVERRIDE_APPLIED': {'console': True, 'file': True},
    'OVERRIDE_VALIDATION': {'console': True, 'file': True},
    
    # Recovery
    'RECOVERY_STATE_SAVED': {'console': True, 'file': True},
    'RECOVERY_STATE_LOADED': {'console': True, 'file': True},
    'RECOVERY_RESUME_START': {'console': True, 'file': True},
    
    # Mapping
    'MAPPING_BOARD': {'console': False, 'file': True},
    'MAPPING_ISA': {'console': False, 'file': True},
    
    # Cleanup
    'CLEANUP_START': {'console': True, 'file': True},
    'CLEANUP_END': {'console': True, 'file': True},
    'CLEANUP_TMP_DIR': {'console': False, 'file': True},
    
    # Setup
    'SETUP_START': {'console': True, 'file': True},
    'SETUP_END': {'console': True, 'file': True},
    'SETUP_DIRECTORIES': {'console': False, 'file': True},
    'SETUP_LOGGING': {'console': True, 'file': True},
    'SETUP_ENVIRONMENT_CHECK': {'console': True, 'file': True},
    
    # System/Environment
    'ENVIRONMENT_VALIDATION_START': {'console': True, 'file': True},
    'ENVIRONMENT_VALIDATION_END': {'console': True, 'file': True},
    'DIRECTORY_CREATED': {'console': False, 'file': True},
    'CONFIG_LOADED': {'console': True, 'file': True},
    
    # Multi-run
    'MULTI_RUN_START': {'console': True, 'file': True},
    'MULTI_RUN_PROGRESS': {'console': True, 'file': True},
    'MULTI_RUN_END': {'console': True, 'file': True},
    
    # Errors and warnings
    'ERROR': {'console': True, 'file': True},
    'ERROR_FATAL': {'console': True, 'file': True},
    'ERROR_RECOVERABLE': {'console': True, 'file': True},
    'ERROR_FILE_NOT_FOUND': {'console': True, 'file': True},
    'ERROR_PERMISSION_DENIED': {'console': True, 'file': True},
    'ERROR_INVALID_CONFIG': {'console': True, 'file': True},
    'ERROR_IMPORT_FAILED': {'console': True, 'file': True},
    'WARNING': {'console': True, 'file': True},
    'INFO': {'console': True, 'file': True},
    'DEBUG': {'console': False, 'file': True},
}

# =============================================================================
# VERBOSE - Everything (debug mode)
# =============================================================================

VERBOSE = {
    # Run lifecycle
    'RUN_START': {'console': True, 'file': True},
    'RUN_END': {'console': True, 'file': True},
    'RUN_FAILED': {'console': True, 'file': True},
    'RUN_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_GENERAL': {'console': True, 'file': True},
    'RUN_COMPLETED_SUCCESS': {'console': True, 'file': True},
    'RUN_FAILED_AT_PHASE': {'console': True, 'file': True},
    'RUN_INTERRUPTED': {'console': True, 'file': True},
    'RUN_SETUP_START': {'console': True, 'file': True},
    'RUN_SETUP_COMPLETE': {'console': True, 'file': True},
    'FATORI_START': {'console': True, 'file': True},
    'FATORI_END': {'console': True, 'file': True},
    
    # Phase lifecycle
    'PHASE_START': {'console': True, 'file': True},
    'PHASE_END': {'console': True, 'file': True},
    'PHASE_FAILED': {'console': True, 'file': True},
    'PHASE_SUCCESS': {'console': True, 'file': True},
    'PHASE_EXCEPTION': {'console': True, 'file': True},
    
    # Validation
    'VALIDATION_START': {'console': True, 'file': True},
    'VALIDATION_END': {'console': True, 'file': True},
    'VALIDATION_ERROR': {'console': True, 'file': True},
    'VALIDATION_WARNING': {'console': True, 'file': True},
    'VALIDATION_ERROR_MISSING_FIELD': {'console': True, 'file': True},
    'VALIDATION_ERROR_INVALID_VALUE': {'console': True, 'file': True},
    'VALIDATION_WARNING_DEPRECATED': {'console': True, 'file': True},
    'VALIDATION_AUTO_CORRECTION': {'console': True, 'file': True},
    'VALIDATION_COMPLETE_NO_ISSUES': {'console': True, 'file': True},
    'VALIDATION_PHASE_EXECUTING': {'console': True, 'file': True},
    'VALIDATION_PHASE_PASSED': {'console': True, 'file': True},
    'VALIDATION_PHASE_FAILED': {'console': True, 'file': True},
    'VALIDATION_PHASE_WARNINGS': {'console': True, 'file': True},
    'VALIDATION_PHASE_EXECUTING': {'console': True, 'file': True},
    'VALIDATION_PHASE_PASSED': {'console': True, 'file': True},
    'VALIDATION_PHASE_WARNINGS': {'console': True, 'file': True},
    
    'DRY_RUN_MODE_ENABLED': {'console': True, 'file': True},
    'DRY_RUN_COMMAND': {'console': True, 'file': True},
    
    # Generation
    'GENERATION_START': {'console': True, 'file': True},
    'GENERATION_END': {'console': True, 'file': True},
    'FILE_GENERATED': {'console': True, 'file': True},
    'SVH_GENERATION': {'console': True, 'file': True},
    'TCL_GENERATION': {'console': True, 'file': True},
    'FEATURES_GENERATION_START': {'console': True, 'file': True},
    'FEATURES_GENERATION_END': {'console': True, 'file': True},
    'FTM_GENERATION_START': {'console': True, 'file': True},
    'FTM_GENERATION_END': {'console': True, 'file': True},
    'GENERATION_PHASE_EXECUTING': {'console': True, 'file': True},
    'GENERATION_PHASE_COMPLETE': {'console': True, 'file': True},
    'GENERATION_PHASE_ERROR': {'console': True, 'file': True},
    'GENERATION_PHASE_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_MASTER_START': {'console': True, 'file': True},
    'GENERATION_STEP1_START': {'console': True, 'file': True},
    'GENERATION_STEP2_START': {'console': True, 'file': True},
    'GENERATION_STEP3_START': {'console': True, 'file': True},
    'GENERATION_STEP4_START': {'console': True, 'file': True},
    'GENERATION_VALIDATION_SUCCESS': {'console': True, 'file': True},
    'ERROR_GENERATION_VALIDATION_FAILED': {'console': True, 'file': True},
    'GENERATION_SVH_COMPLETE': {'console': True, 'file': True},
    'GENERATION_PBLOCK_TCL_COMPLETE': {'console': True, 'file': True},
    'GENERATION_SYSTEM_DICT_START': {'console': True, 'file': True},
    'GENERATION_METRICS_CONFIG_START': {'console': True, 'file': True},
    'GENERATION_SYSTEM_INTEGRATION_COMPLETE': {'console': True, 'file': True},
    'GENERATION_COMPLETE': {'console': True, 'file': True},
    
    # File movement
    'FILE_MOVEMENT_START': {'console': True, 'file': True},
    'FILE_MOVEMENT_END': {'console': True, 'file': True},
    'FILE_ALLOCATED': {'console': True, 'file': True},
    'FILE_BACKUP': {'console': True, 'file': True},
    'FILE_COPY': {'console': True, 'file': True},
    'FILE_MOVEMENT_PHASE_EXECUTING': {'console': True, 'file': True},
    'FILE_MOVEMENT_COMPLETE': {'console': True, 'file': True},
    'FILE_MOVEMENT_NO_FILES': {'console': True, 'file': True},
    'FILE_MOVEMENT_ERROR': {'console': True, 'file': True},
    'TCL_INPUTS_COPIED': {'console': True, 'file': True},
    
    # Build
    'BUILD_START': {'console': True, 'file': True},
    'BUILD_END': {'console': True, 'file': True},
    'BUILD_STEP': {'console': True, 'file': True},
    'BUILD_ERROR': {'console': True, 'file': True},
    'BUILD_VIVADO_SYNTHESIS_START': {'console': True, 'file': True},
    'BUILD_VIVADO_IMPLEMENTATION_START': {'console': True, 'file': True},
    'BUILD_BITSTREAM_START': {'console': True, 'file': True},
    'MAKE_COMMAND_EXECUTING': {'console': True, 'file': True},
    'MAKE_COMMAND_SUCCESS': {'console': True, 'file': True},
    'MAKE_COMMAND_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_VIVADO_FAILED': {'console': True, 'file': True},
    'BUILD_ERROR_MAKE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXECUTING': {'console': True, 'file': True},
    'BUILD_PHASE_CONFIG': {'console': True, 'file': True},
    'BUILD_PHASE_SUCCESS': {'console': True, 'file': True},
    'BUILD_PHASE_FAILED': {'console': True, 'file': True},
    'BUILD_PHASE_EXCEPTION': {'console': True, 'file': True},
    'BUILD_ERRORS_SUMMARY': {'console': True, 'file': True},
    'BUILD_LOG_LOCATION': {'console': True, 'file': True},
    'BUILD_BITSTREAM_READY': {'console': True, 'file': True},
    
    # Execution
    'EXECUTION_START': {'console': True, 'file': True},
    'EXECUTION_END': {'console': True, 'file': True},
    'BENCHMARK_START': {'console': True, 'file': True},
    'BENCHMARK_END': {'console': True, 'file': True},
    'BENCHMARK_OUTPUT': {'console': True, 'file': True},
    'BENCHMARK_ERROR': {'console': True, 'file': True},
    'BENCHMARK_TIMEOUT': {'console': True, 'file': True},
    'SESSION_START': {'console': True, 'file': True},
    'SESSION_COMPLETE': {'console': True, 'file': True},
    'SESSION_FAILED': {'console': True, 'file': True},
    'BENCHMARK_DISCOVERY': {'console': True, 'file': True},
    'FI_LAUNCH': {'console': True, 'file': True},
    'FI_COMPLETE': {'console': True, 'file': True},
    'FI_ERROR': {'console': True, 'file': True},
    'CONSOLE_OUTPUT': {'console': False, 'file': True},
    'EXECUTION_PHASE_START': {'console': True, 'file': True},
    'BENCHMARKS_DISCOVERING': {'console': True, 'file': True},
    'BENCHMARKS_DISCOVERED': {'console': True, 'file': True},
    'BENCHMARKS_VALIDATION_FAILED': {'console': True, 'file': True},
    'BENCHMARKS_VALIDATION_WARNINGS': {'console': True, 'file': True},
    'BENCHMARKS_NONE_ENABLED': {'console': True, 'file': True},
    'FI_ENABLED': {'console': True, 'file': True},
    'FI_DISABLED': {'console': True, 'file': True},
    'FI_VALIDATION_FAILED': {'console': True, 'file': True},
    'FI_VALIDATION_WARNINGS': {'console': True, 'file': True},
    'BENCHMARKS_EXECUTION_START': {'console': True, 'file': True},
    'EXECUTION_NO_RESULTS': {'console': True, 'file': True},
    'EXECUTION_SUMMARY': {'console': True, 'file': True},
    'EXECUTION_ALL_FAILED': {'console': True, 'file': True},
    'EXECUTION_PHASE_COMPLETE': {'console': True, 'file': True},
    'EXECUTION_PHASE_EXCEPTION': {'console': True, 'file': True},
    'EXECUTION_TRACEBACK': {'console': True, 'file': True},
    'EXECUTION_DATA_READY': {'console': True, 'file': True},
    
    # Pblocks
    'PBLOCK_CONFIG_CREATED': {'console': True, 'file': True},
    'PBLOCK_GENERATION_START': {'console': True, 'file': True},
    'PBLOCK_GENERATION_END': {'console': True, 'file': True},
    'PBLOCK_GENERATION_COMPLETE': {'console': True, 'file': True},
    'PBLOCK_MODULE_PROCESSED': {'console': True, 'file': True},
    'PBLOCK_TCL_GENERATED': {'console': True, 'file': True},
    
    # Results
    'RESULTS_START': {'console': True, 'file': True},
    'RESULTS_END': {'console': True, 'file': True},
    'RESULTS_SUMMARY': {'console': True, 'file': True},
    'RESULTS_FILE_CREATED': {'console': True, 'file': True},
    'RESULTS_METRICS_COLLECTED': {'console': True, 'file': True},
    
    # Parser
    'PARSER_START': {'console': True, 'file': True},
    'PARSER_REPORT_PARSED': {'console': True, 'file': True},
    'PARSER_COMPLETE': {'console': True, 'file': True},
    'PARSER_ERROR_REPORT_MISSING': {'console': True, 'file': True},
    'PARSER_ERROR_PARSE_FAILED': {'console': True, 'file': True},
    'PARSER_METRICS_EXTRACTED': {'console': True, 'file': True},
    
    # CLI/UI
    'CLI_DRY_RUN_START': {'console': True, 'file': True},
    'CLI_CONFIG_SUMMARY': {'console': True, 'file': True},
    'CLI_FILES_TO_GENERATE': {'console': True, 'file': True},
    'CLI_BANNER': {'console': True, 'file': True},
    'CLI_OVERRIDE_APPLIED': {'console': True, 'file': True},
    
    # Override system
    'OVERRIDE_START': {'console': True, 'file': True},
    'OVERRIDE_APPLIED': {'console': True, 'file': True},
    'OVERRIDE_VALIDATION': {'console': True, 'file': True},
    
    # Recovery
    'RECOVERY_STATE_SAVED': {'console': True, 'file': True},
    'RECOVERY_STATE_LOADED': {'console': True, 'file': True},
    'RECOVERY_RESUME_START': {'console': True, 'file': True},
    
    # Mapping
    'MAPPING_BOARD': {'console': True, 'file': True},
    'MAPPING_ISA': {'console': True, 'file': True},
    
    # Cleanup
    'CLEANUP_START': {'console': True, 'file': True},
    'CLEANUP_END': {'console': True, 'file': True},
    'CLEANUP_TMP_DIR': {'console': True, 'file': True},
    
    # Setup
    'SETUP_START': {'console': True, 'file': True},
    'SETUP_END': {'console': True, 'file': True},
    'SETUP_DIRECTORIES': {'console': True, 'file': True},
    'SETUP_LOGGING': {'console': True, 'file': True},
    'SETUP_ENVIRONMENT_CHECK': {'console': True, 'file': True},
    
    # System/Environment
    'ENVIRONMENT_VALIDATION_START': {'console': True, 'file': True},
    'ENVIRONMENT_VALIDATION_END': {'console': True, 'file': True},
    'DIRECTORY_CREATED': {'console': True, 'file': True},
    'CONFIG_LOADED': {'console': True, 'file': True},
    
    # Multi-run
    'MULTI_RUN_START': {'console': True, 'file': True},
    'MULTI_RUN_PROGRESS': {'console': True, 'file': True},
    'MULTI_RUN_END': {'console': True, 'file': True},
    
    # Errors and warnings
    'ERROR': {'console': True, 'file': True},
    'ERROR_FATAL': {'console': True, 'file': True},
    'ERROR_RECOVERABLE': {'console': True, 'file': True},
    'ERROR_FILE_NOT_FOUND': {'console': True, 'file': True},
    'ERROR_PERMISSION_DENIED': {'console': True, 'file': True},
    'ERROR_INVALID_CONFIG': {'console': True, 'file': True},
    'ERROR_IMPORT_FAILED': {'console': True, 'file': True},
    'WARNING': {'console': True, 'file': True},
    'INFO': {'console': True, 'file': True},
    'DEBUG': {'console': True, 'file': True},
}

# =============================================================================
# LOG LEVEL REGISTRY
# =============================================================================

LOG_LEVELS = {
    'minimal': MINIMAL,
    'normal': NORMAL,
    'verbose': VERBOSE,
}

# Default log level
DEFAULT_LOG_LEVEL = 'normal'