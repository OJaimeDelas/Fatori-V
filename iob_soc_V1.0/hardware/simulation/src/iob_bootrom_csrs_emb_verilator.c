#include "iob_bootrom_csrs_verilator.h"

// Core Setters and Getters
uint32_t IOB_BOOTROM_GET_ROM(int addr, iob_native_t *native_if) {
  return (uint32_t)iob_read((IOB_BOOTROM_ROM_ADDR) + (addr << 2), native_if);
}

uint16_t IOB_BOOTROM_GET_VERSION(iob_native_t *native_if) {
  return (uint16_t)iob_read((IOB_BOOTROM_VERSION_ADDR), native_if);
}
