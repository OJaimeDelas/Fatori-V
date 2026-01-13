#ifndef H_IOB_UART_CSRS_VERILATOR_H
#define H_IOB_UART_CSRS_VERILATOR_H

#include <stdint.h>

#include "iob_tasks.h"

// used address space width
#define IOB_UART_CSRS_ADDR_W 3

// used address space width
#define IOB_UART_CSRS_ADDR_W 3

// Addresses
#define IOB_UART_SOFTRESET_ADDR 0
#define IOB_UART_DIV_ADDR 2
#define IOB_UART_TXDATA_ADDR 4
#define IOB_UART_TXEN_ADDR 5
#define IOB_UART_RXEN_ADDR 6
#define IOB_UART_TXREADY_ADDR 0
#define IOB_UART_RXREADY_ADDR 1
#define IOB_UART_RXDATA_ADDR 4
#define IOB_UART_VERSION_ADDR 6

// Data widths (bit)
#define IOB_UART_SOFTRESET_W 8
#define IOB_UART_DIV_W 16
#define IOB_UART_TXDATA_W 8
#define IOB_UART_TXEN_W 8
#define IOB_UART_RXEN_W 8
#define IOB_UART_TXREADY_W 8
#define IOB_UART_RXREADY_W 8
#define IOB_UART_RXDATA_W 8
#define IOB_UART_VERSION_W 16

// Core Setters and Getters
void IOB_UART_SET_SOFTRESET(uint8_t value, iob_native_t *native_if);
void IOB_UART_SET_DIV(uint16_t value, iob_native_t *native_if);
void IOB_UART_SET_TXDATA(uint8_t value, iob_native_t *native_if);
void IOB_UART_SET_TXEN(uint8_t value, iob_native_t *native_if);
void IOB_UART_SET_RXEN(uint8_t value, iob_native_t *native_if);
uint8_t IOB_UART_GET_TXREADY(iob_native_t *native_if);
uint8_t IOB_UART_GET_RXREADY(iob_native_t *native_if);
uint8_t IOB_UART_GET_RXDATA(iob_native_t *native_if);
uint16_t IOB_UART_GET_VERSION(iob_native_t *native_if);

#endif // H_IOB_UART__CSRS_VERILATOR_H
