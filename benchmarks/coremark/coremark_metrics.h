// SPDX-License-Identifier: Apache-2.0
// CoreMark metrics capture, parsing, and export

#ifndef COREMARK_METRICS_H
#define COREMARK_METRICS_H

#include <stdint.h>
#include <stdarg.h>

// Forward declare printf for capture function signature
// Actual implementation uses iob_printf
int printf(const char *format, ...);

//=============================================================================
// CoreMark Output Capture
//=============================================================================
// Initialize capture system
void coremark_metrics_init(void);

// Custom printf that captures output
int coremark_printf(const char *format, ...);

//=============================================================================
// CoreMark Metrics Parsing
//=============================================================================
// Parse captured output and extract metrics
void coremark_metrics_parse(void);

//=============================================================================
// CoreMark Metrics Export
//=============================================================================
// Export metrics in standard format
// Returns: new buffer offset
int coremark_metrics_export(char *buffer, int offset);

#endif // COREMARK_METRICS_H