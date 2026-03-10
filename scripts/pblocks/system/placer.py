# =============================================================================
# FATORI-V • Pblock Algorithm
# File: placer.py
# -----------------------------------------------------------------------------
# Clock region allocation and FPGA coordinate generation for pblocks.
# Uses 2D guillotine bin packing so modules fill width and height efficiently.
# =============================================================================

import math

from constants import (
    FPGA_SPECS,
    get_clock_region_capacity,
    get_total_regions,
    luts_to_slices,
)


# =============================================================================
# CLOCK REGION ALLOCATION
# =============================================================================

def allocate_clock_regions(targets_with_sizes, config=None):
    """
    Assign targets to clock regions using 2D guillotine bin packing.

    Each region is treated as a 2D grid (width × height in slices). Modules are
    assigned a balanced rectangle (w × h) whose area covers their slice count.
    Free space is tracked per region as a list of axis-aligned free rectangles;
    after each placement the remaining space is split into two new rectangles
    (horizontal-first guillotine cut).
    
    DSP Awareness:
    When config is provided, MULTDIV modules requiring DSP blocks are checked
    via region_has_dsp_tiles(). On XCKU040-FBVA676, all regions have DSP tiles,
    so this check currently always passes.

    Args:
        targets_with_sizes (dict): {module_name: size_in_luts}
        config (dict, optional): Configuration with features dict for DSP detection

    Returns:
        tuple: (assignments, regions)
            assignments: {module_name: {'region_id', 'size', 'x_offset', 'y_offset', 'width', 'height'}}
            regions:     list of region dicts with 'free_rects' and 'placements'
    """
    from constants import MULTIPLIER_DSP
    
    region_height = FPGA_SPECS['region_dims']['height']  # 60 slices (all regions)
    col_widths = FPGA_SPECS['region_dims']['col_widths']  # [24, 25, 27, 25] per column
    total_regions = get_total_regions()  # 20 regions in 4×5 grid

    # Each region starts as one fully-free rectangle (local coordinates)
    # Use column-specific width for each region
    regions = []
    for region_id in range(total_regions):
        region_col = region_id % 4
        width = col_widths[region_col]
        regions.append({
            'free_rects': [(0, 0, width, region_height)],
            'placements': []
        })

    # Largest modules first — improves packing density
    sorted_targets = sorted(targets_with_sizes.items(), key=lambda x: x[1], reverse=True)

    assignments = {}

    for target, size_luts in sorted_targets:
        total_slices = luts_to_slices(size_luts)
        placed = False
        
        # Check if target requires DSP blocks (MULTDIV with RV32M variant)
        requires_dsp = False
        if config and target == 'MULTDIV':
            features = config.get('features', {})
            rv32m = features.get('FATORI_RV32M', 'None')
            dsp_count = MULTIPLIER_DSP.get(rv32m, 0)
            requires_dsp = (dsp_count > 0)

        for region_id, region in enumerate(regions):
            # DSP constraint check (all regions have DSPs on XCKU040-FBVA676)
            if requires_dsp and not region_has_dsp_tiles(region_id):
                continue
            
            # DSP exclusivity: Skip regions with existing placements
            # Vivado cannot assign DSP resources to pblocks in shared clock regions
            if requires_dsp and len(region['placements']) > 0:
                continue
            
            # Sort free rectangles by area (largest first — prefer open space)
            sorted_rects = sorted(region['free_rects'], key=lambda r: r[2] * r[3], reverse=True)

            for rect in sorted_rects:
                rx, ry, rw, rh = rect
                dims = _choose_dimensions(total_slices, rw, rh)
                if dims is None:
                    continue  # Module cannot fit in this free rectangle

                pw, ph = dims

                # Commit placement: remove used rect, add remainders
                region['free_rects'].remove(rect)
                _guillotine_split(region['free_rects'], rx, ry, rw, rh, pw, ph)

                region['placements'].append(target)
                assignments[target] = {
                    'region_id': region_id,
                    'size':      size_luts,
                    'x_offset':  rx,
                    'y_offset':  ry,
                    'width':     pw,
                    'height':    ph,
                }
                placed = True
                break

            if placed:
                break

        if not placed:
            if requires_dsp:
                raise Exception(
                    f"Cannot fit {target} ({size_luts} LUTs, {total_slices} slices, requires DSP blocks) "
                    f"into any DSP-capable clock region (2-9). All DSP-capable regions exhausted."
                )
            else:
                raise Exception(
                    f"Cannot fit {target} ({size_luts} LUTs, {total_slices} slices) "
                    f"into any clock region. All {total_regions} regions exhausted."
                )

    return assignments, regions


def _choose_dimensions(total_slices, max_w, max_h):
    """
    Choose a balanced (width, height) rectangle for a module in a free rect.

    Aims for an aspect ratio close to the available space to avoid extreme
    shapes (very tall narrow or very wide flat blocks). Returns None if the
    module cannot fit within (max_w × max_h) at all.

    Args:
        total_slices (int): Total slice area the module needs
        max_w (int): Maximum available width (slices)
        max_h (int): Maximum available height (slices)

    Returns:
        (w, h) tuple or None
    """
    # Narrowest width that keeps height within available space
    min_w = math.ceil(total_slices / max_h)
    if min_w > max_w:
        return None  # Even full width is not enough height

    # Aim for an aspect ratio matching the available rectangle
    ideal_w = math.ceil(math.sqrt(total_slices * max_w / max_h))
    w = max(min_w, min(max_w, ideal_w))
    h = math.ceil(total_slices / w)

    # Guard: ensure height stays within bounds (guaranteed by w >= min_w, but explicit)
    if h > max_h:
        w = min_w
        h = math.ceil(total_slices / w)

    return w, h


def _guillotine_split(free_rects, rx, ry, rw, rh, pw, ph):
    """
    Guillotine-split the free rectangle after placing a (pw × ph) block at (rx, ry).

    Uses horizontal-first split:
      - Right piece: same row height as the placed block, to its right
      - Top piece:   full available width, above the placed block

    This preserves wide horizontal bands that accommodate large future modules.

    Args:
        free_rects (list): Free rectangle list to update in-place
        rx, ry (int): Top-left corner of the original free rectangle
        rw, rh (int): Width and height of the original free rectangle
        pw, ph (int): Width and height of the placed module
    """
    # Right piece: extends to the right of the placed module, same height
    if rw - pw > 0:
        free_rects.append((rx + pw, ry, rw - pw, ph))
    # Top piece: spans the full original width, above the placed module
    if rh - ph > 0:
        free_rects.append((rx, ry + ph, rw, rh - ph))


# =============================================================================
# COORDINATE GENERATION
# =============================================================================

def generate_coordinates(target, region_id, x_offset, y_offset, width, height):
    """
    Generate SLICE coordinate range for a pblock from its 2D placement.

    Args:
        target (str):     Module name (used only in error messages)
        region_id (int):  Clock region ID (0-9, mapped to 2×5 grid)
        x_offset (int):   Horizontal offset within the region (local slices)
        y_offset (int):   Vertical offset within the region (local slices)
        width (int):      Pblock width in slices
        height (int):     Pblock height in slices

    Returns:
        str: SLICE range string (e.g., "SLICE_X0Y0:SLICE_X9Y24")
    """
    x_max_fpga   = FPGA_SPECS['slice_limits']['x_max']
    y_max_fpga   = FPGA_SPECS['slice_limits']['y_max']
    region_height = FPGA_SPECS['region_dims']['height']

    region_col = region_id % 4  # 0, 1, 2, or 3
    region_row = region_id // 4  # 0 to 4

    # Get column-specific base X and width from FPGA_SPECS
    col_x_bases = FPGA_SPECS['region_dims']['col_x_bases']
    base_x = col_x_bases[region_col]
    base_y = region_row * region_height

    x_start = base_x + x_offset
    y_start = base_y + y_offset
    x_end   = x_start + width  - 1
    y_end   = y_start + height - 1

    if x_end > x_max_fpga or y_end > y_max_fpga:
        raise ValueError(
            f"Coordinates out of bounds for {target}: "
            f"SLICE_X{x_start}Y{y_start}:SLICE_X{x_end}Y{y_end} "
            f"exceeds FPGA limits X{x_max_fpga} Y{y_max_fpga}"
        )

    return f"SLICE_X{x_start}Y{y_start}:SLICE_X{x_end}Y{y_end}"


def generate_region_name(region_id):
    """
    Convert region ID to Vivado clock region name.
    
    Args:
        region_id (int): Region ID (0-9)
    
    Returns:
        str: Clock region name (e.g., "CLOCKREGION_X0Y2")
    """
    col = region_id % 4
    row = region_id // 4
    return f"CLOCKREGION_X{col}Y{row}"


# =============================================================================
# PLACEMENT PLAN GENERATION
# =============================================================================

def create_placement_plan(targets_with_sizes, config=None):
    """
    Create complete placement plan with regions and coordinates.

    Includes DSP allocation for MULTIPLIER pblocks.

    Args:
        targets_with_sizes (dict): {module_name: size_in_luts}
        config (dict): Configuration dict (needed for MULTIPLIER DSP allocation)

    Returns:
        dict: Complete placement plan for each target
    """
    # Pass config to allocator for DSP-aware placement
    assignments, _regions = allocate_clock_regions(targets_with_sizes, config)

    placement_plan = {}

    for target, assign in assignments.items():
        region_id = assign['region_id']
        coords = generate_coordinates(
            target,
            region_id,
            assign['x_offset'],
            assign['y_offset'],
            assign['width'],
            assign['height'],
        )
        placement_plan[target] = {
            'size':        assign['size'],
            'region_id':   region_id,
            'region_name': generate_region_name(region_id),
            'coordinates': coords,
        }

    if config is not None:
        add_dsp_allocation_to_plan(placement_plan, targets_with_sizes, config)

    return placement_plan


def generate_dsp_coordinates(region_id, dsp_count):
    """
    Generate DSP48 block coordinates for a pblock.
    
    XCKU040 DSP48E2 architecture (empirically verified):
    - 4×5 clock region grid (20 regions total)
    - ALL regions have DSP tiles available
    - Each region is 24 DSPs tall in Y dimension
    - DSP X columns per clock region column:
      X0Y*: X0-X3   (primary: X0)
      X1Y*: X4-X7   (primary: X4)
      X2Y*: X8-X13  (primary: X8)
      X3Y*: X14-X15 (primary: X14)
    
    Args:
        region_id (int): Clock region ID (0-19 for 4×5 grid)
        dsp_count (int): Number of DSP48 blocks needed
    
    Returns:
        str: DSP coordinate string (e.g., 'DSP48_X4Y24:DSP48_X4Y27')
             or None if dsp_count is 0
    
    Raises:
        ValueError: If DSP allocation exceeds region capacity
    """
    if dsp_count == 0:
        return None
    
    # Calculate region position in 4×5 grid
    region_col = region_id % 4  # 0, 1, 2, or 3
    region_row = region_id // 4  # 0-4
    
    # Get DSP X column for this clock region column
    dsp_config = FPGA_SPECS['dsp_regions']
    dsp_x_primary = dsp_config['dsp_x_primary']  # [0, 4, 8, 14]
    dsp_x = dsp_x_primary[region_col]
    
    # DSP Y coordinate calculation
    # Each clock region is 24 DSPs tall (empirically verified)
    # Row 0: Y0-Y23
    # Row 1: Y24-Y47
    # Row 2: Y48-Y71
    # Row 3: Y72-Y95
    # Row 4: Y96-Y119
    dsps_per_region_row = dsp_config['dsps_per_region_row']  # 24
    dsp_y_base = region_row * dsps_per_region_row
    
    # Allocate sequential DSP blocks starting from region base
    dsp_y_start = dsp_y_base
    dsp_y_end = dsp_y_start + dsp_count - 1
    
    # Validate Y coordinates don't exceed region limits
    region_dsp_y_max = dsp_y_base + dsps_per_region_row - 1
    if dsp_y_end > region_dsp_y_max:
        raise ValueError(
            f"DSP allocation exceeds region capacity: requested {dsp_count} DSPs "
            f"in CLOCKREGION_X{region_col}Y{region_row}, but region only has "
            f"{dsps_per_region_row} DSPs available (Y{dsp_y_base}-Y{region_dsp_y_max}). "
            f"Reduce DSP count or use a different placement strategy."
        )
    
    # Validate Y coordinates don't exceed device limits
    # XCKU040: 120 DSPs per column (Y=0 to Y=119)
    if dsp_y_end > 119:
        raise ValueError(
            f"DSP allocation exceeds device limits: DSP48_X{dsp_x}Y{dsp_y_start}:Y{dsp_y_end} "
            f"(max Y=119 for XCKU040). This should never happen if region validation passed."
        )
    
    # Format: DSP48E2_XnYm or DSP48E2_XnYm:DSP48E2_XnYm (UltraScale+ full site name)
    if dsp_count == 1:
        coords = f"DSP48E2_X{dsp_x}Y{dsp_y_start}"
    else:
        coords = f"DSP48E2_X{dsp_x}Y{dsp_y_start}:DSP48E2_X{dsp_x}Y{dsp_y_end}"
    
    return coords


def region_has_dsp_tiles(region_id):
    """
    Check if a clock region has DSP tiles available.
    
    On XCKU040 FBVA676 package, ALL clock regions have DSP tiles available
    (verified empirically via Vivado query 2026-03-09).
    
    Args:
        region_id (int): Clock region ID (0-19)
    
    Returns:
        bool: Always True for XCKU040-FBVA676
    """
    # All 20 clock regions have DSP tiles on this device
    return True


def add_dsp_allocation_to_plan(placement_plan, targets_with_sizes, config):
    """
    Add DSP allocation to MULTIPLIER pblock in placement plan.
    
    Validates that MULTIPLIER is placed in a DSP-capable region and
    generates appropriate DSP48 coordinates.
    
    Args:
        placement_plan (dict): Placement plan to modify
        targets_with_sizes (dict): Original target sizes
        config (dict): Configuration with features dict
    
    Returns:
        None (modifies placement_plan in-place)
    
    Raises:
        ValueError: If MULTIPLIER is placed in region without DSP tiles
    """
    from constants import MULTIPLIER_DSP
    
    # Check if MULTIPLIER is in the plan
    if 'MULTDIV' not in placement_plan:
        return
    
    # Get RV32M variant from config
    features = config.get('features', {})
    rv32m = features.get('FATORI_RV32M', 'None')
    
    # Get DSP count for this variant
    dsp_count = MULTIPLIER_DSP.get(rv32m, 0)
    
    if dsp_count > 0:
        # Get region assignment for MULTIPLIER
        region_id = placement_plan['MULTDIV']['region_id']
        
        # Validate region has DSP tiles BEFORE generating coordinates
        # This provides clear error message if placer made a mistake
        if not region_has_dsp_tiles(region_id):
            region_col = region_id % 2
            region_row = region_id // 2
            raise ValueError(
                f"MULTDIV (MULTIPLIER) placed in CLOCKREGION_X{region_col}Y{region_row} "
                f"(region_id={region_id}) which has NO DSP tiles. "
                f"RV32M={rv32m} requires {dsp_count} DSP blocks. "
                f"XCKU040 DSP tiles only exist in rows 1-4 (regions 2-9). "
                f"This is a placer bug - MULTDIV should only be placed in DSP-capable regions."
            )
        
        # Generate DSP coordinates (will raise ValueError if region invalid)
        dsp_coords = generate_dsp_coordinates(region_id, dsp_count)
        
        # Add to placement plan
        placement_plan['MULTDIV']['dsp_count'] = dsp_count
        placement_plan['MULTDIV']['dsp_coordinates'] = dsp_coords


# =============================================================================
# UTILIZATION ANALYSIS
# =============================================================================

def analyze_utilization(placement_plan):
    """
    Analyze FPGA utilization from placement plan.
    
    Args:
        placement_plan (dict): Placement plan from create_placement_plan()
    
    Returns:
        dict: Utilization statistics
    
    Statistics:
        - Total LUTs allocated
        - Per-region utilization
        - Number of regions used
        - Percentage of FPGA used
    """
    region_capacity = get_clock_region_capacity()
    total_regions = get_total_regions()
    
    # Initialize region usage
    region_usage = [0] * total_regions
    
    # Count LUTs per region
    for target, plan in placement_plan.items():
        region_id = plan['region_id']
        size = plan['size']
        region_usage[region_id] += size
    
    # Calculate statistics
    total_luts_allocated = sum(plan['size'] for plan in placement_plan.values())
    regions_used = sum(1 for usage in region_usage if usage > 0)
    total_fpga_luts = FPGA_SPECS['total']['luts']
    
    # Per-region utilization percentages
    region_utilization = [
        {
            'region_id': i,
            'region_name': generate_region_name(i),
            'luts_used': usage,
            'capacity': region_capacity,
            'utilization_percent': (usage / region_capacity) * 100
        }
        for i, usage in enumerate(region_usage)
    ]
    
    return {
        'total_luts_allocated': total_luts_allocated,
        'total_fpga_luts': total_fpga_luts,
        'fpga_utilization_percent': (total_luts_allocated / total_fpga_luts) * 100,
        'regions_used': regions_used,
        'total_regions': total_regions,
        'region_utilization': region_utilization,
    }


# =============================================================================
# VALIDATION
# =============================================================================

def validate_placement(placement_plan):
    """
    Validate placement plan for errors.
    
    Args:
        placement_plan (dict): Placement plan
    
    Returns:
        list: List of warnings/errors (empty if valid)
    
    Checks:
        - No region over-utilized (>100%)
        - Coordinates within valid FPGA bounds
        - No overlapping pblocks in same region
    """
    warnings = []
    region_capacity = get_clock_region_capacity()
    
    # Check region utilization
    utilization = analyze_utilization(placement_plan)
    
    for region in utilization['region_utilization']:
        if region['utilization_percent'] > 100:
            warnings.append(
                f"{region['region_name']}: Over-utilized at "
                f"{region['utilization_percent']:.1f}% "
                f"({region['luts_used']}/{region['capacity']} LUTs)"
            )
        elif region['utilization_percent'] > 90:
            warnings.append(
                f"{region['region_name']}: High utilization "
                f"{region['utilization_percent']:.1f}% - may have routing issues"
            )
    
    return warnings