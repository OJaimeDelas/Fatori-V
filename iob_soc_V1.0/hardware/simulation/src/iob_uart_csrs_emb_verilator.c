#include "iob_uart_csrs_verilator.h"

// Core Setters and Getters
void IOB_UART_SET_SOFTRESET(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_UART_SOFTRESET_ADDR), value, IOB_UART_SOFTRESET_W, native_if);
}

void IOB_UART_SET_DIV(uint16_t value, iob_native_t *native_if) {
  iob_write((IOB_UART_DIV_ADDR), value, IOB_UART_DIV_W, native_if);
}

void IOB_UART_SET_TXDATA(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_UART_TXDATA_ADDR), value, IOB_UART_TXDATA_W, native_if);
}

void IOB_UART_SET_TXEN(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_UART_TXEN_ADDR), value, IOB_UART_TXEN_W, native_if);
}

void IOB_UART_SET_RXEN(uint8_t value, iob_native_t *native_if) {
  iob_write((IOB_UART_RXEN_ADDR), value, IOB_UART_RXEN_W, native_if);
}

uint8_t IOB_UART_GET_TXREADY(iob_native_t *native_if) {
  return (uint8_t)iob_read((IOB_UART_TXREADY_ADDR), native_if);
}

uint8_t IOB_UART_GET_RXREADY(iob_native_t *native_if) {
  return (uint8_t)iob_read((IOB_UART_RXREADY_ADDR), native_if);
}

uint8_t IOB_UART_GET_RXDATA(iob_native_t *native_if) {
  return (uint8_t)iob_read((IOB_UART_RXDATA_ADDR), native_if);
}

uint16_t IOB_UART_GET_VERSION(iob_native_t *native_if) {
  return (uint16_t)iob_read((IOB_UART_VERSION_ADDR), native_if);
}
