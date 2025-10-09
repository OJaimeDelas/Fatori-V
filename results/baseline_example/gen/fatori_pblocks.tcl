# =============================================================================
# FATORI-V • Generated Vivado TCL (Pblocks)
# File: fatori_pblocks.tcl
# -----------------------------------------------------------------------------
# Board: xcku040
# =============================================================================

create_pblock pb_alu
resize_pblock [get_pblocks pb_alu] -add {SLICE_X60Y80:SLICE_X90Y120}

create_pblock pb_branch_predictor
resize_pblock [get_pblocks pb_branch_predictor] -add {SLICE_X100Y50:SLICE_X120Y90}

