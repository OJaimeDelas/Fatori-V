#ifndef BOARDSUPPORT_H
#define BOARDSUPPORT_H

#include "iob_bsp.h"
#include "iob_timer.h"

// CPU clock in MHz (required by Embench)
#define CPU_MHZ (IOB_BSP_FREQ / 1000000)

// Warmup heat (Embench uses this)
#define WARMUP_HEAT 0

// Platform initialization and timing
void initialise_board(void);
void start_trigger(void);
void stop_trigger(void);

#endif