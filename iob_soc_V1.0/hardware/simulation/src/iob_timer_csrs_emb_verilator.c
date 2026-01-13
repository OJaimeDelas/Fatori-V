#include "iob_timer_csrs_verilator.h"

// Core Setters and Getters
void IOB_TIMER_SET_RESET(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_TIMER_RESET_ADDR), value, IOB_TIMER_RESET_W, native_if);
}

void IOB_TIMER_SET_ENABLE(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_TIMER_ENABLE_ADDR), value, IOB_TIMER_ENABLE_W, native_if);
}

void IOB_TIMER_SET_SAMPLE(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_TIMER_SAMPLE_ADDR), value, IOB_TIMER_SAMPLE_W, native_if);
}

uint32_t IOB_TIMER_GET_DATA_LOW(iob_native_t *native_if) {
  return (uint32_t)iob_read((IOB_TIMER_DATA_LOW_ADDR), native_if);
}

uint32_t IOB_TIMER_GET_DATA_HIGH(iob_native_t *native_if) {
  return (uint32_t)iob_read((IOB_TIMER_DATA_HIGH_ADDR), native_if);
}

uint16_t IOB_TIMER_GET_VERSION(iob_native_t *native_if) {
  return (uint16_t)iob_read((IOB_TIMER_VERSION_ADDR), native_if);
}
