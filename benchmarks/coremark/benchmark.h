// Benchmark interface for CoreMark

#ifndef BENCHMARK_H
#define BENCHMARK_H

// Entry point function - called by wrapper
extern int coremark_main(void);

// Benchmark metadata
#define BENCHMARK_MAIN    coremark_main
#define BENCHMARK_NAME    "CoreMark"
#define BENCHMARK_VERSION "1.0"

#endif // BENCHMARK_H