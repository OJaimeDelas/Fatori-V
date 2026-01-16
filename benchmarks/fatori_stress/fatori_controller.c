#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * Controller Stress
 * 
 * Target Hardware: ibex_controller.sv
 * 
 * Exercises the control state machine through branches, loops, and calls.
 * The controller manages PC updates, branch decisions, and pipeline control.
 * 
 * Patterns tested:
 * - Conditional branches (taken and not-taken)
 * - Nested conditionals
 * - Loops (backward branches)
 * - Function calls (JAL/JALR)
 ******************************************************************************/

#if FATORI_TARGET_CONTROLLER

static uint32_t __attribute__((noinline)) controller_helper(uint32_t val) {
    return val ^ 0xDEADBEEF;
}

uint32_t controller_stress(uint32_t checksum, uint32_t iteration) {
    uint32_t result = 0;
    uint32_t counter = (iteration * 37) & 0xFF;
    
    // Conditional branches
    if (counter > 50) result ^= 1;
    if (counter > 150) result ^= 2;
    if (counter < 200) result ^= 4;
    
    if ((counter & 1) == 0) {
        result ^= 8;
    } else {
        result ^= 16;
    }
    
    // Nested conditionals
    if (counter < 128) {
        if (counter < 64) {
            result ^= 32;
        } else {
            result ^= 64;
        }
    }
    
    // Loop with backward branch
    for (uint32_t i = 0; i < 10; i++) {
        result ^= (i + iteration);
    }
    
    // Function call
    result ^= controller_helper(iteration);
    
    return checksum ^ result;
}

#else

uint32_t controller_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif