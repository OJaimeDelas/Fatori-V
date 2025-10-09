// =============================================================================
// FATORI-V • Generated Defines (Pblocks)
// File: fatori_pblocks.svh
// -----------------------------------------------------------------------------
// Run: baseline_example
// Seed: 123456
// 'FATORI_TARGET_<NAME>' expands to 1 or 0.
// 'FATORI_ATTR_<NAME>' expands to synthesis attributes when enabled.
// =============================================================================

`ifndef FATORI_PBLOCKS_SVH
`define FATORI_PBLOCKS_SVH

`define FATORI_TARGET_ALU 1
`define FATORI_ATTR_ALU (* keep_hierarchy = "yes", dont_touch = "true" *)

`define FATORI_TARGET_BRANCH_PREDICTOR 1
`define FATORI_ATTR_BRANCH_PREDICTOR (* keep_hierarchy = "yes", dont_touch = "true" *)

`define FATORI_TARGET_MULTIPLIER 0
`define FATORI_ATTR_MULTIPLIER 

`endif  // FATORI_PBLOCKS_SVH
