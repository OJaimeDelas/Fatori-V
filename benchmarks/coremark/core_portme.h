// SPDX-License-Identifier: Apache-2.0
// CoreMark port for IOb-SoC RISC-V platform

#ifndef CORE_PORTME_H
#define CORE_PORTME_H

#include <stdint.h>
#include <stddef.h>
#include "iob_bsp.h"
#include "iob_timer.h"
#include "iob_uart.h"
#include "iob_printf.h"
#include "bench_config.h"

/************************/
/* Data types and psecs */
/************************/
// Basic types
typedef int16_t  ee_s16;
typedef uint16_t ee_u16;
typedef int32_t  ee_s32;
typedef uint32_t ee_u32;
typedef uint8_t  ee_u8;
typedef double   ee_f32;
typedef size_t   ee_size_t;
typedef uintptr_t ee_ptr_int;

// Timing type
typedef uint64_t CORE_TICKS;

// Portable struct (used by CoreMark for context)
typedef struct CORE_PORTABLE_S {
    ee_u8 portable_id;
} core_portable;

/*****************************/
/* Configuration             */
/*****************************/
// Memory allocation - use static buffers
#define MEM_METHOD              MEM_STATIC
#define MEM_LOCATION            "STATIC"

// Multicore/threading - single core
#define MULTITHREAD             1
#define USE_PTHREAD             0
#define USE_FORK                0
#define USE_SOCKET              0

// Number of contexts (1 = single threaded)
#ifndef MAIN_HAS_NOARGC
#define MAIN_HAS_NOARGC         1
#endif

#define default_num_contexts    MULTITHREAD

// Compiler info
#define COMPILER_VERSION        "GCC RISC-V"
#define COMPILER_FLAGS          " "


#define HAS_FLOAT               0
#define HAS_TIME_H              0
#define USE_CLOCK               0
#define HAS_STDIO               1
#define HAS_PRINTF              0

// Defined in bench_config.h
//#define ITERATIONS 1000

// Seed configuration
#define SEED_METHOD SEED_VOLATILE

// Run mode - choose ONE:
#define PERFORMANCE_RUN 1
// #define VALIDATION_RUN 1  
// #define PROFILE_RUN 1

/*****************************/
/* Timing functions          */
/*****************************/
#define CORETIMETYPE            CORE_TICKS
#define GETMYTIME(_t)           (*_t = barebones_clock())
#define MYTIMEDIFF(fin, ini)    ((fin) - (ini))
#define TIMER_RES_DIVISOR       1
#define NSECS_PER_SEC           IOB_BSP_FREQ
#define EE_TICKS_PER_SEC        (NSECS_PER_SEC / TIMER_RES_DIVISOR)
#define SAMPLE_TIME_IMPLEMENTATION 1



// Get current time from timer
static inline CORE_TICKS barebones_clock(void) {
    return timer_get_count();
}

/*****************************/
/* Memory alignment          */
/*****************************/
#define ALIGN_SIZE              (sizeof(void *))

static inline void *align_mem(void *ptr) {
    ee_ptr_int addr = (ee_ptr_int)ptr;
    addr = (addr + ALIGN_SIZE - 1) & ~(ALIGN_SIZE - 1);
    return (void *)addr;
}

/*****************************/
/* Printf function           */
/*****************************/
// Forward declare our capture function
int coremark_printf(const char *format, ...);

// Use our capture function instead of printf
#define ee_printf               coremark_printf

/*****************************/
/* Function declarations     */
/*****************************/
void portable_init(core_portable *p, int *argc, char *argv[]);
void portable_fini(core_portable *p);

#endif /* CORE_PORTME_H */