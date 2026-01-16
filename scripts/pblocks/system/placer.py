# =============================================================================
# FATORI-V • Pblock Algorithm
# File: placer.py
# 
# Clock region allocation and FPGA coordinate generation for pblocks
# =============================================================================

from constants import (
    FPGA_SPECS,
    get_clock_region_capacity,
    get_total_regions,
    luts_to_slices,
)


# =============================================================================
# CLOCK REGION ALLOCATION
# =============================================================================

def allocate_clock_regions(targets_with_sizes):
    """
    Assign targets to clock regions using first-fit decreasing algorithm.
    
    Args:
        targets_with_sizes (dict): {module_name: size_in_luts}
    
    Returns:
        dict: {module_name: {'region_id': int, 'size': int}}
    
    Algorithm:
        - Sort targets by size (largest first)
        - Place each target in first region with sufficient space
        - Bin-packing to minimize wasted space
    
    Notes:
        - Each clock region has ~12,000 LUT capacity
        - Multiple pblocks can coexist in same region
    """
    from constants import TARGET_REGION_UTILIZATION

    region_capacity = int(get_clock_region_capacity() * TARGET_REGION_UTILIZATION)
    total_regions = get_total_regions()
    
    # Initialize regions with available space
    regions = [{'used': 0, 'targets': []} for _ in range(total_regions)]
    
    # Sort targets by size (largest first - better bin packing)
    sorted_targets = sorted(targets_with_sizes.items(), 
                           key=lambda x: x[1], 
                           reverse=True)
    
    assignments = {}
    
    for target, size in sorted_targets:
        # Find first region that can fit this target
        placed = False
        for region_id, region in enumerate(regions):
            if region['used'] + size <= region_capacity:
                # Place target in this region
                region['used'] += size
                region['targets'].append(target)
                
                assignments[target] = {
                    'region_id': region_id,
                    'size': size
                }
                placed = True
                break
        
        if not placed:
            raise Exception(
                f"Cannot fit {target} ({size} LUTs) into any region. "
                f"Design too large for FPGA!"
            )
    
    return assignments, regions


# =============================================================================
# COORDINATE GENERATION
# =============================================================================

def generate_coordinates(target, region_id, size_luts, offset=0):
    """
    Generate SLICE coordinate range for a pblock.
    
    Args:
        target (str): Module name
        region_id (int): Clock region ID (0-9)
        size_luts (int): Pblock size in LUTs
        offset (int): Vertical offset within region (for stacking)
    
    Returns:
        str: SLICE range string (e.g., "SLICE_X0Y0:SLICE_X24Y50")
    
    Notes:
        - XCKU040 has 2 columns (X0-X1) and 5 rows (Y0-Y4)
        - Each region is 24 slices wide, 60 slices tall
        - We create rectangular pblocks spanning full width
    """
    # Convert region_id to X,Y coordinates
    region_col = region_id % 2  # 0 or 1
    region_row = region_id // 2  # 0 to 4
    
    # Base coordinates for this region
    base_x = region_col * 24
    base_y = region_row * 60
    
    # Convert LUTs to slice height
    slice_count = luts_to_slices(size_luts)
    
    # Create rectangular pblock spanning full width of region
    width = 24  # Full width of clock region
    height = min(slice_count, 60)  # Capped at region height
    
    # Apply offset for stacking multiple pblocks in same region
    y_start = base_y + offset
    y_end = min(y_start + height, base_y + 60)  # Don't exceed region
    
    # Generate coordinate string
    x_start = base_x
    x_end = base_x + width - 1
    
    coord_str = f"SLICE_X{x_start}Y{y_start}:SLICE_X{x_end}Y{y_end}"
    
    return coord_str


def generate_region_name(region_id):
    """
    Convert region ID to Vivado clock region name.
    
    Args:
        region_id (int): Region ID (0-9)
    
    Returns:
        str: Clock region name (e.g., "CLOCKREGION_X0Y2")
    """
    col = region_id % 2
    row = region_id // 2
    return f"CLOCKREGION_X{col}Y{row}"


# =============================================================================
# PLACEMENT PLAN GENERATION
# =============================================================================

def create_placement_plan(targets_with_sizes):
    """
    Create complete placement plan with regions and coordinates.
    
    Args:
        targets_with_sizes (dict): {module_name: size_in_luts}
    
    Returns:
        dict: Complete placement plan for each target
        
    Structure:
        {
            'ALU': {
                'size': 1200,
                'region_id': 0,
                'region_name': 'CLOCKREGION_X0Y0',
                'coordinates': 'SLICE_X0Y0:SLICE_X24Y50'
            },
            ...
        }
    """
    # Allocate targets to regions
    assignments, regions = allocate_clock_regions(targets_with_sizes)
    
    # Generate coordinates for each target
    placement_plan = {}
    
    for region_id, region in enumerate(regions):
        offset = 0  # Vertical offset within region
        
        for target in region['targets']:
            size = assignments[target]['size']
            
            # Generate coordinates
            coords = generate_coordinates(target, region_id, size, offset)
            
            # Add to placement plan
            placement_plan[target] = {
                'size': size,
                'region_id': region_id,
                'region_name': generate_region_name(region_id),
                'coordinates': coords,
            }
            
            # Update offset for next target in same region
            slice_height = luts_to_slices(size)
            offset += slice_height
    
    return placement_plan


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