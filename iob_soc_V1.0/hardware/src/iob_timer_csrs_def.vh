`include "iob_timer_csrs_conf.vh"
//These macros may be dependent on instance parameters
//address macros
//addresses
`define IOB_TIMER_RESET_ADDR 0
`define IOB_TIMER_RESET_W 1

`define IOB_TIMER_ENABLE_ADDR 1
`define IOB_TIMER_ENABLE_W 1

`define IOB_TIMER_SAMPLE_ADDR 2
`define IOB_TIMER_SAMPLE_W 1

`define IOB_TIMER_DATA_LOW_ADDR 4
`define IOB_TIMER_DATA_LOW_W 32

`define IOB_TIMER_DATA_HIGH_ADDR 8
`define IOB_TIMER_DATA_HIGH_W 32

`define IOB_TIMER_VERSION_ADDR 12
`define IOB_TIMER_VERSION_W 16

