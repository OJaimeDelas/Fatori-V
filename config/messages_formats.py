# =============================================================================
# FATORI-V • Configuration • Message Formats
# File: messages_formats.py
# -----------------------------------------------------------------------------
# Message format functions for each event type.
# User-editable: Customize message strings for each event.
# =============================================================================

# =============================================================================
# RUN LIFECYCLE EVENTS
# =============================================================================

def format_run_start(run_name, run_id, yaml_path):
    """Format run start message."""
    return (
        "=" * 80 + "\n" +
        f"FATORI-V RUN START\n" +
        f"Run Name: {run_name}\n" +
        f"Run ID: {run_id}\n" +
        f"Config: {yaml_path}\n" +
        "=" * 80
    )

def format_run_end(run_name, run_id, duration, success):
    """Format run end message."""
    status = "SUCCESS" if success else "FAILED"
    return (
        "=" * 80 + "\n" +
        f"FATORI-V RUN END - {status}\n" +
        f"Run: {run_name} ({run_id})\n" +
        f"Duration: {duration:.1f}s\n" +
        "=" * 80
    )

def format_run_failed(run_name, error_message):
    """Format run failure message."""
    return (
        "=" * 80 + "\n" +
        "RUN FAILED\n" +
        f"Run: {run_name}\n" +
        f"Error: {error_message}\n" +
        "=" * 80
    )

def format_fatori_start():
    """Format FATORI-V system start message."""
    return (
        "=" * 80 + "\n" +
        "FATORI-V - Fault Injection Framework for RISC-V\n" +
        "=" * 80
    )

def format_fatori_end(total_duration):
    """Format FATORI-V system end message."""
    return (
        "=" * 80 + "\n" +
        f"FATORI-V execution complete (total: {total_duration:.1f}s)\n" +
        "=" * 80
    )

# =============================================================================
# PHASE LIFECYCLE EVENTS
# =============================================================================

def format_phase_start(phase_name, description=None):
    """Format phase start header."""
    lines = [
        "\n" + "=" * 80,
        f"PHASE: {phase_name.upper()}"
    ]
    if description:
        lines.append(f"Description: {description}")
    lines.append("=" * 80)
    return "\n".join(lines)

def format_phase_end(phase_name, duration):
    """Format phase completion."""
    return f"Phase '{phase_name}' completed ({duration:.1f}s)"

def format_phase_failed(phase_name, error_message):
    """Format phase failure."""
    return f"Phase '{phase_name}' FAILED: {error_message}"

# =============================================================================
# VALIDATION EVENTS
# =============================================================================

def format_validation_start():
    """Format validation start."""
    return "Validating configuration..."

def format_validation_end(error_count, warning_count):
    """Format validation end."""
    if error_count > 0:
        return f"Validation FAILED: {error_count} error(s), {warning_count} warning(s)"
    elif warning_count > 0:
        return f"Validation passed with {warning_count} warning(s)"
    else:
        return "Validation passed"

def format_validation_error(error_message):
    """Format validation error."""
    return f"  ERROR: {error_message}"

def format_validation_warning(warning_message):
    """Format validation warning."""
    return f"  WARNING: {warning_message}"

def format_validation_error_missing_field(field_name, section):
    """Format missing field error."""
    return f"Validation Error: Required field '{field_name}' missing in section '{section}'"

def format_validation_error_invalid_value(field_name, value, expected):
    """Format invalid value error."""
    return f"Validation Error: Field '{field_name}' has invalid value '{value}' (expected: {expected})"

def format_validation_warning_deprecated(field_name, replacement):
    """Format deprecation warning."""
    return f"Warning: Field '{field_name}' is deprecated, use '{replacement}' instead"

def format_validation_auto_correction(correction_description):
    """Format auto-correction message."""
    return f"  AUTO-CORRECTED: {correction_description}"

def format_validation_complete_no_issues():
    """Format validation success with no issues."""
    return "Configuration validation passed with no issues"

# =============================================================================
# PHASE-SPECIFIC EVENTS
# =============================================================================

def format_validation_phase_executing():
    """Format validation phase execution start."""
    return "Validating configuration..."

def format_validation_phase_passed():
    """Format validation phase passed."""
    return "Configuration validation passed"

def format_validation_phase_failed(error_count):
    """Format validation phase failure."""
    return f"Validation failed with {error_count} error(s)"

def format_validation_phase_warnings(warning_count):
    """Format validation phase warnings."""
    return f"Validation passed with {warning_count} warning(s)"

def format_generation_master_start():
    """Format generation master start."""
    return "Starting file generation workflow..."

def format_generation_step1_start():
    """Format generation step 1 start."""
    return "Step 1: Configuration validation"

def format_generation_step2_start():
    """Format generation step 2 start."""
    return "Step 2: Generating SystemVerilog headers"

def format_generation_step3_start():
    """Format generation step 3 start."""
    return "Step 3: Generating pblock files and TCL scripts"

def format_generation_step4_start():
    """Format generation step 4 start."""
    return "Step 4: Generating system integration files"

def format_generation_validation_success():
    """Format generation validation success."""
    return "Configuration validated successfully"

def format_error_generation_validation_failed():
    """Format generation validation failure."""
    return "ERROR: Configuration validation failed"

def format_generation_svh_complete(file_count):
    """Format SVH generation completion."""
    return f"SystemVerilog headers generated ({file_count} files)"

def format_generation_pblock_tcl_complete():
    """Format pblock/TCL generation completion."""
    return "Pblock and TCL generation complete"

def format_generation_system_dict_start():
    """Format system dict generation start."""
    return "Generating system_dict_merged.yaml..."

def format_generation_metrics_config_start():
    """Format metrics config generation start."""
    return "Generating metrics_config.h..."

def format_generation_system_integration_complete():
    """Format system integration completion."""
    return "System integration files complete"

def format_generation_complete(total_files, svh_headers, pblock_files, tcl_scripts, system_files):
    """Format generation master completion."""
    return f"File generation complete: {total_files} total ({svh_headers} SVH, {pblock_files} pblock, {tcl_scripts} TCL, {system_files} system)"

def format_generation_phase_executing():
    """Format generation phase execution start."""
    return "Generating files..."

def format_generation_phase_complete(total_files, svh_count, pblock_count, tcl_count, system_count):
    """Format generation phase completion."""
    return f"Generated {total_files} files: {svh_count} SVH, {pblock_count} pblock, {tcl_count} TCL, {system_count} system"

def format_generation_phase_validation_failed():
    """Format generation validation failure."""
    return "Generation validation failed"

def format_generation_phase_error(error_message):
    """Format generation phase error."""
    return f"Generation error: {error_message}"

def format_build_phase_executing():
    """Format build phase execution start."""
    return "Building hardware..."

def format_build_phase_config(clean_before_build, run_ibex_setup):
    """Format build configuration."""
    return f"Build config: clean={clean_before_build}, ibex_setup={run_ibex_setup}"

def format_build_phase_success():
    """Format build phase success."""
    return "Build completed successfully"

def format_build_phase_failed(error_message, step_failed):
    """Format build phase failure."""
    return f"Build failed at '{step_failed}': {error_message}"

def format_build_phase_exception(error_message):
    """Format build phase exception."""
    return f"Build exception: {error_message}"

def format_build_errors_summary(errors, suggestions):
    """Format build errors summary."""
    error_str = '\n  '.join(errors[:5]) if isinstance(errors, list) else str(errors)
    result = f"Build errors:\n  {error_str}"
    if suggestions and isinstance(suggestions, list) and len(suggestions) > 0:
        result += f"\nSuggestion: {suggestions[0]}"
    return result

def format_build_log_location(log_file):
    """Format build log location."""
    return f"Build log saved: {log_file}"

def format_build_bitstream_ready():
    """Format bitstream ready notification."""
    return "FPGA bitstream ready"

def format_file_movement_phase_executing():
    """Format file movement phase execution start."""
    return "Moving files to architecture..."

def format_file_movement_complete(total_files, generated_count, tcl_count, static_count):
    """Format file movement completion."""
    return f"File allocation complete: {total_files} files ({generated_count} generated, {tcl_count} TCL, {static_count} static)"

def format_file_movement_no_files():
    """Format no files moved."""
    return "No files to move"

def format_file_movement_error(error_message):
    """Format file movement error."""
    return f"File movement error: {error_message}"

def format_tcl_inputs_copied(file_count):
    """Format TCL inputs copied."""
    return f"Copied {file_count} TCL file(s) to Vivado inputs"

# =============================================================================
# GENERATION EVENTS
# =============================================================================

def format_generation_start():
    """Format generation start."""
    return "Generating hardware files..."

def format_generation_end(file_count):
    """Format generation completion."""
    return f"Generation complete ({file_count} files)"

def format_file_generated(filename, output_path):
    """Format file generation."""
    return f"  Generated: {filename} -> {output_path}"

def format_svh_generation(filename):
    """Format SystemVerilog header generation."""
    return f"  SVH: {filename}"

def format_tcl_generation(filename):
    """Format TCL script generation."""
    return f"  TCL: {filename}"

def format_features_generation_start():
    """Format features generation start."""
    return "Generating fatori_features.svh..."

def format_features_generation_end():
    """Format features generation end."""
    return "Features generation complete"

def format_ftm_generation_start():
    """Format FTM generation start."""
    return "Generating FTM headers..."

def format_ftm_generation_end(file_count):
    """Format FTM generation end."""
    return f"FTM generation complete ({file_count} files)"

# =============================================================================
# FILE MOVEMENT EVENTS
# =============================================================================

def format_file_movement_start():
    """Format file movement start."""
    return "Allocating files to architecture..."

def format_file_movement_end(file_count):
    """Format file movement end."""
    return f"File allocation complete ({file_count} files)"

def format_file_allocated(source, destination):
    """Format file allocation."""
    return f"  {source} -> {destination}"

def format_file_backup(backup_path):
    """Format file backup."""
    return f"  Backup: {backup_path}"

def format_file_copy(source, destination):
    """Format file copy."""
    return f"  Copy: {source} -> {destination}"

# =============================================================================
# BUILD EVENTS
# =============================================================================

def format_build_start(target):
    """Format build start."""
    return f"Starting build: {target}"

def format_build_end(duration):
    """Format build completion."""
    return f"Build complete ({duration:.1f}s)"

def format_build_step(step_name):
    """Format build step."""
    return f"  -> {step_name}"

def format_build_error(error_message):
    """Format build error."""
    return f"Build Error: {error_message}"

def format_build_vivado_synthesis_start():
    """Format Vivado synthesis start."""
    return (
        "\n" + "-" * 80 + "\n" +
        "Vivado Synthesis\n" +
        "-" * 80
    )

def format_build_vivado_implementation_start():
    """Format Vivado implementation start."""
    return (
        "\n" + "-" * 80 + "\n" +
        "Vivado Implementation\n" +
        "-" * 80
    )

def format_build_bitstream_start():
    """Format bitstream generation start."""
    return (
        "\n" + "-" * 80 + "\n" +
        "Bitstream Generation\n" +
        "-" * 80
    )

def format_make_command_executing(command):
    """Format make command execution."""
    return f"Executing: {command}"

def format_make_command_success(command, duration):
    """Format make command success."""
    return f"Command succeeded ({duration:.1f}s): {command}"

def format_make_command_failed(command, exit_code):
    """Format make command failure."""
    return f"Command failed (exit {exit_code}): {command}"

def format_build_error_vivado_failed(log_file):
    """Format Vivado failure error."""
    return (
        f"Build Error: Vivado synthesis/implementation failed\n"
        f"Check log file: {log_file}"
    )

def format_build_error_make_failed(target, exit_code):
    """Format make failure error."""
    return f"Build Error: Make target '{target}' failed with exit code {exit_code}"

# =============================================================================
# EXECUTION EVENTS
# =============================================================================

def format_execution_start():
    """Format execution phase start."""
    return "Starting benchmark execution..."

def format_execution_end(benchmark_count, session_count):
    """Format execution phase end."""
    return f"Execution complete ({benchmark_count} benchmarks, {session_count} sessions)"

def format_benchmark_start(benchmark_name, session_name):
    """Format benchmark start."""
    return f"Benchmark: {benchmark_name} (session: {session_name})"

def format_benchmark_end(benchmark_name, duration, exit_code):
    """Format benchmark completion."""
    status = "SUCCESS" if exit_code == 0 else f"FAILED (exit {exit_code})"
    return f"Benchmark {benchmark_name} - {status} ({duration:.1f}s)"

def format_benchmark_output(line):
    """Format benchmark stdout/stderr line."""
    return f"  | {line}"

def format_benchmark_error(benchmark_name, error_message):
    """Format benchmark error."""
    return f"Benchmark Error [{benchmark_name}]: {error_message}"

def format_benchmark_timeout(benchmark_name, timeout_seconds):
    """Format benchmark timeout."""
    return f"Benchmark {benchmark_name} timed out after {timeout_seconds}s"

def format_session_start(session_id, benchmark):
    """Format session start."""
    return f"Session #{session_id}: {benchmark}"

def format_session_complete(session_name, duration):
    """Format session completion."""
    return f"Session {session_name} complete ({duration:.1f}s)"

def format_session_failed(session_name, error_message):
    """Format session failure."""
    return f"Session {session_name} FAILED: {error_message}"

def format_benchmark_discovery(benchmark_count, suite_name):
    """Format benchmark discovery."""
    return f"Discovered {benchmark_count} benchmarks in {suite_name}"

def format_fi_launch(command):
    """Format FI console launch."""
    return f"Launching FI console: {command}"

def format_fi_complete(injection_count):
    """Format FI completion."""
    return f"Fault injection complete ({injection_count} injections)"

def format_fi_error(error_message):
    """Format FI error."""
    return f"FI Error: {error_message}"

def format_console_output(line):
    """Format console output line."""
    return f"{line}"

# =============================================================================
# PBLOCK EVENTS
# =============================================================================

def format_pblock_config_created(config_path):
    """Format pblock config creation."""
    return f"Pblock config created: {config_path}"

def format_pblock_generation_start(target_count=0):
    """Format pblock generation start."""
    if target_count > 0:
        return f"Generating pblocks for {target_count} targets..."
    return "Generating pblocks..."

def format_pblock_generation_end(file_count):
    """Format pblock generation end."""
    return f"Pblock generation complete ({file_count} files)"

def format_pblock_generation_complete(pblock_file):
    """Format pblock generation final output."""
    return f"Pblocks generated: {pblock_file}"

def format_pblock_module_processed(module_name, cell_count):
    """Format pblock module processing."""
    return f"  Processed module: {module_name} ({cell_count} cells)"

def format_pblock_tcl_generated(tcl_file):
    """Format pblock TCL generation."""
    return f"  TCL generated: {tcl_file}"

# =============================================================================
# RESULTS EVENTS
# =============================================================================

def format_results_start():
    """Format results collection start."""
    return "Collecting results..."

def format_results_end(file_count):
    """Format results collection end."""
    return f"Results collected ({file_count} files)"

def format_results_summary(summary_data):
    """Format results summary."""
    return (
        "\n" + "=" * 80 + "\n" +
        "RESULTS SUMMARY\n" +
        "=" * 80 + "\n" +
        f"{summary_data}\n" +
        "=" * 80
    )

def format_results_file_created(file_path):
    """Format results file creation."""
    return f"  Created: {file_path}"

def format_results_metrics_collected(metric_count, source):
    """Format metrics collection."""
    return f"  Collected {metric_count} metrics from {source}"

# =============================================================================
# PARSER EVENTS
# =============================================================================

def format_parser_start(reports_dir):
    """Format parser start."""
    return f"Parsing Vivado reports: {reports_dir}"

def format_parser_report_parsed(report_type, report_file):
    """Format report parsing."""
    return f"  Parsed: {report_type} ({report_file})"

def format_parser_complete(metric_count):
    """Format parser completion."""
    return f"Parser complete ({metric_count} metrics extracted)"

def format_parser_error_report_missing(report_type):
    """Format missing report error."""
    return f"Parser Error: Required report missing: {report_type}"

def format_parser_error_parse_failed(report_file, error_message):
    """Format parse failure error."""
    return f"Parser Error: Failed to parse {report_file}: {error_message}"

def format_parser_metrics_extracted(metric_name, value):
    """Format metric extraction."""
    return f"  Metric: {metric_name} = {value}"

# =============================================================================
# CLI/UI EVENTS
# =============================================================================

def format_cli_dry_run_start():
    """Format dry run start."""
    return "DRY RUN - Configuration preview only"

def format_cli_config_summary(summary_lines):
    """Format configuration summary."""
    return (
        "\n" + "=" * 80 + "\n" +
        "CONFIGURATION SUMMARY\n" +
        "=" * 80 + "\n" +
        f"{summary_lines}\n" +
        "=" * 80
    )

def format_cli_files_to_generate(file_list):
    """Format files to generate list."""
    files_str = "\n".join([f"  - {f}" for f in file_list])
    return (
        "\n" + "FILES TO GENERATE:\n" +
        "-" * 80 + "\n" +
        f"{files_str}"
    )

def format_cli_banner(run_name, run_id):
    """Format CLI banner."""
    return (
        "\n" + "=" * 80 + "\n" +
        f"FATORI-V: {run_name} (ID: {run_id})\n" +
        "=" * 80
    )

def format_cli_override_applied(key, old_value, new_value):
    """Format CLI override application."""
    return f"Override applied: {key} = {new_value} (was: {old_value})"

# =============================================================================
# OVERRIDE SYSTEM EVENTS
# =============================================================================

def format_override_start(override_count):
    """Format override processing start."""
    return f"Processing {override_count} configuration overrides..."

def format_override_applied(override_key, override_value):
    """Format override application."""
    return f"  Override: {override_key} = {override_value}"

def format_override_validation(override_key, status):
    """Format override validation."""
    return f"  Validated: {override_key} ({status})"

# =============================================================================
# RECOVERY EVENTS
# =============================================================================

def format_recovery_state_saved(state_file):
    """Format state save."""
    return f"Recovery state saved: {state_file}"

def format_recovery_state_loaded(state_file):
    """Format state load."""
    return f"Recovery state loaded: {state_file}"

def format_recovery_resume_start(phase_name):
    """Format recovery resume."""
    return f"Resuming from phase: {phase_name}"

# =============================================================================
# MAPPING EVENTS
# =============================================================================

def format_mapping_board(board_name, board_config):
    """Format board mapping."""
    return f"Board mapping: {board_name} -> {board_config}"

def format_mapping_isa(isa_extension, enabled):
    """Format ISA extension mapping."""
    status = "enabled" if enabled else "disabled"
    return f"ISA extension: {isa_extension} ({status})"

# =============================================================================
# CLEANUP EVENTS
# =============================================================================

def format_cleanup_start():
    """Format cleanup start."""
    return "Cleaning up temporary files..."

def format_cleanup_end(files_removed):
    """Format cleanup end."""
    return f"Cleanup complete ({files_removed} files removed)"

def format_cleanup_tmp_dir(dir_path):
    """Format tmp directory cleanup."""
    return f"  Removed: {dir_path}"

# =============================================================================
# SETUP EVENTS
# =============================================================================

def format_setup_start():
    """Format setup start."""
    return "Setting up run environment..."

def format_setup_end():
    """Format setup end."""
    return "Setup complete"

def format_setup_directories(dir_list):
    """Format directory setup."""
    dirs_str = ", ".join(dir_list)
    return f"Created directories: {dirs_str}"

def format_setup_logging(log_file):
    """Format logging setup."""
    return f"Logging initialized: {log_file}"

def format_setup_environment_check():
    """Format environment check."""
    return "Checking environment..."

# =============================================================================
# SYSTEM/ENVIRONMENT EVENTS
# =============================================================================

def format_environment_validation_start():
    """Format environment validation start."""
    return "Validating system environment..."

def format_environment_validation_end(checks_passed, checks_total):
    """Format environment validation end."""
    return f"Environment validation complete ({checks_passed}/{checks_total} checks passed)"

def format_directory_created(dir_path):
    """Format directory creation."""
    return f"  Created directory: {dir_path}"

def format_config_loaded(yaml_path):
    """Format configuration load."""
    return f"Loaded configuration: {yaml_path}"

# =============================================================================
# MULTI-RUN EVENTS
# =============================================================================

def format_multi_run_start(run_count):
    """Format multi-run start."""
    return (
        "=" * 80 + "\n" +
        f"MULTI-RUN: {run_count} runs scheduled\n" +
        "=" * 80
    )

def format_multi_run_progress(current, total, run_name):
    """Format multi-run progress."""
    return f"Run {current}/{total}: {run_name}"

def format_multi_run_end(success_count, fail_count, total_duration):
    """Format multi-run end."""
    return (
        "=" * 80 + "\n" +
        "MULTI-RUN COMPLETE\n" +
        f"Success: {success_count} | Failed: {fail_count}\n" +
        f"Total duration: {total_duration:.1f}s\n" +
        "=" * 80
    )

# =============================================================================
# ERROR AND WARNING EVENTS
# =============================================================================

def format_error(error_message):
    """Format generic error."""
    return f"ERROR: {error_message}"

def format_error_fatal(error_message):
    """Format fatal error."""
    return (
        "\n" + "!" * 80 + "\n" +
        "FATAL ERROR\n" +
        f"{error_message}\n" +
        "!" * 80
    )

def format_error_recoverable(error_message, recovery_action):
    """Format recoverable error."""
    return f"ERROR (recoverable): {error_message}\nRecovery: {recovery_action}"

def format_error_file_not_found(file_path):
    """Format file not found error."""
    return f"Error: Required file not found: {file_path}"

def format_error_permission_denied(file_path):
    """Format permission error."""
    return f"Error: Permission denied accessing: {file_path}"

def format_error_invalid_config(config_field, reason):
    """Format invalid configuration error."""
    return f"Error: Invalid configuration for '{config_field}': {reason}"

def format_error_import_failed(module_name, error_message):
    """Format import failure error."""
    return f"Error: Failed to import '{module_name}': {error_message}"

def format_warning(warning_message):
    """Format generic warning."""
    return f"WARNING: {warning_message}"

def format_info(info_message):
    """Format info message."""
    return f"INFO: {info_message}"

def format_debug(debug_message):
    """Format debug message."""
    return f"DEBUG: {debug_message}"

def format_dry_run_mode_enabled():
    """Format dry-run mode enabled message."""
    return (
        "\n" +
        "=" * 80 + "\n" +
        "DRY-RUN MODE ENABLED\n" +
        "=" * 80 + "\n" +
        "System will execute all phases but PRINT commands instead of running them.\n" +
        "Files WILL be generated and validation WILL run.\n" +
        "Only build commands and benchmark execution will be skipped.\n" +
        "=" * 80
    )

def format_dry_run_command(command, cwd):
    """Format dry-run command display."""
    return (
        "\n" +
        "[DRY-RUN] Would execute:\n" +
        f"  Command: {command}\n" +
        f"  Directory: {cwd}"
    )

# =============================================================================
# EXECUTION PHASE EVENTS
# =============================================================================

def format_execution_phase_start():
    """Format execution phase start."""
    return "Starting benchmark execution phase..."

def format_benchmarks_discovering():
    """Format benchmark discovery start."""
    return "Discovering available benchmarks..."

def format_benchmarks_discovered(count):
    """Format benchmark discovery completion."""
    return f"Found {count} enabled benchmark(s)"

def format_benchmarks_validation_failed(error_count, errors):
    """Format benchmark validation failure."""
    errors_str = "; ".join(errors[:3])
    return f"Benchmark validation failed: {error_count} error(s) - {errors_str}"

def format_benchmarks_validation_warnings(warning_count):
    """Format benchmark validation warnings."""
    return f"Benchmark validation: {warning_count} warning(s)"

def format_benchmarks_none_enabled():
    """Format no benchmarks enabled."""
    return "No benchmarks enabled - nothing to execute"

def format_fi_enabled():
    """Format fault injection enabled."""
    return "Fault injection is ENABLED for this run"

def format_fi_disabled():
    """Format fault injection disabled."""
    return "Fault injection is DISABLED for this run"

def format_fi_validation_failed(error_count, errors):
    """Format FI validation failure."""
    errors_str = "; ".join(errors[:3])
    return f"Fault injection validation failed: {error_count} error(s) - {errors_str}"

def format_fi_validation_warnings(warning_count):
    """Format FI validation warnings."""
    return f"Fault injection validation: {warning_count} warning(s)"

def format_benchmarks_execution_start():
    """Format benchmark execution start."""
    return "Executing benchmarks..."

def format_execution_no_results():
    """Format no execution results."""
    return "No execution results collected"

def format_execution_summary(total_sessions, successful_sessions, failed_sessions, fi_sessions):
    """Format execution summary."""
    return (
        f"Execution complete: {total_sessions} session(s) - "
        f"{successful_sessions} succeeded, {failed_sessions} failed, "
        f"{fi_sessions} with FI"
    )

def format_execution_all_failed():
    """Format all executions failed."""
    return "All benchmark executions failed"

def format_execution_phase_complete():
    """Format execution phase completion."""
    return "Benchmark execution phase complete"

def format_execution_phase_exception(error_message):
    """Format execution phase exception."""
    return f"Execution phase exception: {error_message}"

def format_execution_traceback(traceback):
    """Format execution traceback."""
    return f"Traceback:\n{traceback}"

def format_execution_data_ready():
    """Format execution data ready."""
    return "Execution data ready for results processing"

# =============================================================================
# FORMAT FUNCTION REGISTRY
# =============================================================================

FORMAT_FUNCTIONS = {
    # Run lifecycle
    'RUN_START': format_run_start,
    'RUN_END': format_run_end,
    'RUN_FAILED': format_run_failed,
    'FATORI_START': format_fatori_start,
    'FATORI_END': format_fatori_end,

    'VALIDATION_PHASE_EXECUTING': format_validation_phase_executing,
    'VALIDATION_PHASE_PASSED': format_validation_phase_passed,
    'VALIDATION_PHASE_FAILED': format_validation_phase_failed,
    'VALIDATION_PHASE_WARNINGS': format_validation_phase_warnings,
    'GENERATION_PHASE_EXECUTING': format_generation_phase_executing,
    'GENERATION_PHASE_COMPLETE': format_generation_phase_complete,
    'GENERATION_PHASE_VALIDATION_FAILED': format_generation_phase_validation_failed,
    'GENERATION_PHASE_ERROR': format_generation_phase_error,
    'BUILD_PHASE_EXECUTING': format_build_phase_executing,
    'BUILD_PHASE_CONFIG': format_build_phase_config,
    'BUILD_PHASE_SUCCESS': format_build_phase_success,
    'BUILD_PHASE_FAILED': format_build_phase_failed,
    'BUILD_PHASE_EXCEPTION': format_build_phase_exception,
    'BUILD_ERRORS_SUMMARY': format_build_errors_summary,
    'BUILD_LOG_LOCATION': format_build_log_location,
    'BUILD_BITSTREAM_READY': format_build_bitstream_ready,
    'FILE_MOVEMENT_PHASE_EXECUTING': format_file_movement_phase_executing,
    'FILE_MOVEMENT_COMPLETE': format_file_movement_complete,
    'FILE_MOVEMENT_NO_FILES': format_file_movement_no_files,
    'FILE_MOVEMENT_ERROR': format_file_movement_error,
    'TCL_INPUTS_COPIED': format_tcl_inputs_copied,
    
    # Phase lifecycle
    'PHASE_START': format_phase_start,
    'PHASE_END': format_phase_end,
    'PHASE_FAILED': format_phase_failed,

    'DRY_RUN_MODE_ENABLED': format_dry_run_mode_enabled,
    'DRY_RUN_COMMAND': format_dry_run_command,
    
    # Validation
    'VALIDATION_START': format_validation_start,
    'VALIDATION_END': format_validation_end,
    'VALIDATION_ERROR': format_validation_error,
    'VALIDATION_WARNING': format_validation_warning,
    'VALIDATION_ERROR_MISSING_FIELD': format_validation_error_missing_field,
    'VALIDATION_ERROR_INVALID_VALUE': format_validation_error_invalid_value,
    'VALIDATION_WARNING_DEPRECATED': format_validation_warning_deprecated,
    'VALIDATION_AUTO_CORRECTION': format_validation_auto_correction,
    'VALIDATION_COMPLETE_NO_ISSUES': format_validation_complete_no_issues,
    
    # Generation
    'GENERATION_START': format_generation_start,
    'GENERATION_END': format_generation_end,
    'FILE_GENERATED': format_file_generated,
    'SVH_GENERATION': format_svh_generation,
    'TCL_GENERATION': format_tcl_generation,
    'FEATURES_GENERATION_START': format_features_generation_start,
    'FEATURES_GENERATION_END': format_features_generation_end,
    'FTM_GENERATION_START': format_ftm_generation_start,
    'FTM_GENERATION_END': format_ftm_generation_end,
    'GENERATION_MASTER_START': format_generation_master_start,
    'GENERATION_STEP1_START': format_generation_step1_start,
    'GENERATION_STEP2_START': format_generation_step2_start,
    'GENERATION_STEP3_START': format_generation_step3_start,
    'GENERATION_STEP4_START': format_generation_step4_start,
    'GENERATION_VALIDATION_SUCCESS': format_generation_validation_success,
    'ERROR_GENERATION_VALIDATION_FAILED': format_error_generation_validation_failed,
    'GENERATION_SVH_COMPLETE': format_generation_svh_complete,
    'GENERATION_PBLOCK_TCL_COMPLETE': format_generation_pblock_tcl_complete,
    'GENERATION_SYSTEM_DICT_START': format_generation_system_dict_start,
    'GENERATION_METRICS_CONFIG_START': format_generation_metrics_config_start,
    'GENERATION_SYSTEM_INTEGRATION_COMPLETE': format_generation_system_integration_complete,
    'GENERATION_COMPLETE': format_generation_complete,
    
    # File movement
    'FILE_MOVEMENT_START': format_file_movement_start,
    'FILE_MOVEMENT_END': format_file_movement_end,
    'FILE_ALLOCATED': format_file_allocated,
    'FILE_BACKUP': format_file_backup,
    'FILE_COPY': format_file_copy,
    
    # Build
    'BUILD_START': format_build_start,
    'BUILD_END': format_build_end,
    'BUILD_STEP': format_build_step,
    'BUILD_ERROR': format_build_error,
    'BUILD_VIVADO_SYNTHESIS_START': format_build_vivado_synthesis_start,
    'BUILD_VIVADO_IMPLEMENTATION_START': format_build_vivado_implementation_start,
    'BUILD_BITSTREAM_START': format_build_bitstream_start,
    'MAKE_COMMAND_EXECUTING': format_make_command_executing,
    'MAKE_COMMAND_SUCCESS': format_make_command_success,
    'MAKE_COMMAND_FAILED': format_make_command_failed,
    'BUILD_ERROR_VIVADO_FAILED': format_build_error_vivado_failed,
    'BUILD_ERROR_MAKE_FAILED': format_build_error_make_failed,
    
    # Execution
    'EXECUTION_START': format_execution_start,
    'EXECUTION_END': format_execution_end,
    'BENCHMARK_START': format_benchmark_start,
    'BENCHMARK_END': format_benchmark_end,
    'BENCHMARK_OUTPUT': format_benchmark_output,
    'BENCHMARK_ERROR': format_benchmark_error,
    'BENCHMARK_TIMEOUT': format_benchmark_timeout,
    'SESSION_START': format_session_start,
    'SESSION_COMPLETE': format_session_complete,
    'SESSION_FAILED': format_session_failed,
    'BENCHMARK_DISCOVERY': format_benchmark_discovery,
    'FI_LAUNCH': format_fi_launch,
    'FI_COMPLETE': format_fi_complete,
    'FI_ERROR': format_fi_error,
    'CONSOLE_OUTPUT': format_console_output,
    'EXECUTION_PHASE_START': format_execution_phase_start,
    'BENCHMARKS_DISCOVERING': format_benchmarks_discovering,
    'BENCHMARKS_DISCOVERED': format_benchmarks_discovered,
    'BENCHMARKS_VALIDATION_FAILED': format_benchmarks_validation_failed,
    'BENCHMARKS_VALIDATION_WARNINGS': format_benchmarks_validation_warnings,
    'BENCHMARKS_NONE_ENABLED': format_benchmarks_none_enabled,
    'FI_ENABLED': format_fi_enabled,
    'FI_DISABLED': format_fi_disabled,
    'FI_VALIDATION_FAILED': format_fi_validation_failed,
    'FI_VALIDATION_WARNINGS': format_fi_validation_warnings,
    'BENCHMARKS_EXECUTION_START': format_benchmarks_execution_start,
    'EXECUTION_NO_RESULTS': format_execution_no_results,
    'EXECUTION_SUMMARY': format_execution_summary,
    'EXECUTION_ALL_FAILED': format_execution_all_failed,
    'EXECUTION_PHASE_COMPLETE': format_execution_phase_complete,
    'EXECUTION_PHASE_EXCEPTION': format_execution_phase_exception,
    'EXECUTION_TRACEBACK': format_execution_traceback,
    'EXECUTION_DATA_READY': format_execution_data_ready,
    
    # Pblocks
    'PBLOCK_CONFIG_CREATED': format_pblock_config_created,
    'PBLOCK_GENERATION_START': format_pblock_generation_start,
    'PBLOCK_GENERATION_END': format_pblock_generation_end,
    'PBLOCK_GENERATION_COMPLETE': format_pblock_generation_complete,
    'PBLOCK_MODULE_PROCESSED': format_pblock_module_processed,
    'PBLOCK_TCL_GENERATED': format_pblock_tcl_generated,
    
    # Results
    'RESULTS_START': format_results_start,
    'RESULTS_END': format_results_end,
    'RESULTS_SUMMARY': format_results_summary,
    'RESULTS_FILE_CREATED': format_results_file_created,
    'RESULTS_METRICS_COLLECTED': format_results_metrics_collected,
    
    # Parser
    'PARSER_START': format_parser_start,
    'PARSER_REPORT_PARSED': format_parser_report_parsed,
    'PARSER_COMPLETE': format_parser_complete,
    'PARSER_ERROR_REPORT_MISSING': format_parser_error_report_missing,
    'PARSER_ERROR_PARSE_FAILED': format_parser_error_parse_failed,
    'PARSER_METRICS_EXTRACTED': format_parser_metrics_extracted,
    
    # CLI/UI
    'CLI_DRY_RUN_START': format_cli_dry_run_start,
    'CLI_CONFIG_SUMMARY': format_cli_config_summary,
    'CLI_FILES_TO_GENERATE': format_cli_files_to_generate,
    'CLI_BANNER': format_cli_banner,
    'CLI_OVERRIDE_APPLIED': format_cli_override_applied,
    
    # Override
    'OVERRIDE_START': format_override_start,
    'OVERRIDE_APPLIED': format_override_applied,
    'OVERRIDE_VALIDATION': format_override_validation,
    
    # Recovery
    'RECOVERY_STATE_SAVED': format_recovery_state_saved,
    'RECOVERY_STATE_LOADED': format_recovery_state_loaded,
    'RECOVERY_RESUME_START': format_recovery_resume_start,
    
    # Mapping
    'MAPPING_BOARD': format_mapping_board,
    'MAPPING_ISA': format_mapping_isa,
    
    # Cleanup
    'CLEANUP_START': format_cleanup_start,
    'CLEANUP_END': format_cleanup_end,
    'CLEANUP_TMP_DIR': format_cleanup_tmp_dir,
    
    # Setup
    'SETUP_START': format_setup_start,
    'SETUP_END': format_setup_end,
    'SETUP_DIRECTORIES': format_setup_directories,
    'SETUP_LOGGING': format_setup_logging,
    'SETUP_ENVIRONMENT_CHECK': format_setup_environment_check,
    
    # System/Environment
    'ENVIRONMENT_VALIDATION_START': format_environment_validation_start,
    'ENVIRONMENT_VALIDATION_END': format_environment_validation_end,
    'DIRECTORY_CREATED': format_directory_created,
    'CONFIG_LOADED': format_config_loaded,
    
    # Multi-run
    'MULTI_RUN_START': format_multi_run_start,
    'MULTI_RUN_PROGRESS': format_multi_run_progress,
    'MULTI_RUN_END': format_multi_run_end,
    
    # Errors and warnings
    'ERROR': format_error,
    'ERROR_FATAL': format_error_fatal,
    'ERROR_RECOVERABLE': format_error_recoverable,
    'ERROR_FILE_NOT_FOUND': format_error_file_not_found,
    'ERROR_PERMISSION_DENIED': format_error_permission_denied,
    'ERROR_INVALID_CONFIG': format_error_invalid_config,
    'ERROR_IMPORT_FAILED': format_error_import_failed,
    'WARNING': format_warning,
    'INFO': format_info,
    'DEBUG': format_debug,
}