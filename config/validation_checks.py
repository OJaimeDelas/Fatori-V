# =============================================================================
# FATORI-V • Configuration • User Validation Checks
# File: validation_checks.py
# -----------------------------------------------------------------------------
# User-definable validation checks with corrections.
# =============================================================================

from scripts.common.yaml_io.yaml_helpers import get_nested, is_enabled
from scripts.common.common_settings import *


def validation_sequence():
    """
    Define sequence of user validation checks.
    
    Users can add custom validation checks here following this format:
    
    {
        'type': 'warning' or 'error',
        'logic': lambda config: <boolean condition>,
        'message': <string or lambda>,
        'correction': <correction function or None>
    }
    
    Returns:
        List of validation check dictionaries
    """
    checks = []
    
    # # Example check 1: RV32M enabled but multiplier disabled
    # checks.append({
    #     'type': 'warning',
    #     'logic': lambda config: (
    #         get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M, default=False) and
    #         get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER, default='none') == 'none'
    #     ),
    #     'message': 'RV32M extension enabled but hardware multiplier is disabled. Performance may be poor.',
    #     'correction': None  # No automatic correction
    # })
    
    # Example check 2: ICache ECC without ICache
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'icache_ecc', default=False) and
            not get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'icache', default=False)
        ),
        'message': 'ICache ECC enabled but ICache is disabled. Disabling ICache ECC.',
        'correction': lambda config: config.get(KEY_SPECIFICS, {}).get(KEY_SPEC_IBEX, {}).update({'icache_ecc': "off"})
    })
    
    # Example check 3: MemECC enabled (error)
    checks.append({
        'type': 'warning',
        'logic': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'mem_ecc', default=False),
        'message': 'MemECC is enabled but not supported. Disabling it.',
        'correction': lambda config: config.get(KEY_SPECIFICS, {}).get(KEY_SPEC_IBEX, {}).update({'mem_ecc': "off"})
    })
    
    # Example check 4: Lockstep + Shadow CSRs
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'lockstep', default=False) and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'shadow_csrs', default=False)
        ),
        'message': 'Lockstep and Shadow CSRs both enabled. Disabling Shadow CSRs to avoid conflicts.',
        'correction': lambda config: config.get(KEY_SPECIFICS, {}).get(KEY_SPEC_IBEX, {}).update({'shadow_csrs': "off"})
    })
    
    # Example check 5: Writeback Stage enabled (error)
    checks.append({
        'type': 'warning',
        'logic': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, 'writeback_stage', default=False),
        'message': 'WritebackStage is enabled but causes corruption. Disabling WStage.',
        'correction': lambda config: config.get(KEY_SPECIFICS, {}).get(KEY_SPEC_IBEX, {}).update({'writeback_stage': "off"})
    })
    
    # # Example check 6: FT mechanisms without Fault Manager
    # checks.append({
    #     'type': 'warning',
    #     'logic': lambda config: (
    #         any([
    #             get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_REG_MON, default=False),
    #             get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_LOGIC_MON, default=False),
    #             get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, KEY_FTM_SELFTEST, default=False),
    #         ]) and
    #         not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FAULT_MANAGER, default=False)
    #     ),
    #     'message': 'Fault tolerance mechanisms enabled without Fault Manager. Setting metrics_level=1.',
    #     'correction': lambda config: config.get(KEY_SPECIFICS, {}).setdefault(KEY_SPEC_METRICS, {}).update({KEY_METRICS_LEVEL: 1})
    # })

    # # Check 9: Metrics level > 1 requires Fault Manager
    # checks.append({
    #     'type': 'warning',
    #     'logic': lambda config: (
    #         get_nested(config, KEY_GENERAL, "metrics_level", default=0) > 1 and
    #         not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FAULT_MANAGER, default=False)
    #     ),
    #     'message': 'Fault Manager contains the metrics counters needed for the selected Metrics Level. Enabling Fault Manager.',
    #     'correction': lambda config: get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, default={}).update({KEY_FEAT_FAULT_MANAGER: "on"})
    # })

    # Check 6a: Branch predictor FI target requires branch_pred performance mechanism
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "enable", default=False) and
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "branch_predictor", default="off") in [True, "on"] and
            not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_BRANCH_PRED, default=False)
        ),
        'message': 'FI target "branch_predictor" enabled but branch_pred performance mechanism is disabled. Branch predictor module does not exist. Disabling branch_predictor target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"branch_predictor": "off"})
    })
    
    # Check 6b: Branch pred (alias) FI target requires branch_pred performance mechanism  
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "enable", default=False) and
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "branch_pred", default="off") in [True, "on"] and
            not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, KEY_PERF_BRANCH_PRED, default=False)
        ),
        'message': 'FI target "branch_pred" enabled but branch_pred performance mechanism is disabled. Branch predictor module does not exist. Disabling branch_pred target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"branch_pred": "off"})
    })
    
    # FI Target WB Stage requires WB Stage
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "enable", default=False) and
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "wb_stage", default="off") in [True, "on"] and
            not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_PERF_MECH, "wstage", default=False)
        ),
        'message': 'FI target "wb_stage" enabled but wstage performance mechanism is disabled. Disabling wb_stage target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"wb_stage": "off"})
    })
    
    # Check 6c: Multiplier FI target requires RV32M extension
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "enable", default=False) and
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "multiplier", default="off") in [True, "on"] and
            not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M, default=False)
        ),
        'message': 'FI target "multiplier" enabled but RV32M extension is disabled. Multiplier module does not exist. Disabling multiplier target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"multiplier": "off"})
    })
    
    # Check 6d: Prefetch buffer FI target requires prefetch buffer feature
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "enable", default=False) and
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "prefetch_buffer", default="off") in [True, "on"] and
            not get_nested(config, KEY_GENERAL, "features", "performance_mechanisms","icache", default="on")
        ),
        'message': 'FI target "prefetch_buffer" enabled but prefetch buffer feature is disabled when ICache is enabled. Disabling prefetch_buffer target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"prefetch_buffer": "off"})
    })
    
    # Check 7: Multiplier FI target requires RV32M extension
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, "fault_injection", "area_profile", default="device") == "modules" and
            any([get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, bench, KEY_BENCH_INJECTION, default=False) 
                 for bench in get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, default={})]) and
            (get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", "multiplier", default="off") in [True, "on"]) and
            not get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M, default=False)
        ),
        'message': 'FI target "multiplier" is enabled but RV32M extension is disabled. Multiplier module does not exist. Disabling multiplier target.',
        'correction': lambda config: get_nested(config, KEY_SPECIFICS, KEY_SPEC_FT, KEY_SPEC_FI, "area", "modules", "targets", default={}).update({"multiplier": "off"})
    })
    
    # Check 10: MemECC FTM enabled (warning with auto-disable)
    checks.append({
        'type': 'warning',
        'logic': lambda config: get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, "mem_ecc", default=False),
        'message': 'MemECC fault tolerance mechanism is enabled but not currently implemented. Disabling mem_ecc.',
        'correction': lambda config: get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_FTMS, default={}).update({"mem_ecc": "off"})
    })
    
    # Check 11: RV32M extension requires hardware multiplier 
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M, default=False) and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_MULTIPLIER, default='none') == 'none'
        ),
        'message': "RV32M extension enabled but multiplier is 'none'. Set specifics.ibex.multiplier to 'slow', 'fast', or 'single_cycle'. Disabling this extension for now.",
        'correction': lambda config: get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, default={}).update({KEY_ISA_RV32M: "off"})

    })
    
    # Check 12: RV32B extension requires bit manipulation hardware (ERROR)
    checks.append({
        'type': 'warning',
        'logic': lambda config: (
            get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32B, default=False) and
            get_nested(config, KEY_SPECIFICS, KEY_SPEC_IBEX, KEY_IBEX_BIT_MANIP, default='none') == 'none'
        ),
        'message': "RV32B extension enabled but bit_manipulation is 'none'. Set specifics.ibex.bit_manipulation to 'balanced', 'ot_earlgrey', or 'full'. Disabling this extension for now.",
        'correction': lambda config: get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, default={}).update({KEY_ISA_RV32B: "off"})
    })
    
    # Check 13: RV32E incompatible with RV32M (ERROR)
    checks.append({
        'type': 'error',
        'logic': lambda config: (
            is_enabled(get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32E, default="off")) and
            is_enabled(get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32M, default="off"))
        ),
        'message': "RV32E is incompatible with RV32M. RV32E uses 16 registers; disable either RV32E or RV32M.",
        'correction': None  # Must be fixed manually
    })
    
    # Check 14: RV32E incompatible with RV32B (ERROR)
    checks.append({
        'type': 'error',
        'logic': lambda config: (
            is_enabled(get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32E, default="off")) and
            is_enabled(get_nested(config, KEY_GENERAL, KEY_GEN_FEATURES, KEY_FEAT_ISA, KEY_ISA_RV32B, default="off"))
        ),
        'message': "RV32E is incompatible with RV32B. Disable either RV32E or RV32B.",
        'correction': None  # Must be fixed manually
    })
    
    # Check 15: Embench-IoT max 10 sub-benchmarks (CORRECTION)
    def check_embench_limit(config):
        # Get embench-iot configuration
        embench_config = get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, "embench-iot", default={})
        if not embench_config or not isinstance(embench_config, dict):
            return False
        
        # Extract config section
        config_section = embench_config.get("config", {})
        if not config_section:
            return False
        
        # Get embench-benchmarks (try both hyphen and underscore variants)
        sub_benchmarks = config_section.get("embench-benchmarks", config_section.get("embench_benchmarks", {}))
        if not sub_benchmarks or not isinstance(sub_benchmarks, dict):
            return False
        
        # Count enabled benchmarks
        from scripts.common.yaml_io.yaml_helpers import is_enabled
        enabled_count = sum(1 for value in sub_benchmarks.values() if is_enabled(value))
        
        # Return True if more than 10 enabled
        return enabled_count > 10
    
    def correct_embench_limit(config):
        # Get embench-iot configuration
        embench_config = get_nested(config, KEY_GENERAL, KEY_GEN_BENCHMARKS, "embench-iot", default={})
        config_section = embench_config.get("config", {})
        
        # Get embench-benchmarks (try both variants, but correct to hyphen version)
        sub_benchmarks = config_section.get("embench-benchmarks")
        if sub_benchmarks is None:
            sub_benchmarks = config_section.get("embench_benchmarks", {})
            # Migrate underscore to hyphen version
            if sub_benchmarks:
                config_section["embench-benchmarks"] = sub_benchmarks
                if "embench_benchmarks" in config_section:
                    del config_section["embench_benchmarks"]
        
        if not sub_benchmarks or not isinstance(sub_benchmarks, dict):
            return
        
        # Disable first 10 benchmarks (in order they appear)
        from scripts.common.yaml_io.yaml_helpers import is_enabled
        benchmark_names = list(sub_benchmarks.keys())
        
        # Find enabled benchmarks
        enabled_benchmarks = [name for name in benchmark_names if is_enabled(sub_benchmarks[name])]
        
        # Disable first 10 to bring total to <=10
        if len(enabled_benchmarks) > 10:
            # Disable the first (len - 10) benchmarks to leave exactly 10 enabled
            benchmarks_to_disable = enabled_benchmarks[:len(enabled_benchmarks) - 10]
            for bench_name in benchmarks_to_disable:
                sub_benchmarks[bench_name] = "off"
    
    checks.append({
        'type': 'correction',
        'logic': check_embench_limit,
        'message': "More than 10 Embench-IoT sub-benchmarks enabled. Disabling first N benchmarks to meet 10-benchmark limit.",
        'correction': correct_embench_limit
    })
    
    return checks


def display_all_checks():
    """
    Display all validation checks in a readable format.
    
    This is used by the --display-checks CLI argument to show users
    what validation rules are in place.
    """
    checks = validation_sequence()
    
    print(f"\nTotal validation checks: {len(checks)}\n")
    
    for idx, check in enumerate(checks, 1):
        check_type = check.get('type', 'unknown')
        message = check.get('message', 'No description')
        has_correction = check.get('correction') is not None
        
        # Extract message if it's a callable
        if callable(message):
            message = "Dynamic message (context-dependent)"
        
        print(f"Check #{idx}: [{check_type.upper()}]")
        print(f"  Description: {message}")
        print(f"  Auto-correction: {'Yes' if has_correction else 'No'}")
        print()
    
    print("=" * 80)
    print("Legend:")
    print("  ERROR   - Configuration cannot proceed, must be fixed manually")
    print("  WARNING - Configuration issue detected, may be auto-corrected")
    print("=" * 80)