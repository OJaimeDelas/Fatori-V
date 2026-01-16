# =============================================================================
# FATORI-V • Run Phase Definitions
# File: run_phases.py
# -----------------------------------------------------------------------------
# Defines all phases in the FATORI-V execution workflow.
# =============================================================================

from enum import Enum
from typing import List, Dict


class RunPhase:
    """
    Enumeration of all phases in a FATORI-V run.
    
    Each phase represents a major step in the workflow from
    configuration validation through results packaging.
    """
    VALIDATION = "validation"
    GENERATION = "generation"
    FILE_MOVEMENT = "file_movement"
    BUILD = "build"
    EXECUTION = "execution"
    RESULTS = "results"


# Phase execution order
PHASE_ORDER: List[str] = [
    RunPhase.VALIDATION,
    RunPhase.GENERATION,
    RunPhase.FILE_MOVEMENT,
    RunPhase.BUILD,
    RunPhase.EXECUTION,
    RunPhase.RESULTS,
]


# Human-readable phase descriptions
PHASE_DESCRIPTIONS: Dict[str, str] = {
    RunPhase.VALIDATION: "Validate configuration and check consistency",
    RunPhase.GENERATION: "Generate hardware files (SystemVerilog, TCL)",
    RunPhase.FILE_MOVEMENT: "Allocate files to target locations",
    RunPhase.BUILD: "Build FPGA bitstream",
    RunPhase.EXECUTION: "Execute benchmarks and collect metrics",
    RunPhase.RESULTS: "Aggregate results and generate reports",
}


# Phase dependencies (which phases must complete before this one)
PHASE_DEPENDENCIES: Dict[str, List[str]] = {
    RunPhase.VALIDATION: [],  # No dependencies
    RunPhase.GENERATION: [RunPhase.VALIDATION],
    RunPhase.FILE_MOVEMENT: [RunPhase.GENERATION],
    RunPhase.BUILD: [RunPhase.FILE_MOVEMENT],
    RunPhase.EXECUTION: [RunPhase.BUILD],
    RunPhase.RESULTS: [RunPhase.EXECUTION],
}


# Optional phases (can be skipped based on configuration)
OPTIONAL_PHASES: List[str] = []


def is_valid_phase(phase_name: str) -> bool:
    """
    Check if a phase name is valid.
    
    Args:
        phase_name: Phase name to check
    
    Returns:
        Boolean indicating if phase is valid
    """
    return phase_name in PHASE_ORDER


def get_phase_index(phase_name: str) -> int:
    """
    Get the index of a phase in the execution order.
    
    Args:
        phase_name: Phase name
    
    Returns:
        Index in PHASE_ORDER, or -1 if not found
    """
    try:
        return PHASE_ORDER.index(phase_name)
    except ValueError:
        return -1


def get_next_phase(current_phase: str) -> str:
    """
    Get the next phase after the current one.
    
    Args:
        current_phase: Current phase name
    
    Returns:
        Next phase name, or None if current is the last phase
    """
    index = get_phase_index(current_phase)
    
    if index == -1:
        return None
    
    if index >= len(PHASE_ORDER) - 1:
        return None  # Already at last phase
    
    return PHASE_ORDER[index + 1]


def get_phase_description(phase_name: str) -> str:
    """
    Get human-readable description of a phase.
    
    Args:
        phase_name: Phase name
    
    Returns:
        Description string
    """
    return PHASE_DESCRIPTIONS.get(phase_name, "Unknown phase")


def check_dependencies_met(phase_name: str, completed_phases: List[str]) -> bool:
    """
    Check if all dependencies for a phase have been completed.
    
    Args:
        phase_name: Phase to check dependencies for
        completed_phases: List of phases that have been completed
    
    Returns:
        Boolean indicating if dependencies are met
    """
    dependencies = PHASE_DEPENDENCIES.get(phase_name, [])
    
    for dep in dependencies:
        if dep not in completed_phases:
            return False
    
    return True


def get_missing_dependencies(phase_name: str, completed_phases: List[str]) -> List[str]:
    """
    Get list of missing dependencies for a phase.
    
    Args:
        phase_name: Phase to check
        completed_phases: List of phases that have been completed
    
    Returns:
        List of missing dependency phase names
    """
    dependencies = PHASE_DEPENDENCIES.get(phase_name, [])
    
    missing = []
    for dep in dependencies:
        if dep not in completed_phases:
            missing.append(dep)
    
    return missing