// SPDX-License-Identifier: MIT
#ifndef EMBENCH_SCORE_H
#define EMBENCH_SCORE_H

#include <stdint.h>

// Compute geometric mean score
uint32_t compute_embench_score(const uint64_t* baseline,
                                const uint64_t* measured,
                                uint8_t count);

#endif