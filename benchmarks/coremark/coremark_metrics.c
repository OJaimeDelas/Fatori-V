// SPDX-License-Identifier: Apache-2.0
// CoreMark metrics capture, parsing, and export implementation

#include "coremark_metrics.h"
#include "iob_printf.h"
#include "iob_uart.h"
#include <stdarg.h>
#include <string.h>

//=============================================================================
// Output Capture Buffer
//=============================================================================
#define COREMARK_OUTPUT_SIZE 8192
static char coremark_output_buffer[COREMARK_OUTPUT_SIZE];
static int coremark_output_offset = 0;

//=============================================================================
// Parsed Metrics Storage (as strings!)
//=============================================================================
static char metrics_coremark_size[32] = "0";
static char metrics_total_ticks[32] = "0";
static char metrics_total_time_secs[32] = "0";
static char metrics_iterations_per_sec[32] = "0";
static char metrics_iterations[32] = "0";
static char metrics_memory_location[32] = "Unknown";
static char metrics_seedcrc[16] = "0x0000";
static char metrics_crclist[16] = "0x0000";
static char metrics_crcmatrix[16] = "0x0000";
static char metrics_crcstate[16] = "0x0000";
static char metrics_crcfinal[16] = "0x0000";

//=============================================================================
// Capture Functions
//=============================================================================

void coremark_metrics_init(void) {
    coremark_output_offset = 0;
    coremark_output_buffer[0] = '\0';
    
    // Reset all metrics (just strings now!)
    strcpy(metrics_coremark_size, "0");
    strcpy(metrics_total_ticks, "0");
    strcpy(metrics_total_time_secs, "0");
    strcpy(metrics_iterations_per_sec, "0");
    strcpy(metrics_iterations, "0");
    strcpy(metrics_memory_location, "Unknown");
    strcpy(metrics_seedcrc, "0x0000");
    strcpy(metrics_crclist, "0x0000");
    strcpy(metrics_crcmatrix, "0x0000");
    strcpy(metrics_crcstate, "0x0000");
    strcpy(metrics_crcfinal, "0x0000");
}

int coremark_printf(const char *format, ...) {
    va_list args1, args2;
    int written = 0;
    char temp_buffer[256];
    
    // Print to console
    va_start(args1, format);
    written = vprintf(format, args1);
    va_end(args1);
    
    // Capture to buffer
    if (coremark_output_offset + written < COREMARK_OUTPUT_SIZE) {
        va_start(args2, format);
        int added = vsprintf(coremark_output_buffer + coremark_output_offset, 
                            format, args2);
        coremark_output_offset += added;
        va_end(args2);
    }
    
    return written;
}

//=============================================================================
// Parsing Functions
//=============================================================================

void coremark_metrics_parse(void) {
    const char *line;
    
    
    // Parse CoreMark Size - extract as string
    if ((line = strstr(coremark_output_buffer, "CoreMark Size")) != NULL) {
        sscanf(line, "CoreMark Size    : %31s", metrics_coremark_size);
    } 
    
    // Parse Total ticks - extract as string
    if ((line = strstr(coremark_output_buffer, "Total ticks")) != NULL) {
        sscanf(line, "Total ticks      : %31s", metrics_total_ticks);
    }
    
    // Parse Total time (secs) - extract as string
    if ((line = strstr(coremark_output_buffer, "Total time (secs)")) != NULL) {
        sscanf(line, "Total time (secs): %31s", metrics_total_time_secs);
    }
    
    // Parse Iterations/Sec - extract as string (works for both int and float!)
    if ((line = strstr(coremark_output_buffer, "Iterations/Sec")) != NULL) {
        sscanf(line, "Iterations/Sec   : %31s", metrics_iterations_per_sec);
    } 
    
    // Parse Iterations - extract as string
    if ((line = strstr(coremark_output_buffer, "Iterations       :")) != NULL) {
        sscanf(line, "Iterations       : %31s", metrics_iterations);
    }
    
    // Parse Memory location - extract as string
    if ((line = strstr(coremark_output_buffer, "Memory location")) != NULL) {
        sscanf(line, "Memory location  : %31s", metrics_memory_location);
    }
    
    // Parse seedcrc - extract as string
    if ((line = strstr(coremark_output_buffer, "seedcrc")) != NULL) {
        sscanf(line, "seedcrc          : %15s", metrics_seedcrc);
    }
    
    // Parse [0]crclist - extract as string
    if ((line = strstr(coremark_output_buffer, "[0]crclist")) != NULL) {
        sscanf(line, "[0]crclist       : %15s", metrics_crclist);
    }
    
    // Parse [0]crcmatrix - extract as string
    if ((line = strstr(coremark_output_buffer, "[0]crcmatrix")) != NULL) {
        sscanf(line, "[0]crcmatrix     : %15s", metrics_crcmatrix);
    }
    
    // Parse [0]crcstate - extract as string
    if ((line = strstr(coremark_output_buffer, "[0]crcstate")) != NULL) {
        sscanf(line, "[0]crcstate      : %15s", metrics_crcstate);
    }
    
    // Parse [0]crcfinal - extract as string
    if ((line = strstr(coremark_output_buffer, "[0]crcfinal")) != NULL) {
        sscanf(line, "[0]crcfinal      : %15s", metrics_crcfinal);
    }
}

//=============================================================================
// Export Functions
//=============================================================================

int coremark_metrics_export(char *buffer, int offset) {
    int start_offset = offset;

    
    // Just write the strings directly - no formatting needed!
    offset += sprintf(buffer + offset, "[benchmark] coremark_size,%s\n", 
                     metrics_coremark_size);
    offset += sprintf(buffer + offset, "[benchmark] total_ticks,%s\n", 
                     metrics_total_ticks);
    offset += sprintf(buffer + offset, "[benchmark] total_time_secs,%s\n", 
                     metrics_total_time_secs);
    offset += sprintf(buffer + offset, "[benchmark] iterations_per_sec,%s\n", 
                     metrics_iterations_per_sec);
    offset += sprintf(buffer + offset, "[benchmark] iterations,%s\n", 
                     metrics_iterations);
    offset += sprintf(buffer + offset, "[benchmark] memory_location,%s\n", 
                     metrics_memory_location);
    offset += sprintf(buffer + offset, "[benchmark] seedcrc,%s\n", 
                     metrics_seedcrc);
    offset += sprintf(buffer + offset, "[benchmark] crclist,%s\n", 
                     metrics_crclist);
    offset += sprintf(buffer + offset, "[benchmark] crcmatrix,%s\n", 
                     metrics_crcmatrix);
    offset += sprintf(buffer + offset, "[benchmark] crcstate,%s\n", 
                     metrics_crcstate);
    offset += sprintf(buffer + offset, "[benchmark] crcfinal,%s\n", 
                     metrics_crcfinal);
    
    return offset;
}