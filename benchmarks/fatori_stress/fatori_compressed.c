#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * Compressed Decoder Stress
 * 
 * Target Hardware: ibex_compressed_decoder.sv
 * 
 * Generates code patterns that compile to compressed instructions when
 * RV32C extension is enabled. The compressed decoder expands 16-bit
 * instructions to their 32-bit equivalents.
 * 
 * If RV32C is not available, the same C code compiles to standard 32-bit
 * instructions, which simply doesn't exercise the compressed decoder.
 ******************************************************************************/

#if FATORI_TARGET_COMPRESSED

uint32_t compressed_stress(uint32_t checksum, uint32_t iteration) {
    uint32_t result = 0;
    register uint32_t a = iteration * 53;
    register uint32_t b = iteration * 61;
    
    // Small immediate operations
    result = 5;
    result = 10;
    result += 1;
    result += 2;
    result += 4;
    
    // Register operations
    result = a + b;
    uint32_t temp = result;
    result = temp;
    result = a - b;
    result = b - a;
    
    // Logical operations
    result &= a;
    result |= b;
    result ^= (iteration * 71);
    
    // Control flow
    for (int i = 0; i < 10; i++) {
        result ^= (i + iteration);
    }
    
    // Stack operations
    volatile uint32_t stack_var = iteration * 79;
    result ^= stack_var;
    stack_var = result;
    result ^= stack_var;
    
    return checksum ^ result;
}

#else

uint32_t compressed_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif