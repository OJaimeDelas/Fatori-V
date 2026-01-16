// SPDX-License-Identifier: MIT
#ifndef EMBENCH_DATA_H
#define EMBENCH_DATA_H

#include <stdint.h>

// Embench baseline cycles (ARM Cortex-M4 @ 16MHz)
// Converted from baseline execution times (ms) to actual cycle counts
// Formula: baseline_time_ms * 16000 (16MHz * 1000 cycles/ms)
static const uint64_t baseline_cycles[] = {
    64064000ULL,   // aha-mont64 (4004ms * 16000)
    64160000ULL,   // crc32 (4010ms * 16000)
    62896000ULL,   // cubic (3931ms * 16000)
    64160000ULL,   // edn (4010ms * 16000)
    65920000ULL,   // huffbench (4120ms * 16000)
    63760000ULL,   // matmult-int (3985ms * 16000)
    64032000ULL,   // md5sum (4002ms * 16000)
    63968000ULL,   // minver (3998ms * 16000)
    44928000ULL,   // nbody (2808ms * 16000)
    64416000ULL,   // nettle-aes (4026ms * 16000)
    63952000ULL,   // nettle-sha256 (3997ms * 16000)
    64016000ULL,   // nsichneu (4001ms * 16000)
    64480000ULL,   // picojpeg (4030ms * 16000)
    61344000ULL,   // primecount (3834ms * 16000)
    68048000ULL,   // qrduino (4253ms * 16000)
    63696000ULL,   // sglib-combined (3981ms * 16000)
    64160000ULL,   // slre (4010ms * 16000)
    65280000ULL,   // st (4080ms * 16000)
    64016000ULL,   // statemate (4001ms * 16000)
    63984000ULL,   // ud (3999ms * 16000)
    44464000ULL    // wikisort (2779ms * 16000)
};

static const char* benchmark_names[] = {
    "aha-mont64",
    "crc32",
    "cubic",
    "edn",
    "huffbench",
    "matmult-int",
    "md5sum",
    "minver",
    "nbody",
    "nettle-aes",
    "nettle-sha256",
    "nsichneu",
    "picojpeg",
    "primecount",
    "qrduino",
    "sglib-combined",
    "slre",
    "st",
    "statemate",
    "ud",
    "wikisort"
};

#endif