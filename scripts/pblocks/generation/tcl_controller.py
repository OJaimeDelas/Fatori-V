# =============================================================================
# FATORI-V • Pblock Generation • TCL Controller
# File: tcl_controller.py
# -----------------------------------------------------------------------------
# Orchestrates generation of all Vivado TCL hook scripts.
# =============================================================================

from pathlib import Path
import fatori_settings as cfg
from config.constants import (
    PRE_SYNTHESIS_TCL, POST_OPT_TCL, POST_ROUTE_TCL,
    PRE_BITSTREAM_TCL, POST_BITSTREAM_TCL
)
from scripts.pblocks.generation.tcl_generators import (
    generate_pre_synthesis_tcl,
    generate_post_opt_tcl,
    generate_post_route_tcl,
    generate_pre_bitstream_tcl,
    generate_post_bitstream_tcl,
)
from scripts.logging import logger


def generate_all_tcl_files(config, output_dir=None):
    """
    Generate all Vivado TCL hook scripts for a run configuration.
    
    This orchestrates the generation of:
    - pre_synthesis.tcl: SEM IP integration
    - post_opt.tcl: Pblock constraint application
    - post_route.tcl: Post-routing hooks (placeholder)
    - pre_bitstream.tcl: Pre-bitstream hooks (placeholder)
    - post_bitstream.tcl: Post-bitstream hooks (placeholder)
    
    Args:
        config: The loaded YAML configuration dictionary
        output_dir: Directory where TCL files should be written.
                   Defaults to tmp/tcl/
    
    Returns:
        Dictionary mapping script names to their generated paths
        {
            'pre_synthesis': Path,
            'post_opt': Path,
            'post_route': Path,
            'pre_bitstream': Path,
            'post_bitstream': Path,
        }
    """
    # Use default output directory if not specified
    if output_dir is None:
        output_dir = cfg.TMP_TCL_DIR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    logger.log_event('TCL_GENERATION_START', output_dir=str(output_dir))
    
    generated_files = {}
    
    # Generate pre-synthesis script
    logger.log_event('DEBUG', debug_message="Generating pre-synthesis TCL...")
    pre_synth_path = generate_pre_synthesis_tcl(config, output_dir / PRE_SYNTHESIS_TCL)
    generated_files['pre_synthesis'] = pre_synth_path
    logger.log_event('TCL_GENERATION', filename=pre_synth_path.name)
    
    # Generate post-optimization script
    logger.log_event('DEBUG', debug_message="Generating post-optimization TCL...")
    post_opt_path = generate_post_opt_tcl(config, output_dir / POST_OPT_TCL)
    generated_files['post_opt'] = post_opt_path
    logger.log_event('TCL_GENERATION', filename=post_opt_path.name)
    
    # Generate post-route script
    logger.log_event('DEBUG', debug_message="Generating post-route TCL...")
    post_route_path = generate_post_route_tcl(config, output_dir / POST_ROUTE_TCL)
    generated_files['post_route'] = post_route_path
    logger.log_event('TCL_GENERATION', filename=post_route_path.name)
    
    # Generate pre-bitstream script
    logger.log_event('DEBUG', debug_message="Generating pre-bitstream TCL...")
    pre_bit_path = generate_pre_bitstream_tcl(config, output_dir / PRE_BITSTREAM_TCL)
    generated_files['pre_bitstream'] = pre_bit_path
    logger.log_event('TCL_GENERATION', filename=pre_bit_path.name)
    
    # Generate post-bitstream script
    logger.log_event('DEBUG', debug_message="Generating post-bitstream TCL...")
    post_bit_path = generate_post_bitstream_tcl(config, output_dir / POST_BITSTREAM_TCL)
    generated_files['post_bitstream'] = post_bit_path
    logger.log_event('TCL_GENERATION', filename=post_bit_path.name)
    
    logger.log_event('TCL_GENERATION_END', file_count=len(generated_files))
    
    return generated_files