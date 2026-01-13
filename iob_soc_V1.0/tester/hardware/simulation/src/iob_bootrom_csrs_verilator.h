#ifndef H_IOB_BOOTROM_CSRS_VERILATOR_H
#define H_IOB_BOOTROM_CSRS_VERILATOR_H

#include <stdint.h>

#include "iob_tasks.h"

// used address space width
#define IOB_BOOTROM_CSRS_ADDR_W 13

// used address space width
#define IOB_BOOTROM_CSRS_ADDR_W 13

// Addresses
#define IOB_BOOTROM_ROM_ADDR 0
#define IOB_BOOTROM_VERSION_ADDR 4096

// Data widths (bit)
#define IOB_BOOTROM_ROM_W 32
#define IOB_BOOTROM_VERSION_W 16

// Core Setters and Getters
uint32_t IOB_BOOTROM_GET_ROM(int addr, iob_native_t *native_if);
uint16_t IOB_BOOTROM_GET_VERSION(iob_native_t *native_if);

#endif // H_IOB_BOOTROM__CSRS_VERILATOR_H
