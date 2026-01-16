// SPDX-License-Identifier: MIT
#include "embench_score.h"

uint32_t compute_embench_score(const uint64_t* baseline, const uint64_t* measured, uint8_t count) {
    // Compute arithmetic mean of ratios as approximation of geometric mean
    // Real geometric mean requires floating point or complex integer math
    uint64_t sum_ratios = 0;
    
    for (uint8_t i = 0; i < count; i++) {
        if (measured[i] == 0) continue;
        
        // Ratio = (baseline[i] * 1000) / measured[i]
        uint64_t ratio = ((uint64_t)baseline[i] * 1000ULL) / measured[i];
        sum_ratios += ratio;
    }
    
    // Arithmetic mean
    return (uint32_t)(sum_ratios / count);
}