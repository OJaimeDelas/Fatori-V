#include "iob_bootrom_csrs.h"

// Base Address
static int base;
void IOB_BOOTROM_INIT_BASEADDR(uint32_t addr) { base = addr; }

// Core Setters and Getters
uint32_t IOB_BOOTROM_GET_ROM(int addr) {
  return (
      *((volatile uint32_t *)((base) + (IOB_BOOTROM_ROM_ADDR) + (addr << 2))));
}

uint16_t IOB_BOOTROM_GET_VERSION() {
  return (*((volatile uint16_t *)((base) + (IOB_BOOTROM_VERSION_ADDR))));
}
