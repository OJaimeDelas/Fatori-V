#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * Multiplier Stress
 * 
 * Target Hardware: ibex_multdiv_fast.sv or ibex_multdiv_slow.sv
 * 
 * Tests multiply and divide operations. If RV32M extension is available,
 * uses hardware multiplier/divider. Otherwise falls back to software
 * implementation using shifts and loops.
 * 
 * Operations tested:
 * - Unsigned multiply, divide, modulo
 * - Signed multiply, divide, modulo
 * - High multiply (upper 32 bits of 64-bit product)
 ******************************************************************************/

#if FATORI_TARGET_MULTIPLIER

uint32_t multiplier_stress(uint32_t checksum, uint32_t iteration) {
    // Generate non-zero operands (OR with 1 prevents divide by zero)
    uint32_t a = (iteration * 23 + 0x1000) | 1;
    uint32_t b = (iteration * 41 + 0x2000) | 1;
    
    uint32_t result = 0;
    
#ifdef __riscv_mul
    // Hardware multiply/divide operations
    result ^= (a * b);
    result ^= (a / b);
    result ^= (a % b);
    
    // Signed operations
    int32_t sa = (int32_t)a;
    int32_t sb = (int32_t)(b | 0x80000000);
    result ^= (uint32_t)(sa * sb);
    result ^= (uint32_t)(sa / sb);
    result ^= (uint32_t)(sa % sb);
    
    // High multiply
    uint64_t prod = (uint64_t)a * (uint64_t)b;
    result ^= (uint32_t)(prod >> 32);
    
#else
    // Software multiply via shift-and-add
    uint32_t mul_result = 0;
    for (int i = 0; i < 8; i++) {
        if (b & (1 << i)) {
            mul_result += (a << i);
        }
    }
    result ^= mul_result;
    
    // Software divide via repeated subtraction
    if (b != 0) {
        uint32_t div_result = 0;
        uint32_t remainder = a;
        for (int i = 31; i >= 0; i--) {
            if (remainder >= (b << i)) {
                remainder -= (b << i);
                div_result |= (1 << i);
            }
        }
        result ^= div_result;
        result ^= remainder;
    }
#endif
    
    return checksum ^ result;
}

#else

uint32_t multiplier_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif