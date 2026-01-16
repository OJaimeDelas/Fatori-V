#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * Branch Predictor Stress
 * 
 * Target Hardware: ibex_branch_predict.sv
 * 
 * Exercises branch prediction logic with different patterns:
 * 1. Always taken - predictor should learn to always predict taken
 * 2. Stride pattern - repeating sequence the predictor can learn
 * 3. Pseudo-random - unpredictable, predictor cannot learn
 * 4. Alternating - simple pattern for two-bit predictors
 * 5. Nested loops - complex control flow
 ******************************************************************************/

#if FATORI_TARGET_BRANCH_PREDICT

uint32_t branch_predict_stress(uint32_t checksum, uint32_t iteration) {
    uint32_t result = 0;
    
    // Pattern 1: Always taken
    for (int i = 0; i < 16; i++) {
        if (i < 20) {
            result ^= (i + iteration);
        }
    }
    
    // Pattern 2: Predictable stride (taken every 4th)
    for (int i = 0; i < 32; i++) {
        if ((i & 3) == 0) {
            result ^= ((i + iteration) << 1);
        }
    }
    
    // Pattern 3: Pseudo-random (LFSR-based)
    uint16_t lfsr = (uint16_t)(iteration * 47 + 1) | 1;
    for (int i = 0; i < 32; i++) {
        uint16_t bit = ((lfsr >> 0) ^ (lfsr >> 2) ^ (lfsr >> 3) ^ (lfsr >> 5)) & 1;
        lfsr = (lfsr >> 1) | (bit << 15);
        if (lfsr & 1) {
            result ^= lfsr;
        }
    }
    
    // Pattern 4: Alternating
    for (int i = 0; i < 16; i++) {
        if (i & 1) {
            result ^= ((i + iteration) * 3);
        } else {
            result ^= ((i + iteration) * 7);
        }
    }
    
    // Pattern 5: Nested loops
    for (int i = 0; i < 8; i++) {
        for (int j = 0; j < 8; j++) {
            if ((i + j + iteration) & 1) {
                result ^= (i ^ j);
            }
        }
    }
    
    return checksum ^ result;
}

#else

uint32_t branch_predict_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif