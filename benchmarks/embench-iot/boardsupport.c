// SPDX-License-Identifier: MIT
#include "boardsupport.h"

// These functions are required by Embench but unused in our implementation
// We do timing in embench_main.c using CSR reads directly

void initialise_board(void) {
    // Timer and UART already initialized by main wrapper
}

void start_trigger(void) {
    // Not used - timing done in embench_main.c
}

void stop_trigger(void) {
    // Not used - timing done in embench_main.c
}