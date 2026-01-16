# =============================================================================
# FATORI-V • Pblock Generation • TCL Generators
# File: tcl_generators.py
# -----------------------------------------------------------------------------
# Generates Vivado TCL hook scripts for build integration.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import SEM_GEN_TCL, REPORT_GEN_TCL
from scripts.common.common_settings import *
from scripts.common.yaml_io.yaml_helpers import any_benchmark_has_fi
from scripts.common.tcl_writer.tcl_writer import (
    generate_tcl_header,
    generate_section_comment,
    generate_comment,
    generate_puts_statement,
    generate_source_statement,
    write_tcl_file,
)
from config.constants import (
    PRE_SYNTHESIS_TCL, POST_OPT_TCL, POST_ROUTE_TCL,
    PRE_BITSTREAM_TCL, POST_BITSTREAM_TCL
)


def generate_pre_synthesis_tcl(config, output_path):
    """
    Generate pre_synthesis.tcl for Vivado build hooks.
    
    This script runs before synthesis and handles:
    - SEM IP instantiation if FI is enabled
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where pre_synthesis.tcl should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = PRE_SYNTHESIS_TCL
    
    content_lines = []
    
    # Check if FI is enabled
    fi_enabled = any_benchmark_has_fi(config)
    
    if fi_enabled:
        # Section: SEM IP Integration
        content_lines.append(generate_section_comment("SEM IP Integration"))
        content_lines.append("")
        
        content_lines.append(generate_puts_statement("FATORI-V: Integrating SEM IP for fault injection"))
        content_lines.append("")
        
        # Source the SEM generation script
        content_lines.append(generate_comment("Source SEM IP generation script"))
        content_lines.append(generate_source_statement(f"[file join $::env(VIVADO_INPUT) {SEM_GEN_TCL}]"))
        content_lines.append("")
    else:
        # No FI - minimal script
        content_lines.append(generate_puts_statement("FATORI-V: No fault injection configured"))
        content_lines.append(generate_comment("No SEM IP integration needed"))
    
    # Write the file
    return write_tcl_file(
        output_path=output_path.parent,
        file_name=file_name,
        description="Pre-synthesis Vivado hooks",
        content=content_lines,
        purpose="Pre-Synthesis"
    )


def generate_post_opt_tcl(config, output_path):
    """
    Generate post_opt.tcl for Vivado build hooks.
    
    This script runs after optimization and handles:
    - Sourcing pblock placement constraints if FI enabled
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where post_opt.tcl should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = POST_OPT_TCL
    
    content_lines = []
    
    # Check if FI is enabled
    fi_enabled = any_benchmark_has_fi(config)
    
    if fi_enabled:
        # Section: Pblock Constraints
        content_lines.append(generate_section_comment("Pblock Placement Constraints"))
        content_lines.append("")
        
        content_lines.append(generate_puts_statement("FATORI-V: Applying pblock placement constraints"))
        content_lines.append("")
        
        # Source the pblock TCL file
        content_lines.append(generate_comment("Source pblock placement constraints"))
        content_lines.append(generate_source_statement("[file join $::env(VIVADO_INPUT) fatori_pblocks.tcl]"))
        content_lines.append("")
    else:
        # No FI - minimal script
        content_lines.append(generate_puts_statement("FATORI-V: No pblock constraints needed"))
        content_lines.append(generate_comment("No fault injection configured"))
    
    # Write the file
    return write_tcl_file(
        output_path=output_path.parent,
        file_name=file_name,
        description="Post-optimization Vivado hooks",
        content=content_lines,
        purpose="Post-Optimization"
    )


def generate_post_route_tcl(config, output_path):
    """
    Generate post_route.tcl for Vivado build hooks.
    
    This is a placeholder for future post-routing hooks.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where post_route.tcl should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = POST_ROUTE_TCL
    
    content_lines = []
    
    content_lines.append(generate_puts_statement("FATORI-V: Post-route hook"))
    content_lines.append(generate_comment("Placeholder for future post-routing operations"))
    
    # Write the file
    return write_tcl_file(
        output_path=output_path.parent,
        file_name=file_name,
        description="Post-routing Vivado hooks",
        content=content_lines,
        purpose="Post-Route"
    )


def generate_pre_bitstream_tcl(config, output_path):
    """
    Generate pre_bitstream.tcl for Vivado build hooks.
    
    This script runs before bitstream generation and handles:
    - Sourcing report generation script
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where pre_bitstream.tcl should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = PRE_BITSTREAM_TCL
    
    content_lines = []
    
    # Section: Report Generation
    content_lines.append(generate_section_comment("Report Generation"))
    content_lines.append("")
    
    content_lines.append(generate_puts_statement("FATORI-V: Generating Vivado reports"))
    content_lines.append("")
    
    # Source the report generation script
    content_lines.append(generate_comment("Source report generation script"))
    content_lines.append(generate_source_statement(f"[file join $::env(VIVADO_INPUT) {REPORT_GEN_TCL}]"))
    content_lines.append("")
    
    # Write the file
    return write_tcl_file(
        output_path=output_path.parent,
        file_name=file_name,
        description="Pre-bitstream Vivado hooks",
        content=content_lines,
        purpose="Pre-Bitstream"
    )


def generate_post_bitstream_tcl(config, output_path):
    """
    Generate post_bitstream.tcl for Vivado build hooks.
    
    This is a placeholder for future post-bitstream hooks.
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where post_bitstream.tcl should be written
    
    Returns:
        Path to the generated file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_name = POST_BITSTREAM_TCL
    
    content_lines = []
    
    content_lines.append(generate_puts_statement("FATORI-V: Post-bitstream hook"))
    content_lines.append(generate_comment("Placeholder for future post-bitstream operations"))
    
    # Write the file
    return write_tcl_file(
        output_path=output_path.parent,
        file_name=file_name,
        description="Post-bitstream Vivado hooks",
        content=content_lines,
        purpose="Post-Bitstream"
    )