#ifndef FATORI_STRESS_H
#define FATORI_STRESS_H

#include <stdint.h>

/******************************************************************************
 * FATORI Stress Function Declarations
 * 
 * Each function stresses a specific hardware module in the Ibex core.
 * Functions compute a result based solely on the iteration number, then
 * XOR it with the checksum to maintain reversibility.
 * 
 * Parameters:
 *   @param checksum - Current checksum state (used only for final XOR)
 *   @param iteration - Iteration number (determines all computation)
 *   @return New checksum value (checksum XOR result)
 ******************************************************************************/

uint32_t alu_stress(uint32_t checksum, uint32_t iteration);
uint32_t multiplier_stress(uint32_t checksum, uint32_t iteration);
uint32_t decoder_stress(uint32_t checksum, uint32_t iteration);
uint32_t controller_stress(uint32_t checksum, uint32_t iteration);
uint32_t lsu_stress(uint32_t checksum, uint32_t iteration);
uint32_t branch_predict_stress(uint32_t checksum, uint32_t iteration);
uint32_t compressed_stress(uint32_t checksum, uint32_t iteration);

#endif