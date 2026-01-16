# =============================================================================
# FATORI-V • File Movement Phase Executor
# File: phase_file_movement.py
# -----------------------------------------------------------------------------
# Executes file allocation phase.
# =============================================================================

import shutil
from pathlib import Path
import fatori_settings as cfg
from config.constants import SEM_GEN_TCL, REPORT_GEN_TCL
from scripts.phases.phase_executor import PhaseExecutor
from scripts.orchestration.run_context import RunContext
from scripts.build.file_allocator import allocate_files
from scripts.logging.logger import log_event


def copy_tcl_input_scripts():
    """
    Copy TCL input scripts from inputs/tcl/ to tmp/tcl/.
    
    These scripts (sem_gen.tcl, report_gen.tcl) are sourced by
    the generated Vivado hook files.
    """
    src_dir = cfg.INPUTS_TCL_DIR
    dst_dir = cfg.TMP_TCL_DIR
    
    # Ensure destination directory exists
    dst_dir.mkdir(parents=True, exist_ok=True)
    
    copied_files = []
    
    # Copy sem_gen.tcl (if exists)
    src_sem = src_dir / SEM_GEN_TCL
    if src_sem.exists():
        dst_sem = dst_dir / SEM_GEN_TCL
        shutil.copy2(src_sem, dst_sem)
        copied_files.append(SEM_GEN_TCL)
    
    # Copy report_gen.tcl (if exists)
    src_report = src_dir / REPORT_GEN_TCL
    if src_report.exists():
        dst_report = dst_dir / REPORT_GEN_TCL
        shutil.copy2(src_report, dst_report)
        copied_files.append(REPORT_GEN_TCL)
    
    return copied_files


def execute_file_movement_phase(context: RunContext) -> bool:
    """
    Execute file movement phase.
    
    This allocates generated and static files to the architecture tree:
    - Generated .svh files → architecture/hardware/...
    - TCL scripts → architecture/hardware/fpga/vivado/tcl/
    - Static hardware files → various architecture locations
    - Static software files → various architecture locations
    
    Additionally copies TCL input scripts to tmp/tcl/ for sourcing.
    
    Args:
        context: Run context with configuration
    
    Returns:
        Boolean indicating if file movement succeeded
    """
    log_event('FILE_MOVEMENT_PHASE_EXECUTING')
    
    try:
        # Copy TCL input scripts first
        tcl_inputs = copy_tcl_input_scripts()
        if tcl_inputs:
            log_event('TCL_INPUTS_COPIED', file_count=len(tcl_inputs))
        
        # Allocate all files with backup enabled
        allocated_files = allocate_files(context.config, backup_enabled=True)
        
        # Verify files were allocated
        generated_count = len(allocated_files.get('generated', []))
        tcl_count = len(allocated_files.get('tcl', []))
        static_count = len(allocated_files.get('static', []))
        
        total_allocated = generated_count + tcl_count + static_count
        
        if total_allocated == 0:
            log_event('FILE_MOVEMENT_NO_FILES')
            return False
        
        log_event('FILE_MOVEMENT_COMPLETE',
                  total_files=total_allocated,
                  generated_count=generated_count,
                  tcl_count=tcl_count,
                  static_count=static_count)
        
        return True
    
    except Exception as e:
        log_event('FILE_MOVEMENT_ERROR', error_message=str(e))
        return False


class FileMovementPhaseExecutor(PhaseExecutor):
    """
    Executor for file movement phase.
    """
    
    def __init__(self):
        super().__init__("file_movement")
    
    def execute(self, context: RunContext) -> bool:
        """
        Execute file movement phase.
        
        Args:
            context: Run context
        
        Returns:
            Boolean indicating success
        """
        return execute_file_movement_phase(context)