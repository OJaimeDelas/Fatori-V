#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * LSU Stress
 * 
 * Target Hardware: ibex_load_store_unit.sv
 * 
 * Exercises the Load-Store Unit with various memory access patterns.
 * Tests different access sizes (byte, halfword, word) and patterns
 * (sequential, stride, mixed sizes).
 * 
 * Each location is written before reading to ensure deterministic behavior.
 ******************************************************************************/

#if FATORI_TARGET_LSU

static uint32_t lsu_array[64];
static uint8_t byte_array[256];

uint32_t lsu_stress(uint32_t checksum, uint32_t iteration) {
    uint32_t result = 0;
    uint32_t idx = (iteration * 17) & 0x3F;
    uint32_t write_val_0 = iteration * 19 + 0x1000;
    uint32_t write_val_1 = iteration * 23 + 0x2000;
    
    // Word accesses (32-bit)
    lsu_array[idx] = write_val_0;
    result ^= lsu_array[idx];
    
    lsu_array[(idx + 1) & 0x3F] = write_val_1;
    result ^= lsu_array[(idx + 1) & 0x3F];
    
    // Sequential access pattern
    for (int i = 0; i < 4; i++) {
        uint32_t val = iteration + i * 100;
        lsu_array[i] = val;
        result ^= lsu_array[i];
    }
    
    // Stride access pattern
    for (int i = 0; i < 4; i++) {
        uint32_t val = iteration - i * 50;
        lsu_array[i * 8] = val;
        result ^= lsu_array[i * 8];
    }
    
    // Byte accesses (8-bit)
    uint32_t byte_idx = (iteration * 13) & 0xFF;
    uint8_t byte_val = (uint8_t)(iteration * 7);
    
    byte_array[byte_idx] = byte_val;
    result ^= byte_array[byte_idx];
    
    byte_array[(byte_idx + 1) & 0xFF] = (uint8_t)(iteration * 11);
    result ^= byte_array[(byte_idx + 1) & 0xFF];
    
    // Halfword accesses (16-bit)
    uint16_t* half_ptr = (uint16_t*)lsu_array;
    uint16_t half_val = (uint16_t)(iteration * 31);
    
    half_ptr[idx & 0x1F] = half_val;
    result ^= half_ptr[idx & 0x1F];
    
    // Mixed access sizes to same location
    uint32_t mixed_val = iteration * 43 + 0xABCD;
    lsu_array[0] = mixed_val;
    result ^= *((uint8_t*)&lsu_array[0]);
    result ^= *((uint16_t*)&lsu_array[0]);
    result ^= lsu_array[0];
    
    return checksum ^ result;
}

#else

uint32_t lsu_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif