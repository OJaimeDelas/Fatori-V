#ifndef H_IOB_TIMER_CSRS_H
#define H_IOB_TIMER_CSRS_H

#include <stdint.h>

// used address space width
#define IOB_TIMER_CSRS_ADDR_W 4

// Addresses
#define IOB_TIMER_RESET_ADDR 0
#define IOB_TIMER_ENABLE_ADDR 1
#define IOB_TIMER_SAMPLE_ADDR 2
#define IOB_TIMER_DATA_LOW_ADDR 4
#define IOB_TIMER_DATA_HIGH_ADDR 8
#define IOB_TIMER_VERSION_ADDR 12

// Data widths (bit)
#define IOB_TIMER_RESET_W 8
#define IOB_TIMER_ENABLE_W 8
#define IOB_TIMER_SAMPLE_W 8
#define IOB_TIMER_DATA_LOW_W 32
#define IOB_TIMER_DATA_HIGH_W 32
#define IOB_TIMER_VERSION_W 16

// Base Address
void IOB_TIMER_INIT_BASEADDR(uint32_t addr);

// Core Setters and Getters
void IOB_TIMER_SET_RESET(uint8_t value);
void IOB_TIMER_SET_ENABLE(uint8_t value);
void IOB_TIMER_SET_SAMPLE(uint8_t value);
uint32_t IOB_TIMER_GET_DATA_LOW();
uint32_t IOB_TIMER_GET_DATA_HIGH();
uint16_t IOB_TIMER_GET_VERSION();

#endif // H_IOB_TIMER__CSRS_H
