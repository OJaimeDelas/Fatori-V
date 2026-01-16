// SPDX-License-Identifier: MIT
// Forward declarations for all Embench benchmarks
#ifndef EMBENCH_BENCHMARKS_H
#define EMBENCH_BENCHMARKS_H

#include "bench_config.h"

#if EMBENCH_AHA_MONT64
void initialise_benchmark_aha_mont64(void);
int benchmark_aha_mont64(void);
int verify_benchmark_aha_mont64(int);
#endif

#if EMBENCH_CRC32
void initialise_benchmark_crc32(void);
int benchmark_crc32(void);
int verify_benchmark_crc32(int);
#endif

#if EMBENCH_CUBIC
void initialise_benchmark_cubic(void);
int benchmark_cubic(void);
int verify_benchmark_cubic(int);
#endif

#if EMBENCH_EDN
void initialise_benchmark_edn(void);
int benchmark_edn(void);
int verify_benchmark_edn(int);
#endif

#if EMBENCH_HUFFBENCH
void initialise_benchmark_huffbench(void);
int benchmark_huffbench(void);
int verify_benchmark_huffbench(int);
#endif

#if EMBENCH_MATMULT_INT
void initialise_benchmark_matmult_int(void);
int benchmark_matmult_int(void);
int verify_benchmark_matmult_int(int);
#endif

#if EMBENCH_MD5SUM
void initialise_benchmark_md5sum(void);
int benchmark_md5sum(void);
int verify_benchmark_md5sum(int);
#endif

#if EMBENCH_MINVER
void initialise_benchmark_minver(void);
int benchmark_minver(void);
int verify_benchmark_minver(int);
#endif

#if EMBENCH_NBODY
void initialise_benchmark_nbody(void);
int benchmark_nbody(void);
int verify_benchmark_nbody(int);
#endif

#if EMBENCH_NETTLE_AES
void initialise_benchmark_nettle_aes(void);
int benchmark_nettle_aes(void);
int verify_benchmark_nettle_aes(int);
#endif

#if EMBENCH_NETTLE_SHA256
void initialise_benchmark_nettle_sha256(void);
int benchmark_nettle_sha256(void);
int verify_benchmark_nettle_sha256(int);
#endif

#if EMBENCH_NSICHNEU
void initialise_benchmark_nsichneu(void);
int benchmark_nsichneu(void);
int verify_benchmark_nsichneu(int);
#endif

#if EMBENCH_PICOJPEG
void initialise_benchmark_picojpeg(void);
int benchmark_picojpeg(void);
int verify_benchmark_picojpeg(int);
#endif

#if EMBENCH_PRIMECOUNT
void initialise_benchmark_primecount(void);
int benchmark_primecount(void);
int verify_benchmark_primecount(int);
#endif

#if EMBENCH_QRDUINO
void initialise_benchmark_qrduino(void);
int benchmark_qrduino(void);
int verify_benchmark_qrduino(int);
#endif

#if EMBENCH_SGLIB_COMBINED
void initialise_benchmark_sglib_combined(void);
int benchmark_sglib_combined(void);
int verify_benchmark_sglib_combined(int);
#endif

#if EMBENCH_SLRE
void initialise_benchmark_slre(void);
int benchmark_slre(void);
int verify_benchmark_slre(int);
#endif

#if EMBENCH_ST
void initialise_benchmark_st(void);
int benchmark_st(void);
int verify_benchmark_st(int);
#endif

#if EMBENCH_STATEMATE
void initialise_benchmark_statemate(void);
int benchmark_statemate(void);
int verify_benchmark_statemate(int);
#endif

#if EMBENCH_UD
void initialise_benchmark_ud(void);
int benchmark_ud(void);
int verify_benchmark_ud(int);
#endif

#if EMBENCH_WIKISORT
void initialise_benchmark_wikisort(void);
int benchmark_wikisort(void);
int verify_benchmark_wikisort(int);
#endif

#endif