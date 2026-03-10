# =============================================================================
# FATORI-V • Generation Phase Executor
# File: phase_generation.py
# -----------------------------------------------------------------------------
# Executes hardware file generation phase.
# =============================================================================

from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.orchestration.generate_all import generate_all_files
from scripts.logging.logger import log_event
import fatori_settings as cfg
import shutil


def execute_generation_phase(context: RunContext) -> bool:
    """
    Execute generation phase.
    
    This generates all hardware files including:
    - SystemVerilog headers (.svh)
    - Pblock configuration files
    - TCL scripts for Vivado
    - System integration files
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if generation succeeded
    """
    log_event('GENERATION_PHASE_EXECUTING')
    
    try:
        # Generate all files
        generation_result = generate_all_files(context.config)
        
        # Check if generation was valid
        if not generation_result.get('valid', False):
            log_event('GENERATION_PHASE_VALIDATION_FAILED')
            return False
        
        # Log summary of generated files
        svh_headers = generation_result.get('svh_headers', {})
        pblock_files = generation_result.get('pblock_files', {})
        tcl_scripts = generation_result.get('tcl_scripts', {})
        system_files = generation_result.get('system_files', {})
        
        total_files = (
            len([v for v in svh_headers.values() if v]) +
            len([v for v in pblock_files.values() if v]) +
            len([v for v in tcl_scripts.values() if v]) +
            len([v for v in system_files.values() if v])
        )
        
        log_event('GENERATION_PHASE_COMPLETE',
                  total_files=total_files,
                  svh_count=len(svh_headers),
                  pblock_count=len([v for v in pblock_files.values() if v]),
                  tcl_count=len(tcl_scripts),
                  system_count=len(system_files))
        
        # Immediately copy generated files to results/gen/ for preservation
        import shutil
        log_event('GENERATION_COPYING_TO_RESULTS')
        
        gen_source_dir = cfg.ROOT_DIR / 'tmp' / 'generated'
        
        if gen_source_dir.exists():
            run_gen_dir = context.results_dir / 'gen'
            run_gen_dir.mkdir(parents=True, exist_ok=True)
            
            copied_count = 0
            bench_configs_count = 0
            
            for gen_file in gen_source_dir.iterdir():
                if not gen_file.is_file():
                    continue
                
                # Check if benchmark-specific config file
                if gen_file.name.startswith('bench_config_') and gen_file.name.endswith('.h'):
                    bench_name = gen_file.name.replace('bench_config_', '').replace('.h', '')
                    session_gen_dir = context.results_dir / 'sessions' / bench_name / 'gen'
                    session_gen_dir.mkdir(parents=True, exist_ok=True)
                    dest_file = session_gen_dir / gen_file.name
                    shutil.copy2(gen_file, dest_file)
                    bench_configs_count += 1
                else:
                    dest_file = run_gen_dir / gen_file.name
                    shutil.copy2(gen_file, dest_file)
                    copied_count += 1
            
            log_event('GENERATION_FILES_COPIED_TO_RESULTS',
                      run_level_count=copied_count,
                      benchmark_configs_count=bench_configs_count)
        
        # Copy TCL files to results/gen/tcl/
        tcl_source_dir = cfg.ROOT_DIR / 'tmp' / 'tcl'
        
        if tcl_source_dir.exists():
            tcl_dest_dir = context.results_dir / 'gen' / 'tcl'
            tcl_dest_dir.mkdir(parents=True, exist_ok=True)
            
            tcl_copied_count = 0
            for tcl_file in tcl_source_dir.iterdir():
                if tcl_file.is_file() and tcl_file.suffix == '.tcl':
                    dest_file = tcl_dest_dir / tcl_file.name
                    shutil.copy2(tcl_file, dest_file)
                    tcl_copied_count += 1
            
            log_event('GENERATION_TCL_FILES_COPIED_TO_RESULTS', count=tcl_copied_count)
        
        return True
    
    except Exception as e:
        log_event('GENERATION_PHASE_ERROR', error_message=str(e))
        return False


class GenerationPhaseExecutor(PhaseExecutor):
    """
    Executor for generation phase.
    """
    
    def __init__(self):
        super().__init__("generation")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute generation phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_generation_phase(context)