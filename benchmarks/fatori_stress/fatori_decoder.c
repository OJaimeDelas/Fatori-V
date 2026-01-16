#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * Decoder Stress
 * 
 * Target Hardware: ibex_decoder.sv
 * 
 * Exercises instruction decoder by generating various instruction formats.
 * The decoder must extract opcode, function codes, register addresses,
 * and immediates from each instruction format.
 * 
 * Formats tested:
 * - R-type: register-register operations
 * - I-type: immediate operations and loads
 * - S-type: store operations
 * - U-type: upper immediate operations
 ******************************************************************************/

#if FATORI_TARGET_DECODER

uint32_t decoder_stress(uint32_t checksum, uint32_t iteration) {
    uint32_t result = 0;
    uint32_t a = iteration * 19 + 0x1111;
    uint32_t b = iteration * 29 + 0x2222;
    
    // R-type instructions (register-register)
    result ^= (a + b);
    result ^= (a - b);
    result ^= (a & b);
    result ^= (a | b);
    result ^= (a ^ b);
    result ^= (a << (b & 0x1F));
    result ^= (a >> (b & 0x1F));
    
    // I-type instructions (immediate operations)
    result ^= (a + 0x123);
    result ^= (a & 0xF0F);
    result ^= (a | 0x0F0);
    result ^= (a ^ 0xABC);
    result ^= (a << 5);
    result ^= (a >> 3);
    
    // U-type instructions (upper immediate)
    uint32_t upper = 0x12345000 + (iteration << 12);
    result ^= upper;
    result ^= (a + upper);
    
    // I-type load instructions
    volatile uint32_t temp_data[4];
    temp_data[0] = a;
    temp_data[1] = b;
    temp_data[2] = a + b;
    temp_data[3] = a - b;
    result ^= temp_data[iteration & 0x3];
    
    // S-type store instructions
    uint32_t store_val = result ^ iteration;
    temp_data[iteration & 0x3] = store_val;
    result ^= temp_data[iteration & 0x3];
    
    return checksum ^ result;
}

#else

uint32_t decoder_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif