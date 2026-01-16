#include "bench_config.h"
#include "fatori_stress.h"

/******************************************************************************
 * ALU Stress
 * 
 * Target Hardware: ibex_alu.sv
 * 
 * Exercises the Arithmetic Logic Unit through various operations:
 * - Arithmetic: ADD, SUB
 * - Logic: AND, OR, XOR
 * - Shifts: SLL, SRL, SRA
 * - Comparisons: SLT, SLTU
 * 
 * Two main patterns:
 * 1. Independent operations - can execute in parallel, tests ILP
 * 2. Dependent chains - must execute sequentially, tests forwarding
 ******************************************************************************/

#if FATORI_TARGET_ALU

uint32_t alu_stress(uint32_t checksum, uint32_t iteration) {
    // Generate test operands from iteration using different multipliers
    uint32_t a = iteration * 17;
    uint32_t b = iteration * 31;
    uint32_t c = iteration * 13 + 0x12345;
    uint32_t d = iteration * 7 + 0xABCDE;
    
    uint32_t result = 0;
    
    // Independent operations - no dependencies between them
    result ^= (a + b);           // ADD
    result ^= (c - d);           // SUB
    result ^= (a & b);           // AND
    result ^= (c | d);           // OR
    result ^= (a ^ b);           // XOR
    result ^= (c << 3);          // Shift left by constant
    result ^= (d >> 2);          // Shift right by constant
    result ^= (a << 5) >> 3;     // Combined shift operations
    
    // Dependent chain - each operation uses result of previous
    uint32_t chain = a;
    chain = chain + b;
    chain = chain - c;
    chain = chain & 0xFFFFFF;
    chain = chain | d;
    chain = chain ^ b;
    result ^= chain;
    
    // Comparison operations
    result ^= (a < b) ? 1 : 0;                    // Unsigned less-than
    result ^= (c > d) ? 2 : 0;                    // Unsigned greater-than
    result ^= ((int32_t)a < (int32_t)b) ? 4 : 0;  // Signed less-than
    
    // Variable shift operations (shift amount depends on iteration)
    result ^= (a << (iteration & 0x1F));
    result ^= (c >> (iteration & 0x1F));
    result ^= ((int32_t)a >> ((iteration + 5) & 0x1F));
    
    return checksum ^ result;
}

#else

uint32_t alu_stress(uint32_t checksum, uint32_t iteration) {
    (void)iteration;
    return checksum;
}

#endif