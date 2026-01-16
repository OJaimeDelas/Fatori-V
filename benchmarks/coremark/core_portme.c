// SPDX-License-Identifier: Apache-2.0
// CoreMark port implementation for Fatori-V

#include "coremark.h"
#include "iob_timer.h"

// Seed variables - PERFORMANCE RUN
volatile ee_s32 seed1_volatile = 0x0;    
volatile ee_s32 seed2_volatile = 0x0;
volatile ee_s32 seed3_volatile = 0x66;
volatile ee_s32 seed4_volatile = ITERATIONS;
volatile ee_s32 seed5_volatile = 0;

// Timing variables
static CORE_TICKS start_time_val;
static CORE_TICKS stop_time_val;

// Start timing measurement
void start_time(void) {
    GETMYTIME(&start_time_val); 
}

// Stop timing measurement
void stop_time(void) {
    GETMYTIME(&stop_time_val);
}

// Get elapsed time in ticks
CORE_TICKS get_time(void) {
    CORE_TICKS elapsed;
    elapsed = MYTIMEDIFF(stop_time_val, start_time_val);
    return elapsed;
}

// Convert ticks to seconds (integer division - no float support)
secs_ret time_in_secs(CORE_TICKS ticks) {
    // Convert timer ticks to seconds
    // Timer runs at EE_TICKS_PER_SEC Hz
    // Return whole seconds (integer division)
    return (secs_ret)(ticks / EE_TICKS_PER_SEC);
}

// Initialize portable data
void portable_init(core_portable *p, int *argc, char *argv[]) {
    // Timer and UART already initialized by wrapper
    // Just set portable ID
    if (p) {
        p->portable_id = 1;
    }
    
    // Suppress unused warnings
    (void)argc;
    (void)argv;
}

// Finalize portable data
void portable_fini(core_portable *p) {
    // Nothing to clean up
    (void)p;
}

// Memory allocation - CoreMark uses static buffers, so these are not called
// But need to be defined for linking
#if (MEM_METHOD == MEM_MALLOC)
void *portable_malloc(ee_size_t size) {
    return NULL; // Not used in MEM_STATIC mode
}

void portable_free(void *p) {
    (void)p; // Not used in MEM_STATIC mode
}
#endif