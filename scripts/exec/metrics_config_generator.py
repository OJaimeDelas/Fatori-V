# =============================================================================
# FATORI-V • Execution • Metrics Config Generator
# File: metrics_config_generator.py
# -----------------------------------------------------------------------------
# Generates metrics_config.h with metrics layer definition.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import HEADER_WIDTH
from scripts.common.common_settings import *
from scripts.logging.logger import log_event


def generate_c_header_comment(file_name, description):
    """
    Generate C-style header comment block.
    
    Args:
        file_name: Name of the file
        description: Description of the file's purpose
    
    Returns:
        String with formatted header comment
    """
    lines = []
    
    # Top separator
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    # Title
    lines.append("// FATORI-V • Metrics Configuration")
    
    # File name
    lines.append(f"// File: {file_name}")
    
    # Sub-separator
    lines.append("//" + "-" * (HEADER_WIDTH - 2))
    
    # Description
    lines.append(f"// {description}")
    
    # Bottom separator
    lines.append("//" + "=" * (HEADER_WIDTH - 1))
    
    return "\n".join(lines)


def generate_header_guard(file_name):
    """
    Generate C header guard name from filename.
    
    Args:
        file_name: Name of the header file (e.g., "metrics_config.h")
    
    Returns:
        Guard name (e.g., "METRICS_CONFIG_H")
    """
    return file_name.upper().replace(".", "_")


def generate_metrics_config_h(config, output_path):
    """
    Generate metrics_config.h header file with metrics layer and FI flag.
    
    This file defines:
    - METRICS_LAYER macro based on general.metrics_level
    - FATORI_FI macro based on general.fault_injection.enable
    
    Metrics levels:
    - 0: Minimal (mcycle, minstret only)
    - 1: Basic Ibex HPMCs (all ibex native performance counters)
    - 2: Error monitoring (Layer 1 + min_err_cnt, maj_err_cnt) [32 bits]
    - 3: Fault mitigation (Layer 2 + corrected_err_cnt) [48 bits]
    - 4: Full FI campaign (Layer 3 + timing counters) [128 bits]
    - 5: Detailed latency (Layer 4 + latency stats) [176 bits]
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where metrics_config.h should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = "metrics_config.h"
    
    # Extract metrics level from config (default to 0)
    metrics_level = get_nested(
        config,
        KEY_GENERAL, 'metrics_level',
        default=0
    )
    
    # Validate metrics level
    if not isinstance(metrics_level, int) or metrics_level < 0 or metrics_level > 5:
        log_event('WARNING', warning_message=f"Invalid metrics_level {metrics_level}, using 0")
        metrics_level = 0
    
    # Extract FI enable flag from config
    fi_config = get_nested(config, KEY_GENERAL, "fault_injection", default={})
    fi_enable = fi_config.get("enable", False)
    
    # Normalize to boolean then to 0/1
    if isinstance(fi_enable, str):
        from scripts.common.yaml_io.yaml_helpers import is_on
        fi_value = 1 if is_on(fi_enable) else 0
    else:
        fi_value = 1 if fi_enable else 0
    
    log_event('DEBUG', debug_message=f"Generating metrics_config.h with METRICS_LAYER={metrics_level}, FATORI_FI={fi_value}")
    
    lines = []
    
    # Header comment
    lines.append(generate_c_header_comment(file_name, "Metrics layer and FI configuration"))
    lines.append("")
    
    # Header guard start
    guard_name = generate_header_guard(file_name)
    lines.append(f"#ifndef {guard_name}")
    lines.append(f"#define {guard_name}")
    lines.append("")
    
    # Metrics layer definition with explanation
    lines.append("// Metrics collection level (0-5)")
    lines.append("// 0: Minimal, 1: Basic, 2: Error, 3: Mitigation, 4: Full FI, 5: Latency")
    lines.append("#ifndef METRICS_LAYER")
    lines.append(f"#define METRICS_LAYER {metrics_level}")
    lines.append("#endif")
    lines.append("")
    
    # FATORI_FI definition
    lines.append("// Fault injection enabled flag")
    lines.append("#ifndef FATORI_FI")
    lines.append(f"#define FATORI_FI {fi_value}")
    lines.append("#endif")
    lines.append("")
    
    # Header guard end
    lines.append(f"#endif // {guard_name}")
    
    # Write file
    try:
        with output_path.open('w') as f:
            f.write("\n".join(lines))
            f.write("\n")  # Ensure file ends with newline
        
        log_event('FILE_GENERATED', filename=file_name, output_path=str(output_path))
        return output_path
    
    except Exception as e:
        log_event('ERROR', error_message=f"Error writing metrics_config.h: {e}")
        raise