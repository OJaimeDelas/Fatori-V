#include "iob_timer_csrs.h"

// Base Address
static int base;
void IOB_TIMER_INIT_BASEADDR(uint32_t addr) { base = addr; }

// Core Setters and Getters
void IOB_TIMER_SET_RESET(uint8_t value) {
  (*((volatile uint8_t *)((base) + (IOB_TIMER_RESET_ADDR))) = (value));
}

void IOB_TIMER_SET_ENABLE(uint8_t value) {
  (*((volatile uint8_t *)((base) + (IOB_TIMER_ENABLE_ADDR))) = (value));
}

void IOB_TIMER_SET_SAMPLE(uint8_t value) {
  (*((volatile uint8_t *)((base) + (IOB_TIMER_SAMPLE_ADDR))) = (value));
}

uint32_t IOB_TIMER_GET_DATA_LOW() {
  return (*((volatile uint32_t *)((base) + (IOB_TIMER_DATA_LOW_ADDR))));
}

uint32_t IOB_TIMER_GET_DATA_HIGH() {
  return (*((volatile uint32_t *)((base) + (IOB_TIMER_DATA_HIGH_ADDR))));
}

uint16_t IOB_TIMER_GET_VERSION() {
  return (*((volatile uint16_t *)((base) + (IOB_TIMER_VERSION_ADDR))));
}
