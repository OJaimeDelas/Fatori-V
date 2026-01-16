// Benchmark interface for Hello World

#ifndef BENCHMARK_H
#define BENCHMARK_H

// Entry point function - called by wrapper
extern int iob_hello_world_main(void);

// Benchmark metadata
#define BENCHMARK_MAIN    iob_hello_world_main
#define BENCHMARK_NAME    "Hello World (Default)"
#define BENCHMARK_VERSION "1.0"

#endif // BENCHMARK_H