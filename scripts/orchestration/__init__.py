# =============================================================================
# FATORI-V • Orchestration
# File: __init__.py
# -----------------------------------------------------------------------------
# High-level run orchestration and state management.
# =============================================================================

# Import main orchestration components for convenience
from .run_controller import RunController
from .run_context import RunContext
from .run_state import RunState
from .run_phases import RunPhase, PHASE_ORDER