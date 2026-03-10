# =============================================================================
# FATORI-V • Feature Generation • System Dict Merger
# File: system_dict_merger.py
# -----------------------------------------------------------------------------
# Merges fatori_registers.yaml with pblock_dict.yaml into system_dict_merged.yaml.
# =============================================================================

from pathlib import Path
import yaml
import fatori_settings as cfg
from scripts.common.yaml_io.yaml_helpers import get_board_name
from scripts.logging import logger
from config.constants import PBLOCK_DICT_YAML, SYSTEM_DICT_MERGED_NAME


def load_yaml_file(file_path):
    """
    Load a YAML file and return its contents.
    
    Args:
        file_path: Path to the YAML file
    
    Returns:
        Dictionary with file contents, or empty dict if file doesn't exist
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        logger.log_event('WARNING', warning_message=f"YAML file not found: {file_path}")
        return {}
    
    try:
        with file_path.open('r') as f:
            data = yaml.safe_load(f)
            return data if data is not None else {}
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error loading YAML file {file_path}: {e}")
        return {}


def extract_coordinates_from_pblock(coordinates_str, board_name="xcku040"):
    """
    Extract x_lo, y_lo, x_hi, y_hi from pblock coordinates string.
    
    Converts SLICE coordinates to physical tile coordinates for ACME compatibility.
    ACME filtering requires tile coordinates (e.g., X=50-357 for XCKU040),
    while Vivado pblocks use SLICE coordinates (e.g., X=0-47 for XCKU040).
    
    Format: "SLICE_X0Y0:SLICE_X23Y60"
    
    Args:
        coordinates_str: Coordinates string from pblock_dict
        board_name: FPGA board identifier (default: "xcku040")
    
    Returns:
        Dictionary with x_lo, y_lo, x_hi, y_hi in tile coordinates
    """
    try:
        # Parse "SLICE_X0Y0:SLICE_X23Y60"
        parts = coordinates_str.split(":")
        start = parts[0].replace("SLICE_", "")  # "X0Y0"
        end = parts[1].replace("SLICE_", "")    # "X23Y60"
        
        # Extract SLICE X and Y values
        slice_x_lo = int(start.split("Y")[0].replace("X", ""))
        slice_y_lo = int(start.split("Y")[1])
        slice_x_hi = int(end.split("Y")[0].replace("X", ""))
        slice_y_hi = int(end.split("Y")[1])
        
        # Convert SLICE coordinates to tile coordinates for ACME
        # This is board-specific; XCKU040 requires conversion
        if board_name.lower() == "xcku040":
            from fi.backend.acme.xcku040 import Xcku040Board
            board = Xcku040Board()
            tile_x_lo, tile_y_lo = board.slice_xy_to_tile_xy(slice_x_lo, slice_y_lo)
            tile_x_hi, tile_y_hi = board.slice_xy_to_tile_xy(slice_x_hi, slice_y_hi)
        else:
            # For other boards, assume SLICE == tile (may need board-specific logic)
            tile_x_lo, tile_y_lo = slice_x_lo, slice_y_lo
            tile_x_hi, tile_y_hi = slice_x_hi, slice_y_hi
        
        return {
            "x_lo": tile_x_lo,
            "y_lo": tile_y_lo,
            "x_hi": tile_x_hi,
            "y_hi": tile_y_hi
        }
    except Exception as e:
        logger.log_event('WARNING', warning_message=f"Error parsing coordinates '{coordinates_str}': {e}")
        return {"x_lo": 0, "y_lo": 0, "x_hi": 0, "y_hi": 0}


def parse_fatori_registers(registers_data):
    """
    Parse fatori_registers.yaml to build:
    1. Flat register dictionary: {id: {name, module}}
    2. Module-to-registers mapping: {module: [reg_ids]}
    
    Args:
        registers_data: Loaded fatori_registers.yaml content
    
    Returns:
        Tuple of (flat_registers_dict, module_to_regs_dict)
    """
    flat_registers = {}
    module_to_regs = {}
    
    modules = registers_data.get("modules", [])
    
    for module_entry in modules:
        module_name = module_entry.get("module", "").replace(".sv", "")
        regs = module_entry.get("regs", [])
        
        if not module_name:
            continue
        
        module_to_regs[module_name] = []
        
        for reg in regs:
            reg_id = reg.get("id")
            reg_name = reg.get("name")
            
            if reg_id is None or not reg_name:
                continue
            
            # Add to flat dictionary
            flat_registers[reg_id] = {
                "name": reg_name,
                "module": module_name
            }
            
            # Add to module mapping
            module_to_regs[module_name].append(reg_id)
    
    return flat_registers, module_to_regs


def map_pblock_to_ibex_module(pblock_name):
    """
    Map pblock target names to Ibex module names.
    
    Args:
        pblock_name: Name from pblock_dict (e.g., "ALU", "ID_STAGE")
    
    Returns:
        Corresponding module name from fatori_registers
    """
    # Mapping from pblock names to module names
    mapping = {
        "ALU": "ibex_alu",
        "MULTDIV": "ibex_multdiv_fast",  # or ibex_multdiv_slow
        "LSU": "ibex_load_store_unit",
        "ID_STAGE": "ibex_id_stage",
        "IF_STAGE": "ibex_if_stage",
        "EX_BLOCK": "ibex_ex_block",
        "CONTROLLER": "ibex_controller",
        "DECODER": "ibex_decoder",
        "BRANCH_PREDICT": "ibex_branch_predict",
        "ICACHE": "ibex_icache",
        "WB_STAGE": "ibex_wb_stage",
    }
    
    return mapping.get(pblock_name.upper(), pblock_name.lower())


def get_device_bounds(board_name):
    """
    Get device bounds for a specific FPGA board.
    
    Args:
        board_name: Board identifier (e.g., "xcku040")
    
    Returns:
        Dictionary with device bounds
    """
    # Device bounds for supported FPGAs
    devices = {
        "xcku040": {
            "min_x": 0,
            "max_x": 358,
            "min_y": 0,
            "max_y": 310,
            "wf": 123  # Words per frame for UltraScale
        },
        "xc7a35t": {
            "min_x": 0,
            "max_x": 115,
            "min_y": 0,
            "max_y": 200,
            "wf": 101  # Words per frame for 7-series
        }
    }
    
    return devices.get(board_name, devices["xcku040"])


def merge_system_dicts(config, output_path):
    """
    Merge fatori_registers.yaml and pblock_dict.yaml into system_dict_merged.yaml.
    
    Creates a unified system dictionary in the format:
    <board_name>:
      device:
        min_x, max_x, min_y, max_y, wf
      targets:
        <target_name>:
          x_lo, y_lo, x_hi, y_hi
          registers: [list of reg IDs]
          module: <module_name>
      registers:
        <id>: {name: <name>, module: <module>}
    
    Args:
        config: The loaded YAML configuration dictionary
        output_path: Path where system_dict_merged.yaml should be written
    
    Returns:
        Path to the generated merged file
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    logger.log_event('DEBUG', debug_message="Merging system dictionaries...")
    
    board_name = get_board_name(config)
    logger.log_event('DEBUG', debug_message=f"  Board: {board_name}")
    
    # Generate fatori_registers_active.yaml (filtered based on enabled macros)
    from scripts.features.register_filter import create_active_registers_yaml
    from config.constants import FATORI_REGISTERS_ACTIVE_NAME
    
    active_registers_path = cfg.TMP_GENERATED_DIR / FATORI_REGISTERS_ACTIVE_NAME
    create_active_registers_yaml(config, active_registers_path)
    
    # Load fatori_registers_active.yaml (filtered version)
    fatori_registers_data = load_yaml_file(active_registers_path)
    
    if not fatori_registers_data:
        logger.log_event('ERROR', error_message="fatori_registers.yaml is empty or missing - cannot proceed")
        return None
    
    # Parse registers
    flat_registers, module_to_regs = parse_fatori_registers(fatori_registers_data)
    logger.log_event('DEBUG', debug_message=f"  Loaded {len(flat_registers)} registers from fatori_registers.yaml")
    
    # Load pblock_dict.yaml (may not exist if FI disabled or external system unavailable)
    pblock_dict_path = cfg.TMP_GENERATED_DIR / PBLOCK_DICT_YAML
    pblock_dict = load_yaml_file(pblock_dict_path)
    
    # Build the merged dictionary
    system_dict = {
        board_name: {
            "device": get_device_bounds(board_name),
            "targets": {},
            "registers": {}
        }
    }
    
    # Add targets with coordinates from pblock_dict
    if pblock_dict and "targets" in pblock_dict:
        logger.log_event('DEBUG', debug_message=f"  Found {len(pblock_dict['targets'])} targets in pblock_dict.yaml")
        
        for target in pblock_dict["targets"]:
            target_name = target.get("name", "").lower()
            coordinates_str = target.get("coordinates", "")
            
            if not target_name or not coordinates_str:
                continue
            
           # Extract coordinates (converted to tile coordinates for ACME)
            coords = extract_coordinates_from_pblock(coordinates_str, board_name)
            
            # Map to module name
            module_name = map_pblock_to_ibex_module(target_name)
            
            # Get registers for this module
            registers_for_module = module_to_regs.get(module_name, [])
            
            # Add to targets
            system_dict[board_name]["targets"][target_name] = {
                "x_lo": coords["x_lo"],
                "y_lo": coords["y_lo"],
                "x_hi": coords["x_hi"],
                "y_hi": coords["y_hi"],
                "registers": registers_for_module,
                "module": module_name
            }
    else:
        logger.log_event('DEBUG', debug_message="  No pblock_dict.yaml found - generating without target coordinates")
        
        # Create targets from module_to_regs without coordinates
        for module_name, reg_ids in module_to_regs.items():
            if not reg_ids:
                continue
            
            # Use module name as target name
            target_name = module_name.replace("ibex_", "").replace("_", "")
            
            system_dict[board_name]["targets"][target_name] = {
                "x_lo": 0,
                "y_lo": 0,
                "x_hi": 0,
                "y_hi": 0,
                "registers": reg_ids,
                "module": module_name
            }
    
    # Add flat registers dictionary
    system_dict[board_name]["registers"] = flat_registers
    
    logger.log_event('DEBUG', debug_message=f"  Merged dictionary has {len(system_dict[board_name]['targets'])} targets")
    logger.log_event('DEBUG', debug_message=f"  Merged dictionary has {len(flat_registers)} registers")
    
    # Write merged dictionary with custom formatting
    try:
        with output_path.open('w') as f:
            # Add header comment
            f.write("# FATORI-V System Dictionary - Merged Format\n")
            f.write("# Combines register definitions with pblock placement\n\n")
            
            # Write board section
            f.write(f"{board_name}:\n")
            
            # Write device section
            device = system_dict[board_name]["device"]
            f.write("  device:\n")
            for key, value in device.items():
                f.write(f"    {key}: {value}\n")
            f.write("\n")
            
            # Write targets section
            f.write("  targets:\n")
            targets = system_dict[board_name]["targets"]
            for target_name, target_data in targets.items():
                f.write(f"    {target_name}:\n")
                f.write(f"      x_lo: {target_data['x_lo']}\n")
                f.write(f"      y_lo: {target_data['y_lo']}\n")
                f.write(f"      x_hi: {target_data['x_hi']}\n")
                f.write(f"      y_hi: {target_data['y_hi']}\n")
                # Write registers as a single-line list
                regs_str = str(target_data['registers']).replace(' ', '')
                f.write(f"      registers: {regs_str}\n")
                f.write(f"      module: {target_data['module']}\n")
            f.write("\n")
            
            # Write registers section with inline format
            f.write("  registers:\n")
            registers = system_dict[board_name]["registers"]
            # Sort by ID for readability
            sorted_regs = sorted(registers.items(), key=lambda x: x[0])
            for reg_id, reg_data in sorted_regs:
                # Format: id: {name: "name", module: "module"}
                f.write(f"    {reg_id}: {{name: \"{reg_data['name']}\", module: \"{reg_data['module']}\"}}\n")
        
        logger.log_event('FILE_GENERATED', filename=SYSTEM_DICT_MERGED_NAME, output_path=str(output_path))
        return output_path
    
    except Exception as e:
        logger.log_event('ERROR', error_message=f"Error writing merged dictionary: {e}")
        raise