# =============================================================================
# FATORI-V • Configuration • Message Formats
# File: messages_formats.py
# -----------------------------------------------------------------------------
# Message format functions for each event type.
# User-editable: Customize message strings for each event.
# =============================================================================

# =============================================================================
# RUN LIFECYCLE
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

def format_run_failed(run_name=None, error_message=None):
    """Format run failure message."""
    lines = ["=" * 80, "RUN FAILED"]
    if run_name:
        lines.append(f"Run: {run_name}")
    if error_message:
        lines.append(f"Error: {error_message}")
    lines.append("=" * 80)
    return "\n".join(lines)

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
# PHASE LIFECYCLE
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
# VALIDATION - Core Events
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
    return f"\n  WARNING: {warning_message}"

def format_validation_error_missing_field(field_name, section):
    """Format missing field error."""
    return f"\nValidation Error: Required field '{field_name}' missing in section '{section}'"

def format_validation_error_invalid_value(field_name, value, expected):
    """Format invalid value error."""
    return f"\nValidation Error: Field '{field_name}' has invalid value '{value}' (expected: {expected})"

def format_validation_warning_deprecated(field_name, replacement):
    """Format deprecation warning."""
    return f"\nWarning: Field '{field_name}' is deprecated, use '{replacement}' instead"

def format_validation_auto_correction(correction_description):
    """Format auto-correction message."""
    return f"  AUTO-CORRECTED: {correction_description}\n"

def format_validation_complete_no_issues():
    """Format validation success with no issues."""
    return "Configuration validation passed with no issues"

# =============================================================================
# VALIDATION - Phase Execution
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

# =============================================================================
# VALIDATION - Detailed Display
# =============================================================================

def format_validation_start_full():
    """Format full validation start."""
    return "Starting validation..."

def format_validation_strict_mode(enabled):
    """Format strict mode status."""
    mode = "ENABLED" if enabled else "DISABLED"
    return f"Strict mode: {mode}"

def format_validation_summary_start():
    """Format validation summary header."""
    return "\nValidation Summary:"

def format_validation_summary_end():
    """Format validation summary footer."""
    return ""

def format_validation_config_valid():
    """Format successful validation."""
    return "Configuration validation passed"

def format_validation_error_count(error_count):
    """Format error count."""
    return f"Validation failed with {error_count} error(s)"

def format_validation_error_item(index, error_message):
    """Format individual error item."""
    return f"  Error {index}: {error_message}"

def format_validation_error_more(additional_count):
    """Format additional errors message."""
    return f"  ... and {additional_count} more error(s)"

def format_validation_warning_count(warning_count):
    """Format warning count."""
    return f"Validation warnings: {warning_count}"

def format_validation_warning_item(index, warning_message):
    """Format individual warning item."""
    return f"  Warning {index}: {warning_message}"

def format_validation_warning_more(additional_count):
    """Format additional warnings message."""
    return f"  ... and {additional_count} more warning(s)"

def format_validation_corrections_applied(correction_count):
    """Format corrections applied message."""
    return f"Auto-corrections applied: {correction_count}"

def format_error_validation_exception(error_message):
    """Format validation exception error."""
    return f"ERROR: Validation exception: {error_message}"

def format_error_validation_failed_cannot_proceed():
    """Format validation failure message."""
    return "ERROR: Validation failed - cannot proceed with run"

# =============================================================================
# GENERATION - Master Orchestration
# =============================================================================

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

def format_metrics_retrieval_source_missing(bench_id, source):
    """Format metrics source missing."""
    return f"Metrics file not found for {bench_id}: {source}"

def format_metrics_retrieved(bench_id, source, dest):
    """Format metrics retrieved."""
    return f"Retrieved metrics for {bench_id}: {dest}"

def format_metrics_retrieval_failed(bench_id, error_message):
    """Format metrics retrieval failure."""
    return f"Failed to retrieve metrics for {bench_id}: {error_message}"

def format_fi_log_source_missing(bench_id, source):
    """Format FI log source missing."""
    return f"FI injection log not found for {bench_id}: {source}"

def format_fi_log_collected(bench_id, source, dest):
    """Format FI log collected."""
    return f"Collected FI log for {bench_id}: {dest}"

def format_fi_log_collection_failed(bench_id, error_message):
    """Format FI log collection failure."""
    return f"Failed to collect FI log for {bench_id}: {error_message}"

def format_yaml_copy_source_missing(source):
    """Format YAML source missing."""
    return f"YAML file not found: {source}"

def format_yaml_original_copied(source, dest):
    """Format original YAML copied."""
    return f"Copied original YAML: {dest}"

def format_yaml_verified_saved(dest):
    """Format verified YAML saved."""
    return f"Saved verified YAML: {dest}"

def format_yaml_copy_failed(source, error_message):
    """Format YAML copy failure."""
    return f"Failed to copy YAML from {source}: {error_message}"

def format_yaml_save_failed(dest, error_message):
    """Format YAML save failure."""
    return f"Failed to save YAML to {dest}: {error_message}"

# =============================================================================
# GENERATION - Phase Execution
# =============================================================================

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

# =============================================================================
# GENERATION - File-Level Events
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
# BUILD - Phase Execution
# =============================================================================

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

# =============================================================================
# BUILD - Command Execution
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
# FILE MOVEMENT
# =============================================================================

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
# EXECUTION - Phase Level
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
# EXECUTION - Benchmark/Session Level
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
    return f"\n{'*'*80}\n>>> Session #{session_id}: {benchmark}\n"

def format_session_complete(session_name, duration):
    """Format session completion."""
    return f">>> Session {session_name} complete ({duration:.1f}s)\n{'*'*80}\n"

def format_session_failed(session_name, error_message):
    """Format session failure."""
    return f"Session {session_name} FAILED: {error_message}"

def format_benchmark_discovery(benchmark_count, suite_name):
    """Format benchmark discovery."""
    return f"Discovered {benchmark_count} benchmarks in {suite_name}"

def format_fi_launch(command):
    """Format FI console launch."""
    return f"Launching FI console: {command}"

def format_fi_command_build_failed(error_message):
    """Format FI command build failure."""
    return f"Failed to build FI command: {error_message}"

def format_fi_command_built(command, output_log, timeout_s):
    """Format FI command built successfully."""
    lines = [
        "\nRunning FI COMMAND:",
        f"  Command: {command}\n"
    ]
    return "\n".join(lines)

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
# PBLOCKS
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

def format_pblock_script_not_found(script_path):
    """Format pblock script not found error."""
    return f"Pblock generation script not found: {script_path}"

def format_pblock_system_calling(command):
    """Format pblock system call."""
    return f"Calling external pblock system: {command}"

def format_pblock_system_success():
    """Format pblock system success."""
    return "External pblock system completed successfully"

def format_pblock_system_failed(return_code, stdout, stderr):
    """Format pblock system failure."""
    lines = [f"External pblock system failed (exit code: {return_code})"]
    if stderr:
        lines.append(f"Error: {stderr[:200]}")
    if stdout:
        lines.append(f"Output: {stdout[:200]}")
    return "\n".join(lines)

def format_pblock_system_timeout():
    """Format pblock system timeout."""
    return "External pblock system timed out (>60s)"

def format_pblock_system_error(error_message):
    """Format pblock system error."""
    return f"External pblock system error: {error_message}"

def format_pblock_output_missing(expected_file):
    """Format pblock output missing warning."""
    return f"Expected pblock output not created: {expected_file}"

def format_pblock_dict_missing(expected_file):
    """Format pblock dict missing warning."""
    return f"Pblock dictionary not created: {expected_file}"

def format_pblock_summary_missing(expected_file):
    """Format pblock summary missing warning."""
    return f"Pblock summary not created: {expected_file}"

# =============================================================================
# RESULTS - Phase Level
# =============================================================================

def format_results_phase_start():
    """Format results phase start."""
    return "Starting results collection and packaging..."

def format_results_session_collection_start():
    """Format session collection start."""
    return "Collecting session metrics..."

def format_results_no_sessions():
    """Format no sessions found."""
    return "No sessions found - skipping session metrics"

def format_results_session_metrics_collected(count):
    """Format session metrics collected."""
    return f"Collected metrics from {count} session(s)"

def format_results_sessions_found(session_count):
    """Format sessions found."""
    return f"Found {session_count} session(s) to process"

def format_results_build_collection_start():
    """Format build collection start."""
    return "Collecting build metrics..."

def format_results_build_metrics_collected():
    """Format build metrics collected."""
    return "Build metrics collected from Vivado reports"

def format_results_build_metrics_unavailable():
    """Format build metrics unavailable."""
    return "Build metrics unavailable - reports not found"

def format_results_aggregation_start():
    """Format aggregation start."""
    return "Aggregating metrics..."

def format_results_aggregation_complete(session_count):
    """Format aggregation complete."""
    return f"Metrics aggregated ({session_count} sessions)"

def format_results_summary_generation_start():
    """Format summary generation start."""
    return "Generating run summary..."

def format_results_summary_generated(summary_path):
    """Format summary generated."""
    return f"Run summary: {summary_path}"

def format_results_excel_export_start():
    """Format Excel export start."""
    return "Exporting to Excel..."

def format_results_excel_exported(excel_path):
    """Format Excel exported."""
    return f"Excel workbook: {excel_path}"

def format_results_excel_export_failed():
    """Format Excel export failed."""
    return "Excel export failed - openpyxl may not be available"

def format_results_csv_export_start():
    """Format CSV export start."""
    return "Exporting to CSV..."

def format_results_csv_exported(csv_count):
    """Format CSV exported."""
    return f"Exported {csv_count} CSV file(s)"

def format_results_validation_start(results_dir=None):
    """Format results validation start message."""
    if results_dir:
        return f"Validating results package: {results_dir}"
    else:
        return "Validating results package"

def format_results_validation_failed(error_count, errors):
    """Format validation failed."""
    errors_str = "; ".join(errors[:3])
    return f"Results validation failed: {error_count} error(s) - {errors_str}"

def format_results_validation_passed():
    """Format validation passed."""
    return "Results validation passed"

def format_results_validation_warnings(warning_count):
    """Format validation warnings."""
    return f"Results validation: {warning_count} warning(s)"

def format_results_phase_summary(results_dir, session_count, build_metrics_available, excel_generated, csv_count):
    """Format results phase summary."""
    return (
        f"Results complete:\n"
        f"  Directory: {results_dir}\n"
        f"  Sessions: {session_count}\n"
        f"  Build metrics: {'available' if build_metrics_available else 'unavailable'}\n"
        f"  Excel: {'generated' if excel_generated else 'not generated'}\n"
        f"  CSVs: {csv_count}"
    )

def format_results_phase_exception(error_message):
    """Format results phase exception."""
    return f"Results phase exception: {error_message}"

def format_results_traceback(traceback):
    """Format results traceback."""
    return f"Traceback:\n{traceback}"

def format_reports_copy_source_missing(source):
    """Format reports source missing."""
    return f"Reports directory not found: {source}"

def format_reports_copied(source, dest):
    """Format reports copied."""
    return f"Copied reports directory: {source} -> {dest}"

def format_reports_copy_failed(error_message):
    """Format reports copy failure."""
    return f"Failed to copy reports directory: {error_message}"

def format_vivado_parser_not_found(parser):
    """Format parser not found."""
    return f"Vivado parser not found: {parser}"

def format_vivado_parser_reports_missing(reports_dir):
    """Format parser reports missing."""
    return f"Reports directory missing for parser: {reports_dir}"

def format_vivado_parser_start(reports_dir, prefix=None):
    """Format parser start."""
    if prefix:
        return f"Running Vivado parser on: {reports_dir} (prefix: {prefix})"
    return f"Running Vivado parser on: {reports_dir}"

def format_vivado_parser_success(output, prefix=None):
    """Format parser success."""
    if prefix:
        return f"Vivado parser completed: {output} (prefix: {prefix})"
    return f"Vivado parser completed: {output}"

def format_vivado_parser_no_output(expected):
    """Format parser no output."""
    return f"Vivado parser ran but output file not found: {expected}"

def format_vivado_parser_failed(exit_code, stderr="(no stderr captured)"):
    """Format parser failure."""
    return f"Vivado parser failed (exit {exit_code}): {stderr}"

def format_vivado_parser_timeout():
    """Format parser timeout."""
    return "Vivado parser timed out (exceeded 5 minutes)"

def format_vivado_parser_exception(error_message):
    """Format parser exception."""
    return f"Vivado parser exception: {error_message}"

def format_vivado_parser_import_error(error_message):
    """Format parser import error."""
    return f"Vivado parser import error: {error_message}"

def format_vivado_parser_no_reports(reports_dir):
    """Format no reports found message."""
    return f"Vivado parser: no standard .rpt files found in {reports_dir}"

def format_vivado_parser_traceback(traceback):
    """Format parser traceback."""
    return f"Vivado parser traceback:\n{traceback}"

def format_bench_metrics_table_start():
    """Format bench metrics table generation start."""
    return "Generating benchmark metrics table..."

def format_bench_metrics_table_success(output, benchmark_count, metric_count,
                                        system_params, fi_params):
    """Format bench metrics table success."""
    return (f"Benchmark metrics table written: {output} "
            f"({benchmark_count} benchmarks, {metric_count} metrics, "
            f"{system_params} system params, {fi_params} FI params)")

def format_bench_metrics_table_failed():
    """Format bench metrics table failure."""
    return "Benchmark metrics table generation failed"

def format_bench_metrics_session_table_success(output, benchmark, metric_count):
    """Format per-session metrics_table.csv success."""
    return f"Session metrics table written: {output} ({benchmark}, {metric_count} metrics)"

# =============================================================================
# RESULTS - Generic
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

def format_results_run_dir_created(run_dir):
    """Format run directory creation."""
    return f"Created results directory: {run_dir}"

def format_results_structure_initialized(run_dir):
    """Format structure initialization."""
    return f"Initialized results structure: {run_dir}"

# =============================================================================
# PARSER
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
# CLI/UI
# =============================================================================

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
        "Running MAKE COMMAND:\n" +
        f"  Command: {command}\n"
    )

def format_cli_dry_run_start():
    """Format dry run start."""
    return "DRY RUN - Configuration preview only"

def format_dry_run_reminder():
    """Format dry-run reminder message."""
    return "\n  REMINDER: Run with '--restore-arch' to reset the system to its original state.\n"

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
# CONFIGURATION OVERRIDES
# =============================================================================

def format_override_start(override_count):
    """Format override processing start."""
    return f"Processing {override_count} configuration overrides..."

def format_override_applied(svh_file, source, dest):
    """Format SVH file override application."""
    return f"  Override: {svh_file} copied from {source} to {dest}"

def format_override_validation(override_key, status):
    """Format override validation."""
    return f"  Validated: {override_key} ({status})"

# =============================================================================
# RECOVERY
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

def format_arch_restore_start():
    """Format architecture restore start."""
    return "Starting architecture restoration from backup..."

def format_arch_restore_no_backup(backup_path):
    """Format no backup error."""
    return f"ERROR: No backup found at {backup_path}. Run a dry-run first or check tmp/backup/ exists."

def format_arch_restore_no_arch_dir(arch_path):
    """Format no architecture directory error."""
    return f"ERROR: Architecture directory not found: {arch_path}"

def format_arch_restore_removing_current(arch_path):
    """Format current architecture removal."""
    return f"Removing current architecture: {arch_path}"

def format_arch_restore_copying_backup(backup_path, arch_path):
    """Format backup copying."""
    return f"Restoring from backup: {backup_path} -> {arch_path}"

def format_arch_restore_success():
    """Format successful restoration."""
    return "Architecture restored successfully"

def format_arch_restore_failed(error_message):
    """Format restoration failure."""
    return f"Architecture restoration failed: {error_message}"

def format_arch_restore_cleanup_tmp(tmp_path):
    """Format tmp cleanup start."""
    return f"Cleaning tmp directory: {tmp_path}"

def format_arch_restore_tmp_cleaned():
    """Format tmp cleanup success."""
    return "Tmp directory cleaned"

def format_arch_restore_tmp_failed(error_message):
    """Format tmp cleanup failure."""
    return f"Tmp cleanup failed: {error_message}"

def format_arch_restore_workflow_start():
    """Format workflow start."""
    return (
        "=" * 80 + "\n" +
        "ARCHITECTURE RESTORATION\n" +
        "=" * 80
    )

def format_arch_restore_workflow_failed():
    """Format workflow failure."""
    return "Architecture restoration workflow failed"

def format_arch_restore_workflow_partial():
    """Format partial success."""
    return "Architecture restored but tmp cleanup failed"

def format_arch_restore_workflow_complete():
    """Format workflow completion."""
    return (
        "=" * 80 + "\n" +
        "Architecture restoration complete\n" +
        "=" * 80
    )

# =============================================================================
# MAPPING
# =============================================================================

def format_mapping_board(board_name, board_config):
    """Format board mapping."""
    return f"Board mapping: {board_name} -> {board_config}"

def format_mapping_isa(isa_extension, enabled):
    """Format ISA extension mapping."""
    status = "enabled" if enabled else "disabled"
    return f"ISA extension: {isa_extension} ({status})"

# =============================================================================
# USER VALIDATION
# =============================================================================
def format_user_validation_start(check_count):
    """Format message for start of user validation."""
    return f"  User validation: executing {check_count} custom checks..."

def format_user_validation_invalid_check(check_index):
    """Format message for invalid user validation check."""
    return f"  User check #{check_index}: invalid check definition (logic must be callable)"

def format_user_validation_check_error(check_index, error_message):
    """Format message for user validation check execution error."""
    return f"  User check #{check_index}: error during execution: {error_message}"

def format_user_validation_error(message):
    """Format message for user validation error."""
    return f"  User validation error: {message}"

def format_user_validation_warning(message):
    """Format message for user validation warning."""
    return f"  User validation warning: {message}"

def format_user_validation_correction_applied(message):
    """Format message for applied user validation correction."""
    return f"  Correction applied: {message}"

def format_user_validation_correction_failed(message, error_message):
    """Format message for failed user validation correction."""
    return f"  Correction failed for '{message}': {error_message}"

def format_user_validation_complete(errors, warnings, corrections):
    """Format message for user validation completion."""
    return f"  User validation complete: {errors} errors, {warnings} warnings, {corrections} corrections"

def format_user_validation_not_available():
    """Format message when user validation is not available."""
    return "  User validation: no custom checks defined (config/validation_checks.py not found)"

def format_user_validation_exception(error_message):
    """Format message for user validation exception."""
    return f"  User validation system error: {error_message}"

# =============================================================================
# SESSION RESULTS
# =============================================================================

def format_session_results_parse_error(metrics_path, error_message):
    """Format message for session metrics parse error."""
    return f"  Failed to parse metrics file {metrics_path}: {error_message}"

def format_session_results_no_metrics(bench_id, session_dir):
    """Format message when no metrics found for session."""
    return f"  No metrics found for session {bench_id} in {session_dir}"

def format_session_results_csv_generated(bench_id, output_path):
    """Format message for successful session CSV generation."""
    return f"  Generated session CSV for {bench_id}: {output_path}"

def format_session_results_csv_failed(bench_id, error_message):
    """Format message for failed session CSV generation."""
    return f"  Failed to generate session CSV for {bench_id}: {error_message}"

def format_session_results_xlsx_generated(bench_id, output_path):
    """Format message for successful session XLSX generation."""
    return f"  Generated session XLSX for {bench_id}: {output_path}"

def format_session_results_xlsx_failed(bench_id, error_message):
    """Format message for failed session XLSX generation."""
    return f"  Failed to generate session XLSX for {bench_id}: {error_message}"

def format_session_results_xlsx_unavailable():
    """Format message when XLSX library is not available."""
    return "  XLSX export unavailable (openpyxl not installed)"

def format_session_results_no_sessions_dir(sessions_dir):
    """Format message when sessions directory doesn't exist."""
    return f"  Sessions directory not found: {sessions_dir}"

def format_session_results_generation_complete(session_count):
    """Format message for completion of session results generation."""
    return f"  Session results generation complete: {session_count} sessions processed"

# =============================================================================
# RUN RESULTS
# =============================================================================

def format_run_results_no_vivado_metrics(parsed_path):
    """Format message when vivado metrics file not found."""
    return f"  Vivado metrics not found: {parsed_path}"

def format_run_results_vivado_load_error(error_message):
    """Format message for vivado metrics load error."""
    return f"  Failed to load vivado metrics: {error_message}"

def format_run_results_csv_generated(run_id=None, output_path=None, output=None):
    """Format run results CSV generated message."""
    # Support both 'output_path' and 'output' parameter names
    path = output_path if output_path else output
    if path:
        return f"Run results CSV generated: {path}"
    else:
        return "Run results CSV generated"


def format_run_results_xlsx_generated(run_id=None, output_path=None, output=None):
    """Format run results XLSX generated message."""
    # Support both 'output_path' and 'output' parameter names
    path = output_path if output_path else output
    if path:
        return f"Run results XLSX generated: {path}"
    else:
        return "Run results XLSX generated"

def format_run_results_csv_failed(run_id, error_message):
    """Format message for failed run CSV generation."""
    return f"  Failed to generate run results CSV for {run_id}: {error_message}"

def format_run_results_xlsx_failed(run_id, error_message):
    """Format message for failed run XLSX generation."""
    return f"  Failed to generate run XLSX for {run_id}: {error_message}"

def format_run_results_xlsx_unavailable():
    """Format message when XLSX library is not available."""
    return "  XLSX export unavailable (openpyxl not installed)"

# =============================================================================
# CLEANUP
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

def format_cleanup_skip_dry_run(tmp_dir):
    """Format dry-run cleanup skip message."""
    return f"Skipping tmp/ cleanup in dry-run mode: {tmp_dir}"

def format_cleanup_preserving_tmp(tmp_dir):
    """Format tmp preservation message."""
    return f"Preserving tmp/ directory for debugging: {tmp_dir}"

def format_cleanup_tmp_cleaned():
    """Format tmp cleaned message."""
    return "Temporary directory cleaned"

def format_cleanup_tmp_failed(error_message):
    """Format tmp cleanup failure."""
    return f"Failed to clean tmp/ directory: {error_message}"

def format_debug_tmp_dir_not_exists():
    """Format debug message for missing tmp dir."""
    return "Tmp directory does not exist, skipping cleanup"

# =============================================================================
# SETUP
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
# SYSTEM/ENVIRONMENT
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
# MULTI-RUN
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
# ERRORS AND WARNINGS
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

# =============================================================================
# FORMAT FUNCTION REGISTRY
# All format functions must be registered here for the logger to find them.
# =============================================================================

FORMAT_FUNCTIONS = {
    # Run lifecycle
    'RUN_START': format_run_start,
    'RUN_END': format_run_end,
    'RUN_FAILED': format_run_failed,
    'FATORI_START': format_fatori_start,
    'FATORI_END': format_fatori_end,
    
    # Phase lifecycle
    'PHASE_START': format_phase_start,
    'PHASE_END': format_phase_end,
    'PHASE_FAILED': format_phase_failed,
    
    # Validation - Core
    'VALIDATION_START': format_validation_start,
    'VALIDATION_END': format_validation_end,
    'VALIDATION_ERROR': format_validation_error,
    'VALIDATION_WARNING': format_validation_warning,
    'VALIDATION_ERROR_MISSING_FIELD': format_validation_error_missing_field,
    'VALIDATION_ERROR_INVALID_VALUE': format_validation_error_invalid_value,
    'VALIDATION_WARNING_DEPRECATED': format_validation_warning_deprecated,
    'VALIDATION_AUTO_CORRECTION': format_validation_auto_correction,
    'VALIDATION_COMPLETE_NO_ISSUES': format_validation_complete_no_issues,
    
    # Validation - Phase
    'VALIDATION_PHASE_EXECUTING': format_validation_phase_executing,
    'VALIDATION_PHASE_PASSED': format_validation_phase_passed,
    'VALIDATION_PHASE_FAILED': format_validation_phase_failed,
    'VALIDATION_PHASE_WARNINGS': format_validation_phase_warnings,
    
    # Validation - Detailed Display
    'VALIDATION_START_FULL': format_validation_start_full,
    'VALIDATION_STRICT_MODE': format_validation_strict_mode,
    'VALIDATION_SUMMARY_START': format_validation_summary_start,
    'VALIDATION_SUMMARY_END': format_validation_summary_end,
    'VALIDATION_CONFIG_VALID': format_validation_config_valid,
    'VALIDATION_ERROR_COUNT': format_validation_error_count,
    'VALIDATION_ERROR_ITEM': format_validation_error_item,
    'VALIDATION_ERROR_MORE': format_validation_error_more,
    'VALIDATION_WARNING_COUNT': format_validation_warning_count,
    'VALIDATION_WARNING_ITEM': format_validation_warning_item,
    'VALIDATION_WARNING_MORE': format_validation_warning_more,
    'VALIDATION_CORRECTIONS_APPLIED': format_validation_corrections_applied,
    'ERROR_VALIDATION_EXCEPTION': format_error_validation_exception,
    'ERROR_VALIDATION_FAILED_CANNOT_PROCEED': format_error_validation_failed_cannot_proceed,
    
    # Generation - Master
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
    
    # Generation - Phase
    'GENERATION_PHASE_EXECUTING': format_generation_phase_executing,
    'GENERATION_PHASE_COMPLETE': format_generation_phase_complete,
    'GENERATION_PHASE_VALIDATION_FAILED': format_generation_phase_validation_failed,
    'GENERATION_PHASE_ERROR': format_generation_phase_error,
    
    # Generation - Files
    'GENERATION_START': format_generation_start,
    'GENERATION_END': format_generation_end,
    'FILE_GENERATED': format_file_generated,
    'SVH_GENERATION': format_svh_generation,
    'TCL_GENERATION': format_tcl_generation,
    'FEATURES_GENERATION_START': format_features_generation_start,
    'FEATURES_GENERATION_END': format_features_generation_end,
    'FTM_GENERATION_START': format_ftm_generation_start,
    'FTM_GENERATION_END': format_ftm_generation_end,
    
    # Build - Phase
    'BUILD_PHASE_EXECUTING': format_build_phase_executing,
    'BUILD_PHASE_CONFIG': format_build_phase_config,
    'BUILD_PHASE_SUCCESS': format_build_phase_success,
    'BUILD_PHASE_FAILED': format_build_phase_failed,
    'BUILD_PHASE_EXCEPTION': format_build_phase_exception,
    'BUILD_ERRORS_SUMMARY': format_build_errors_summary,
    'BUILD_LOG_LOCATION': format_build_log_location,
    'BUILD_BITSTREAM_READY': format_build_bitstream_ready,
    
    # Build - Commands
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
    
    # File Movement
    'FILE_MOVEMENT_PHASE_EXECUTING': format_file_movement_phase_executing,
    'FILE_MOVEMENT_COMPLETE': format_file_movement_complete,
    'FILE_MOVEMENT_NO_FILES': format_file_movement_no_files,
    'FILE_MOVEMENT_ERROR': format_file_movement_error,
    'TCL_INPUTS_COPIED': format_tcl_inputs_copied,
    'FILE_MOVEMENT_START': format_file_movement_start,
    'FILE_MOVEMENT_END': format_file_movement_end,
    'FILE_ALLOCATED': format_file_allocated,
    'FILE_BACKUP': format_file_backup,
    'FILE_COPY': format_file_copy,
    
    # Execution - Phase
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
    
    # Execution - Benchmarks
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
    'FI_COMMAND_BUILD_FAILED': format_fi_command_build_failed,
    'FI_COMMAND_BUILT': format_fi_command_built,
    'FI_COMPLETE': format_fi_complete,
    'FI_ERROR': format_fi_error,
    'CONSOLE_OUTPUT': format_console_output,
    
    # Pblocks
    'PBLOCK_CONFIG_CREATED': format_pblock_config_created,
    'PBLOCK_GENERATION_START': format_pblock_generation_start,
    'PBLOCK_GENERATION_END': format_pblock_generation_end,
    'PBLOCK_GENERATION_COMPLETE': format_pblock_generation_complete,
    'PBLOCK_MODULE_PROCESSED': format_pblock_module_processed,
    'PBLOCK_TCL_GENERATED': format_pblock_tcl_generated,
    'PBLOCK_SCRIPT_NOT_FOUND': format_pblock_script_not_found,
    'PBLOCK_SYSTEM_CALLING': format_pblock_system_calling,
    'PBLOCK_SYSTEM_SUCCESS': format_pblock_system_success,
    'PBLOCK_SYSTEM_FAILED': format_pblock_system_failed,
    'PBLOCK_SYSTEM_TIMEOUT': format_pblock_system_timeout,
    'PBLOCK_SYSTEM_ERROR': format_pblock_system_error,
    'PBLOCK_OUTPUT_MISSING': format_pblock_output_missing,
    'PBLOCK_DICT_MISSING': format_pblock_dict_missing,
    'PBLOCK_SUMMARY_MISSING': format_pblock_summary_missing,
    
    # Results - Phase
    'RESULTS_PHASE_START': format_results_phase_start,
    'RESULTS_SESSION_COLLECTION_START': format_results_session_collection_start,
    'RESULTS_NO_SESSIONS': format_results_no_sessions,
    'RESULTS_SESSION_METRICS_COLLECTED': format_results_session_metrics_collected,
    'RESULTS_SESSIONS_FOUND': format_results_sessions_found,
    'RESULTS_BUILD_COLLECTION_START': format_results_build_collection_start,
    'RESULTS_BUILD_METRICS_COLLECTED': format_results_build_metrics_collected,
    'RESULTS_BUILD_METRICS_UNAVAILABLE': format_results_build_metrics_unavailable,
    'RESULTS_AGGREGATION_START': format_results_aggregation_start,
    'RESULTS_AGGREGATION_COMPLETE': format_results_aggregation_complete,
    'RESULTS_SUMMARY_GENERATION_START': format_results_summary_generation_start,
    'RESULTS_SUMMARY_GENERATED': format_results_summary_generated,
    'RESULTS_EXCEL_EXPORT_START': format_results_excel_export_start,
    'RESULTS_EXCEL_EXPORTED': format_results_excel_exported,
    'RESULTS_EXCEL_EXPORT_FAILED': format_results_excel_export_failed,
    'RESULTS_CSV_EXPORT_START': format_results_csv_export_start,
    'RESULTS_CSV_EXPORTED': format_results_csv_exported,
    'RESULTS_VALIDATION_START': format_results_validation_start,
    'RESULTS_VALIDATION_FAILED': format_results_validation_failed,
    'RESULTS_VALIDATION_PASSED': format_results_validation_passed,
    'RESULTS_VALIDATION_WARNINGS': format_results_validation_warnings,
    'RESULTS_PHASE_SUMMARY': format_results_phase_summary,
    'RESULTS_PHASE_EXCEPTION': format_results_phase_exception,
    'RESULTS_TRACEBACK': format_results_traceback,
    
    # Results - Generic
    'RESULTS_START': format_results_start,
    'RESULTS_END': format_results_end,
    'RESULTS_SUMMARY': format_results_summary,
    'RESULTS_FILE_CREATED': format_results_file_created,
    'RESULTS_METRICS_COLLECTED': format_results_metrics_collected,
    'RESULTS_RUN_DIR_CREATED': format_results_run_dir_created,
    'RESULTS_STRUCTURE_INITIALIZED': format_results_structure_initialized,

    # Results - Metrics & Logs
    'METRICS_RETRIEVAL_SOURCE_MISSING': format_metrics_retrieval_source_missing,
    'METRICS_RETRIEVED': format_metrics_retrieved,
    'METRICS_RETRIEVAL_FAILED': format_metrics_retrieval_failed,
    'FI_LOG_SOURCE_MISSING': format_fi_log_source_missing,
    'FI_LOG_COLLECTED': format_fi_log_collected,
    'FI_LOG_COLLECTION_FAILED': format_fi_log_collection_failed,
    'YAML_COPY_SOURCE_MISSING': format_yaml_copy_source_missing,
    'YAML_ORIGINAL_COPIED': format_yaml_original_copied,
    'YAML_VERIFIED_SAVED': format_yaml_verified_saved,
    'YAML_COPY_FAILED': format_yaml_copy_failed,
    'YAML_SAVE_FAILED': format_yaml_save_failed,
    'REPORTS_COPY_SOURCE_MISSING': format_reports_copy_source_missing,
    'REPORTS_COPIED': format_reports_copied,
    'REPORTS_COPY_FAILED': format_reports_copy_failed,
    'VIVADO_PARSER_NOT_FOUND': format_vivado_parser_not_found,
    'VIVADO_PARSER_REPORTS_MISSING': format_vivado_parser_reports_missing,
    'VIVADO_PARSER_START': format_vivado_parser_start,
    'VIVADO_PARSER_SUCCESS': format_vivado_parser_success,
    'VIVADO_PARSER_NO_OUTPUT': format_vivado_parser_no_output,
    'VIVADO_PARSER_FAILED': format_vivado_parser_failed,
    'VIVADO_PARSER_TIMEOUT': format_vivado_parser_timeout,
    'VIVADO_PARSER_EXCEPTION': format_vivado_parser_exception,
    'VIVADO_PARSER_IMPORT_ERROR': format_vivado_parser_import_error,
    'VIVADO_PARSER_NO_REPORTS': format_vivado_parser_no_reports,
    'VIVADO_PARSER_TRACEBACK': format_vivado_parser_traceback,

    # Bench metrics table
    'BENCH_METRICS_TABLE_START': format_bench_metrics_table_start,
    'BENCH_METRICS_TABLE_SUCCESS': format_bench_metrics_table_success,
    'BENCH_METRICS_TABLE_FAILED': format_bench_metrics_table_failed,
    'BENCH_METRICS_SESSION_TABLE_SUCCESS': format_bench_metrics_session_table_success,

    # User Validation
    'USER_VALIDATION_START': format_user_validation_start,
    'USER_VALIDATION_INVALID_CHECK': format_user_validation_invalid_check,
    'USER_VALIDATION_CHECK_ERROR': format_user_validation_check_error,
    'USER_VALIDATION_ERROR': format_user_validation_error,
    'USER_VALIDATION_WARNING': format_user_validation_warning,
    'USER_VALIDATION_CORRECTION_APPLIED': format_user_validation_correction_applied,
    'USER_VALIDATION_CORRECTION_FAILED': format_user_validation_correction_failed,
    'USER_VALIDATION_COMPLETE': format_user_validation_complete,
    'USER_VALIDATION_NOT_AVAILABLE': format_user_validation_not_available,
    'USER_VALIDATION_EXCEPTION': format_user_validation_exception,
    
    # Session Results
    'SESSION_RESULTS_PARSE_ERROR': format_session_results_parse_error,
    'SESSION_RESULTS_NO_METRICS': format_session_results_no_metrics,
    'SESSION_RESULTS_CSV_GENERATED': format_session_results_csv_generated,
    'SESSION_RESULTS_CSV_FAILED': format_session_results_csv_failed,
    'SESSION_RESULTS_XLSX_GENERATED': format_session_results_xlsx_generated,
    'SESSION_RESULTS_XLSX_FAILED': format_session_results_xlsx_failed,
    'SESSION_RESULTS_XLSX_UNAVAILABLE': format_session_results_xlsx_unavailable,
    'SESSION_RESULTS_NO_SESSIONS_DIR': format_session_results_no_sessions_dir,
    'SESSION_RESULTS_GENERATION_COMPLETE': format_session_results_generation_complete,
    
    # Run Results
    'RUN_RESULTS_NO_VIVADO_METRICS': format_run_results_no_vivado_metrics,
    'RUN_RESULTS_VIVADO_LOAD_ERROR': format_run_results_vivado_load_error,
    'RUN_RESULTS_CSV_GENERATED': format_run_results_csv_generated,
    'RUN_RESULTS_CSV_FAILED': format_run_results_csv_failed,
    'RUN_RESULTS_XLSX_GENERATED': format_run_results_xlsx_generated,
    'RUN_RESULTS_XLSX_FAILED': format_run_results_xlsx_failed,
    'RUN_RESULTS_XLSX_UNAVAILABLE': format_run_results_xlsx_unavailable,
    
    # Parser
    'PARSER_START': format_parser_start,
    'PARSER_REPORT_PARSED': format_parser_report_parsed,
    'PARSER_COMPLETE': format_parser_complete,
    'PARSER_ERROR_REPORT_MISSING': format_parser_error_report_missing,
    'PARSER_ERROR_PARSE_FAILED': format_parser_error_parse_failed,
    'PARSER_METRICS_EXTRACTED': format_parser_metrics_extracted,
    
    # CLI/UI
    'DRY_RUN_MODE_ENABLED': format_dry_run_mode_enabled,
    'DRY_RUN_COMMAND': format_dry_run_command,
    'CLI_DRY_RUN_START': format_cli_dry_run_start,
    'DRY_RUN_REMINDER': format_dry_run_reminder,
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
    
    # Architecture Restoration
    'ARCH_RESTORE_START': format_arch_restore_start,
    'ARCH_RESTORE_NO_BACKUP': format_arch_restore_no_backup,
    'ARCH_RESTORE_NO_ARCH_DIR': format_arch_restore_no_arch_dir,
    'ARCH_RESTORE_REMOVING_CURRENT': format_arch_restore_removing_current,
    'ARCH_RESTORE_COPYING_BACKUP': format_arch_restore_copying_backup,
    'ARCH_RESTORE_SUCCESS': format_arch_restore_success,
    'ARCH_RESTORE_FAILED': format_arch_restore_failed,
    'ARCH_RESTORE_CLEANUP_TMP': format_arch_restore_cleanup_tmp,
    'ARCH_RESTORE_TMP_CLEANED': format_arch_restore_tmp_cleaned,
    'ARCH_RESTORE_TMP_FAILED': format_arch_restore_tmp_failed,
    'ARCH_RESTORE_WORKFLOW_START': format_arch_restore_workflow_start,
    'ARCH_RESTORE_WORKFLOW_FAILED': format_arch_restore_workflow_failed,
    'ARCH_RESTORE_WORKFLOW_PARTIAL': format_arch_restore_workflow_partial,
    'ARCH_RESTORE_WORKFLOW_COMPLETE': format_arch_restore_workflow_complete,
    
    # Mapping
    'MAPPING_BOARD': format_mapping_board,
    'MAPPING_ISA': format_mapping_isa,
    
    # Cleanup
    'CLEANUP_START': format_cleanup_start,
    'CLEANUP_END': format_cleanup_end,
    'CLEANUP_TMP_DIR': format_cleanup_tmp_dir,
    'CLEANUP_SKIP_DRY_RUN': format_cleanup_skip_dry_run,
    'CLEANUP_PRESERVING_TMP': format_cleanup_preserving_tmp,
    'CLEANUP_TMP_CLEANED': format_cleanup_tmp_cleaned,
    'CLEANUP_TMP_FAILED': format_cleanup_tmp_failed,
    'DEBUG_TMP_DIR_NOT_EXISTS': format_debug_tmp_dir_not_exists,
    
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