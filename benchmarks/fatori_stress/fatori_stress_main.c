// SPDX-License-Identifier: MIT
// FATORI Stress Test with metrics export

#include "bench_config.h"
#include "fatori_stress.h"
#include "iob_printf.h"
#include "iob_uart.h"
#include <stdio.h>

/******************************************************************************
 * FATORI Stress Benchmark - Main
 * 
 * Self-validating benchmark using XOR-based reversibility. Runs stress
 * functions forward, then backward, and validates that the checksum returns
 * to its initial value. Any computation error breaks the XOR cancellation.
 ******************************************************************************/

// String-based storage for metrics export
static char metrics_enabled_targets[256] = "";
static char metrics_iterations[16] = "0";
static char metrics_initial_checksum[16] = "0x00000000";
static char metrics_forward_checksum[16] = "0x00000000";
static char metrics_backward_checksum[16] = "0x00000000";
static char metrics_validation[8] = "UNKNOWN";
static char metrics_first_mismatch[16] = "NONE";

static inline uint32_t apply_stress(uint32_t checksum, uint32_t iteration) {
#if FATORI_TARGET_ALU
    checksum = alu_stress(checksum, iteration);
#endif
#if FATORI_TARGET_MULTIPLIER
    checksum = multiplier_stress(checksum, iteration);
#endif
#if FATORI_TARGET_DECODER
    checksum = decoder_stress(checksum, iteration);
#endif
#if FATORI_TARGET_CONTROLLER
    checksum = controller_stress(checksum, iteration);
#endif
#if FATORI_TARGET_LSU
    checksum = lsu_stress(checksum, iteration);
#endif
#if FATORI_TARGET_BRANCH_PREDICT
    checksum = branch_predict_stress(checksum, iteration);
#endif
#if FATORI_TARGET_COMPRESSED
    checksum = compressed_stress(checksum, iteration);
#endif
    return checksum;
}

int fatori_stress_main(void) {
    const uint32_t INITIAL_CHECKSUM = 0x12345678;
    const int32_t max_iterations = FATORI_ITERATIONS;
    
    // Store for metrics export (convert to strings)
    sprintf(metrics_initial_checksum, "0x%08x", INITIAL_CHECKSUM);
    sprintf(metrics_iterations, "%d", max_iterations);
    
    // Build enabled targets string
    int offset = 0;
#if FATORI_TARGET_ALU
    offset += sprintf(metrics_enabled_targets + offset, "ALU,");
#endif
#if FATORI_TARGET_MULTIPLIER
    offset += sprintf(metrics_enabled_targets + offset, "MULTIPLIER,");
#endif
#if FATORI_TARGET_DECODER
    offset += sprintf(metrics_enabled_targets + offset, "DECODER,");
#endif
#if FATORI_TARGET_CONTROLLER
    offset += sprintf(metrics_enabled_targets + offset, "CONTROLLER,");
#endif
#if FATORI_TARGET_LSU
    offset += sprintf(metrics_enabled_targets + offset, "LSU,");
#endif
#if FATORI_TARGET_BRANCH_PREDICT
    offset += sprintf(metrics_enabled_targets + offset, "BRANCH_PREDICT,");
#endif
#if FATORI_TARGET_COMPRESSED
    offset += sprintf(metrics_enabled_targets + offset, "COMPRESSED_DECODER,");
#endif
    // Remove trailing comma
    if (offset > 0) {
        metrics_enabled_targets[offset - 1] = '\0';
    }
    
    uart_puts("\n");
    uart_puts("========================================\n");
    uart_puts("     FATORI Stress Benchmark\n");
    uart_puts("========================================\n\n");
    
    // Print enabled targets
    uart_puts("Enabled targets:\n");
#if FATORI_TARGET_ALU
    uart_puts("  - ALU\n");
#endif
#if FATORI_TARGET_MULTIPLIER
    uart_puts("  - MULTIPLIER\n");
#endif
#if FATORI_TARGET_DECODER
    uart_puts("  - DECODER\n");
#endif
#if FATORI_TARGET_CONTROLLER
    uart_puts("  - CONTROLLER\n");
#endif
#if FATORI_TARGET_LSU
    uart_puts("  - LSU\n");
#endif
#if FATORI_TARGET_BRANCH_PREDICT
    uart_puts("  - BRANCH_PREDICT\n");
#endif
#if FATORI_TARGET_COMPRESSED
    uart_puts("  - COMPRESSED_DECODER\n");
#endif
    
    uart_puts("\n");
    if (max_iterations < 0) {
        uart_puts("Iterations: infinite (no validation)\n");
    } else {
        printf("Iterations: %d\n", max_iterations);
    }
    uart_puts("========================================\n\n");
    
    // Forward pass
    uart_puts("FORWARD RUN\n");
    printf("Starting checksum: 0x%08x\n", INITIAL_CHECKSUM);
    
    uint32_t checksum = INITIAL_CHECKSUM;
    int32_t iteration = 0;
    
    uint32_t* forward_checksums = NULL;
    if (max_iterations > 0 && max_iterations <= 10000) {
        static uint32_t checksum_storage[10000];
        forward_checksums = checksum_storage;
    }
    
    while (1) {
        checksum = apply_stress(checksum, iteration);
        
        if (forward_checksums != NULL && iteration < 10000) {
            forward_checksums[iteration] = checksum;
        }
        
        if ((iteration % 100) == 0 && iteration > 0) {
            printf("  Iteration %d: 0x%08x\n", iteration, checksum);
        }
        
        iteration++;
        
        if (max_iterations >= 0 && iteration >= max_iterations) {
            break;
        }
    }
    
    uint32_t forward_checksum = checksum;
    sprintf(metrics_forward_checksum, "0x%08x", forward_checksum);
    printf("Completed %d iterations\n", iteration);
    printf("Final checksum: 0x%08x\n\n", forward_checksum);
    
    // Backward pass
    int validation_result = 0;
    
    if (max_iterations > 0) {
        uart_puts("BACKWARD RUN\n");
        printf("Starting checksum: 0x%08x\n", checksum);
        
        int32_t first_mismatch = -1;
        
        for (int32_t i = iteration - 1; i >= 0; i--) {
            checksum = apply_stress(checksum, i);
            
            if ((i % 100) == 0 && i > 0) {
                printf("  Iteration %d: 0x%08x", i, checksum);
                
                if (forward_checksums != NULL && i > 0 && i <= iteration) {
                    uint32_t expected = forward_checksums[i - 1];
                    if (checksum != expected) {
                        printf(" [MISMATCH]");
                        if (first_mismatch == -1) {
                            first_mismatch = i;
                        }
                    }
                }
                printf("\n");
            }
        }
        
        uint32_t final_checksum = checksum;
        sprintf(metrics_backward_checksum, "0x%08x", final_checksum);
        if (first_mismatch >= 0) {
            sprintf(metrics_first_mismatch, "%d", first_mismatch);
        } else {
            sprintf(metrics_first_mismatch, "NONE");
        }
        
        printf("Completed %d iterations\n", iteration);
        printf("Final checksum: 0x%08x\n\n", final_checksum);
        
        // Validation
        uart_puts("========================================\n");
        uart_puts("VALIDATION\n");
        uart_puts("========================================\n");
        printf("Expected: 0x%08x\n", INITIAL_CHECKSUM);
        printf("Got:      0x%08x\n", final_checksum);
        uart_puts("----------------------------------------\n");
        
        if (final_checksum == INITIAL_CHECKSUM) {
            uart_puts("Result: PASS\n");
            uart_puts("========================================\n\n");
            validation_result = 0;
            sprintf(metrics_validation, "PASS");
        } else {
            uart_puts("Result: FAIL\n");
            printf("Difference: 0x%08x\n", final_checksum ^ INITIAL_CHECKSUM);
            
            if (first_mismatch >= 0) {
                printf("First mismatch at iteration %d\n", first_mismatch);
            }
            
            uart_puts("========================================\n\n");
            validation_result = 1;
            sprintf(metrics_validation, "FAIL");
        }
    } else {
        uart_puts("========================================\n");
        uart_puts("VALIDATION: SKIPPED (infinite mode)\n");
        uart_puts("========================================\n\n");
        validation_result = 0;
        sprintf(metrics_validation, "SKIPPED");
    }
    
    return validation_result;
}

//=============================================================================
// METRICS EXPORT FUNCTION
//=============================================================================
int get_benchmark_metrics(char *buffer, int offset) {
    // All metrics are strings now - just write them directly!
    offset += sprintf(buffer + offset, "[benchmark] enabled_targets,%s\n", metrics_enabled_targets);
    offset += sprintf(buffer + offset, "[benchmark] iterations,%s\n", metrics_iterations);
    offset += sprintf(buffer + offset, "[benchmark] initial_checksum,%s\n", metrics_initial_checksum);
    offset += sprintf(buffer + offset, "[benchmark] forward_checksum,%s\n", metrics_forward_checksum);
    offset += sprintf(buffer + offset, "[benchmark] backward_checksum,%s\n", metrics_backward_checksum);
    offset += sprintf(buffer + offset, "[benchmark] validation,%s\n", metrics_validation);
    offset += sprintf(buffer + offset, "[benchmark] first_mismatch,%s\n", metrics_first_mismatch);
    
    return offset;
}