// SPDX-License-Identifier: MIT
// Minimal firmware wrapper for IOb-SoC benchmarks with metrics collection

#include "benchmark.h"
#include "iob_bsp.h"
#include "iob_csr.h"
#include "iob_printf.h"
#include "iob_soc_conf.h"
#include "iob_soc_mmap.h"
#include "iob_timer.h"
#include "iob_uart.h"
#include <stdint.h>
#include <string.h>

// Metrics collection interface
#include "benchmark_metrics.h"

//=============================================================================
// Metrics Collection Buffer
//=============================================================================
// Allocate static buffer for metrics (no malloc needed)
// Format: CSV-like with [stage] prefix
// Example: [pre] mcycle,0x0000000000001234
//          [benchmark] coremark_size,666
#define METRICS_BUFFER_SIZE 8192 // 8KB for CSRs + benchmark metrics
static char metrics_buffer[METRICS_BUFFER_SIZE];
static int metrics_offset = 0;

//=============================================================================
// Helper Functions
//=============================================================================

// Add header to metrics file
static void metrics_add_header(void) {
  metrics_offset = append_to_buffer(metrics_buffer, metrics_offset,
                                    "# FATORI-V Metrics Collection\n");
  metrics_offset = append_to_buffer(metrics_buffer, metrics_offset,
                                    "# Benchmark: %s\n", BENCHMARK_NAME);
  metrics_offset = append_to_buffer(metrics_buffer, metrics_offset,
                                    "# Version: %s\n", BENCHMARK_VERSION);
  metrics_offset = append_to_buffer(metrics_buffer, metrics_offset,
                                    "# Format: [stage] metric_name,value\n");
  metrics_offset = append_to_buffer(metrics_buffer, metrics_offset, "#\n");
}

// Record CSRs at specific stage (pre/post/mid/etc.)
static void metrics_record_csrs(const char *stage) {
  metrics_offset =
      write_all_csrs_to_buffer(metrics_buffer, metrics_offset, stage);
}

// Collect benchmark-specific metrics
static void metrics_record_benchmark(void) {

  // Try direct metrics export (all benchmarks now support this)
  if (get_benchmark_metrics != NULL) {
    metrics_offset = get_benchmark_metrics(metrics_buffer, metrics_offset);
    uart_puts("[Metrics] Benchmark metrics collected\n\n");
  } else {
    uart_puts("[Metrics] No metrics export available for this benchmark\n\n");
  }
}

// Send metrics file via UART
static void metrics_send_file(void) {
  uart_puts("\n");
  uart_puts("========================================\n");
  uart_puts("   Sending Metrics File\n");
  uart_puts("========================================\n");
  printf("Buffer size: %d bytes\n", metrics_offset);
  uart_puts("Sending via UART...\n\n");

  // Send the metrics buffer as a file
  uart_sendfile("metrics.txt", metrics_offset, metrics_buffer);

  uart_puts("Metrics file sent successfully!\n");
  uart_puts("========================================\n\n");
}

// Send sync file for FI system
static void send_sync_file(void) {
  // Create small buffer for sync file
  static char sync_buffer[] = "fi system starter\n";
  int sync_size = sizeof(sync_buffer) - 1; // Exclude null terminator

  uart_puts("= Sending via UART...\n\n");

  // Send the sync buffer as a file
  uart_sendfile("sync_file.sync", sync_size, sync_buffer);

  uart_puts("= Sync file sent successfully!\n");
}

//=============================================================================
// Main Entry Point
//=============================================================================
int main(void) {
  int result = 0;

  // Initialize peripherals
  timer_init(TIMER0_BASE);
  uart_init(UART0_BASE, IOB_BSP_FREQ / IOB_BSP_BAUD);
  printf_init(&uart_putc);

  // Print header
  uart_puts("\n\n");
  uart_puts("========================================\n");
  uart_puts("   FATORI-V Benchmark Execution\n");
  uart_puts("========================================\n");
  printf("Benchmark: %s\n", BENCHMARK_NAME);
  printf("Version:   %s\n", BENCHMARK_VERSION);
  uart_puts("========================================\n\n");

  //=========================================================================
  // Initialize Metrics Collection
  //=========================================================================
  metrics_offset = 0;
  metrics_add_header();

  //=========================================================================
  // Print and Record CSRs BEFORE Benchmark
  //=========================================================================
  print_all_csrs();
  metrics_record_csrs("pre");

  //=========================================================================
  // Run Benchmark
  //=========================================================================

  uart_puts("\n=================================================\n");
  uart_puts("\n=================================================\n");
  uart_puts("=== Sending FI Sync FIle ===\n\n");

  // The FI system expects a sync file to know when to start injecting faults
  send_sync_file();

  uart_puts("\n=================================================\n");
  uart_puts("=== Running Benchmark ===\n\n");

  result = BENCHMARK_MAIN();

  uart_puts("\n=== Benchmark Complete ===\n");

  uart_puts("=================================================\n");
  uart_puts("=================================================\n");

  //=========================================================================
  // Print and Record CSRs AFTER Benchmark
  //=========================================================================
  print_all_csrs();
  metrics_record_csrs("post");

  //=========================================================================
  // Collect Benchmark-Specific Metrics
  //=========================================================================
  metrics_record_benchmark();

  //=========================================================================
  // Send Metrics File via UART
  //=========================================================================
  metrics_send_file();

  //=========================================================================
  // Print Result
  //=========================================================================
  printf("BENCH RESULT: %s\n\n", result == 0 ? "PASS" : "FAIL");

  uart_finish();
  return result;
}