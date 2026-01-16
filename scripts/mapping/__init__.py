# =============================================================================
# FATORI-V • Mappings Module
# File: __init__.py
# -----------------------------------------------------------------------------
# Centralized name mappings for YAML to implementation translations.
# =============================================================================

from scripts.mapping.board_mapping import (
    get_make_board_name,
    is_valid_board,
)

from scripts.mapping.isa_mapping import (
    get_multiplier_enum,
    get_bit_manip_enum,
    get_regfile_enum,
    requires_use_mul_div,
    requires_use_compressed,
)

from scripts.mapping.feature_mapping import (
    get_feature_macro_name,
    get_ftm_macro_name,
    get_ft_layer_macro,
)

from scripts.mapping.pblock_mapping import (
    get_pblock_macro_name,
    is_conditional_target,
    get_target_condition,
    get_all_targets,
    get_default_targets,
)

from scripts.mapping.benchmark_mapping import (
    get_iterations_macro,
    get_fatori_stress_target_macros,
    get_embench_subbench_macros,
    is_embench_iot,
    is_fatori_stress,
)

__all__ = [
    # Board mapping
    "get_make_board_name",
    "is_valid_board",
    # ISA mapping
    "get_multiplier_enum",
    "get_bit_manip_enum",
    "get_regfile_enum",
    "requires_use_mul_div",
    "requires_use_compressed",
    # Feature mapping
    "get_feature_macro_name",
    "get_ftm_macro_name",
    "get_ft_layer_macro",
    # Pblock mapping
    "get_pblock_macro_name",
    "is_conditional_target",
    "get_target_condition",
    "get_all_targets",
    "get_default_targets",
    # Benchmark mapping
    "get_iterations_macro",
    "get_fatori_stress_target_macros",
    "get_embench_subbench_macros",
    "is_embench_iot",
    "is_fatori_stress",
]