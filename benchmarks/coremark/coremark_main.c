// SPDX-License-Identifier: Apache-2.0
// CoreMark entry point with metrics export

#include "coremark_metrics.h"
#include "iob_printf.h"

// Rename CoreMark's main() before including it
#define main coremark_main_impl

// Include CoreMark's main source
// CoreMark repo code remains completely unmodified
// NOTE: core_portme.h defines ee_printf as coremark_printf for capture
#include "repo/core_main.c"

// Restore main definition
#undef main

//=============================================================================
// CoreMark Wrapper Entry Point  
//=============================================================================
// Our debug output uses printf (goes to console, not captured)
// CoreMark's output uses ee_printf which is captured via core_portme.h
int coremark_main(void) {
    // Initialize metrics capture
    coremark_metrics_init();
    
    // Run CoreMark (ee_printf output will be captured)
    int result = coremark_main_impl();
    
    // Parse captured output to extract metrics
    coremark_metrics_parse();
    
    return result;
}

//=============================================================================
// METRICS EXPORT FUNCTION
//=============================================================================
// Called by firmware to export metrics
int get_benchmark_metrics(char *buffer, int offset) {
    return coremark_metrics_export(buffer, offset);
}