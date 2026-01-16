#ifndef BENCH_CONFIG_H
#define BENCH_CONFIG_H

// Execution control
// Number of iterations to run (-1 = infinite loop)
#define FATORI_ITERATIONS  100

// Target enables (1=enabled, 0=disabled)
#define FATORI_TARGET_ALU               1
#define FATORI_TARGET_MULTIPLIER        1
#define FATORI_TARGET_DECODER           1
#define FATORI_TARGET_CONTROLLER        1
#define FATORI_TARGET_LSU               1
#define FATORI_TARGET_BRANCH_PREDICT    1
#define FATORI_TARGET_COMPRESSED        1 

#endif