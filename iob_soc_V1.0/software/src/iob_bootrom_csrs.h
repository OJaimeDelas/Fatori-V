#ifndef H_IOB_BOOTROM_CSRS_H
#define H_IOB_BOOTROM_CSRS_H

#include <stdint.h>

// used address space width
#define IOB_BOOTROM_CSRS_ADDR_W 13

// Addresses
#define IOB_BOOTROM_ROM_ADDR 0
#define IOB_BOOTROM_VERSION_ADDR 4096

// Data widths (bit)
#define IOB_BOOTROM_ROM_W 32
#define IOB_BOOTROM_VERSION_W 16

// Base Address
void IOB_BOOTROM_INIT_BASEADDR(uint32_t addr);

// Core Setters and Getters
uint32_t IOB_BOOTROM_GET_ROM(int addr);
uint16_t IOB_BOOTROM_GET_VERSION();

#endif // H_IOB_BOOTROM__CSRS_H
