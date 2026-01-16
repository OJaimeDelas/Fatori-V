// SPDX-License-Identifier: MIT
// Embench-IoT Suite wrapper for FATORI-V with string-based metrics

#include "bench_config.h"
#include "embench_benchmarks.h"
#include "embench_data.h"
#include "embench_score.h"
#include "iob_printf.h"
#include "iob_uart.h"
#include "iob_csr.h"
#include <stdint.h>
#include <stdio.h>

// Storage for results (no malloc in baremetal)
#define MAX_BENCHMARKS 21
static uint64_t measured_cycles[MAX_BENCHMARKS];
static uint8_t benchmark_passed[MAX_BENCHMARKS];
static uint8_t benchmark_index = 0;

// String-based metrics storage for export
static char metrics_total_benchmarks[16] = "0";
static char metrics_total_passed[16] = "0";
static char metrics_embench_score[32] = "0.000";
static char metrics_per_bench_cycles[MAX_BENCHMARKS][32];
static char metrics_per_bench_pass[MAX_BENCHMARKS][8];
static char metrics_per_bench_ratio[MAX_BENCHMARKS][32];

int embench_main(void) {
    int result;
    uint64_t start, end;
    
    uart_puts("\n");
    uart_puts("========================================\n");
    uart_puts("   Embench-IoT Suite\n");
    uart_puts("========================================\n\n");
    
    benchmark_index = 0;
    
    // Macro to run benchmark and track timing
    #define RUN_BENCH(name, idx) \
        do { \
            int verify_result; \
            uart_puts("Running " #name "... "); \
            initialise_benchmark_##name(); \
            start = read_mcycle_low() | ((uint64_t)read_mcycle_high() << 32); \
            result = benchmark_##name(); \
            end = read_mcycle_low() | ((uint64_t)read_mcycle_high() << 32); \
            measured_cycles[idx] = end - start; \
            verify_result = verify_benchmark_##name(result); \
            benchmark_passed[idx] = verify_result; \
            printf("%s (%llu cycles) [verify=%d, result=%d]\n", \
                benchmark_passed[idx] ? "PASS" : "FAIL", \
                measured_cycles[idx], verify_result, result); \
            benchmark_index++; \
        } while(0)
    
    #if EMBENCH_AHA_MONT64
    RUN_BENCH(aha_mont64, benchmark_index);
    #endif

    #if EMBENCH_CRC32
    RUN_BENCH(crc32, benchmark_index);
    #endif

    #if EMBENCH_CUBIC
    RUN_BENCH(cubic, benchmark_index);
    #endif

    #if EMBENCH_EDN
    RUN_BENCH(edn, benchmark_index);
    #endif

    #if EMBENCH_HUFFBENCH
    RUN_BENCH(huffbench, benchmark_index);
    #endif

    #if EMBENCH_MATMULT_INT
    RUN_BENCH(matmult_int, benchmark_index);
    #endif

    #if EMBENCH_MD5SUM
    RUN_BENCH(md5sum, benchmark_index);
    #endif

    #if EMBENCH_MINVER
    RUN_BENCH(minver, benchmark_index);
    #endif

    #if EMBENCH_NBODY
    RUN_BENCH(nbody, benchmark_index);
    #endif

    #if EMBENCH_NETTLE_AES
    RUN_BENCH(nettle_aes, benchmark_index);
    #endif

    #if EMBENCH_NETTLE_SHA256
    RUN_BENCH(nettle_sha256, benchmark_index);
    #endif

    #if EMBENCH_NSICHNEU
    RUN_BENCH(nsichneu, benchmark_index);
    #endif

    #if EMBENCH_PICOJPEG
    RUN_BENCH(picojpeg, benchmark_index);
    #endif

    #if EMBENCH_PRIMECOUNT
    RUN_BENCH(primecount, benchmark_index);
    #endif

    #if EMBENCH_QRDUINO
    RUN_BENCH(qrduino, benchmark_index);
    #endif

    #if EMBENCH_SGLIB_COMBINED
    RUN_BENCH(sglib_combined, benchmark_index);
    #endif

    #if EMBENCH_SLRE
    RUN_BENCH(slre, benchmark_index);
    #endif

    #if EMBENCH_ST
    RUN_BENCH(st, benchmark_index);
    #endif

    #if EMBENCH_STATEMATE
    RUN_BENCH(statemate, benchmark_index);
    #endif

    #if EMBENCH_UD
    RUN_BENCH(ud, benchmark_index);
    #endif

    #if EMBENCH_WIKISORT
    RUN_BENCH(wikisort, benchmark_index);
    #endif
    
    // Compute score
    uint32_t embench_score_x1000 = compute_embench_score(baseline_cycles, measured_cycles, benchmark_index);
    
    uart_puts("\n========================================\n");
    uart_puts("   Embench Results\n");
    uart_puts("========================================\n");
    
    // Print individual results
    uint8_t total_passed = 0;
    for (uint8_t i = 0; i < benchmark_index; i++) {
        uint32_t ratio = ((uint64_t)baseline_cycles[i] * 1000ULL) / measured_cycles[i];
        printf("%-18s: %llu cycles (ratio: %u.%03u)\n", 
               benchmark_names[i], measured_cycles[i], ratio/1000, ratio%1000);
        if (benchmark_passed[i]) total_passed++;
    }
    
    printf("\nPassed: %u/%u\n", total_passed, benchmark_index);
    printf("Embench Score: %u.%03u (vs ARM Cortex-M4 baseline)\n", 
           embench_score_x1000/1000, embench_score_x1000%1000);
    uart_puts("========================================\n\n");
    
    //=========================================================================
    // Convert metrics to strings for export
    //=========================================================================
    sprintf(metrics_total_benchmarks, "%u", benchmark_index);
    sprintf(metrics_total_passed, "%u", total_passed);
    sprintf(metrics_embench_score, "%u.%03u", embench_score_x1000/1000, embench_score_x1000%1000);
    
    // Convert per-benchmark metrics to strings
    for (uint8_t i = 0; i < benchmark_index; i++) {
        uint32_t ratio = ((uint64_t)baseline_cycles[i] * 1000ULL) / measured_cycles[i];
        sprintf(metrics_per_bench_cycles[i], "%llu", measured_cycles[i]);
        sprintf(metrics_per_bench_pass[i], "%u", benchmark_passed[i]);
        sprintf(metrics_per_bench_ratio[i], "%u.%03u", ratio/1000, ratio%1000);
    }
    
    return (total_passed == benchmark_index) ? 0 : 1;
}

//=============================================================================
// METRICS EXPORT FUNCTION
//=============================================================================
// This function is called by the firmware wrapper to export metrics
// Returns: new buffer offset after writing metrics
//=============================================================================
int get_benchmark_metrics(char *buffer, int offset) {
    // Overall metrics (all strings now!)
    offset += sprintf(buffer + offset, "[benchmark] total_benchmarks,%s\n", metrics_total_benchmarks);
    offset += sprintf(buffer + offset, "[benchmark] total_passed,%s\n", metrics_total_passed);
    offset += sprintf(buffer + offset, "[benchmark] embench_score,%s\n", metrics_embench_score);
    
    // Per-benchmark metrics (all strings!)
    for (uint8_t i = 0; i < benchmark_index; i++) {
        offset += sprintf(buffer + offset, "[benchmark] %s_cycles,%s\n", 
                         benchmark_names[i], metrics_per_bench_cycles[i]);
        offset += sprintf(buffer + offset, "[benchmark] %s_pass,%s\n", 
                         benchmark_names[i], metrics_per_bench_pass[i]);
        offset += sprintf(buffer + offset, "[benchmark] %s_ratio,%s\n", 
                         benchmark_names[i], metrics_per_bench_ratio[i]);
    }
    
    return offset;
}