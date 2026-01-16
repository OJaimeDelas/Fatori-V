// SPDX-License-Identifier: MIT
#include "bench_config.h"
#include "support.h"

// For each benchmark, we need to:
// 1. Rename the 5 main functions
// 2. Rename warm_caches and benchmark_body (helper functions)
// 3. Make static globals file-scoped (they'll be isolated)

//==============================================================================
// AHA-MONT64
//==============================================================================
#if EMBENCH_AHA_MONT64
#define benchmark benchmark_aha_mont64
#define initialise_benchmark initialise_benchmark_aha_mont64
#define verify_benchmark verify_benchmark_aha_mont64
#define warm_caches warm_caches_aha_mont64
#define benchmark_body benchmark_body_aha_mont64
#include "src/mont64.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// CRC32
//==============================================================================
#if EMBENCH_CRC32
#define benchmark benchmark_crc32
#define initialise_benchmark initialise_benchmark_crc32
#define verify_benchmark verify_benchmark_crc32
#define warm_caches warm_caches_crc32
#define benchmark_body benchmark_body_crc32
#include "src/crc_32.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// CUBIC (includes TWO source files!)
//==============================================================================
#if EMBENCH_CUBIC
#define benchmark benchmark_cubic
#define initialise_benchmark initialise_benchmark_cubic
#define verify_benchmark verify_benchmark_cubic
#define warm_caches warm_caches_cubic
#define benchmark_body benchmark_body_cubic
#include "src/libcubic.c"
#include "src/basicmath_small.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// EDN
//==============================================================================
#if EMBENCH_EDN
#define benchmark benchmark_edn
#define initialise_benchmark initialise_benchmark_edn
#define verify_benchmark verify_benchmark_edn
#define warm_caches warm_caches_edn
#define benchmark_body benchmark_body_edn
// Rename conflicting globals
#define a a_edn
#define b b_edn
#define c c_edn
#define d d_edn
#include "src/libedn.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef a
#undef b
#undef c
#undef d
#endif

//==============================================================================
// HUFFBENCH
//==============================================================================
#if EMBENCH_HUFFBENCH
#define benchmark benchmark_huffbench
#define initialise_benchmark initialise_benchmark_huffbench
#define verify_benchmark verify_benchmark_huffbench
#define warm_caches warm_caches_huffbench
#define benchmark_body benchmark_body_huffbench
#define heap heap_huffbench
#include "src/libhuffbench.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef heap
#endif

//==============================================================================
// MATMULT-INT
//==============================================================================
#if EMBENCH_MATMULT_INT
#define benchmark benchmark_matmult_int
#define initialise_benchmark initialise_benchmark_matmult_int
#define verify_benchmark verify_benchmark_matmult_int
#define warm_caches warm_caches_matmult_int
#define benchmark_body benchmark_body_matmult_int
#define Initialize Initialize_matmult_int
#define Test Test_matmult_int
#define InitSeed InitSeed_matmult_int
#define RandomInteger RandomInteger_matmult_int
#define ArrayA ArrayA_matmult_int
#define ArrayB ArrayB_matmult_int
#include "src/matmult-int.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef Initialize
#undef Test
#undef InitSeed
#undef RandomInteger
#undef ArrayA
#undef ArrayB
#endif

//==============================================================================
// MD5SUM
//==============================================================================
#if EMBENCH_MD5SUM
#define benchmark benchmark_md5sum
#define initialise_benchmark initialise_benchmark_md5sum
#define verify_benchmark verify_benchmark_md5sum
#define warm_caches warm_caches_md5sum
#define benchmark_body benchmark_body_md5sum
#define heap heap_md5sum
#include "src/md5.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef heap
#endif

//==============================================================================
// MINVER
//==============================================================================
#if EMBENCH_MINVER
#define benchmark benchmark_minver
#define initialise_benchmark initialise_benchmark_minver
#define verify_benchmark verify_benchmark_minver
#define warm_caches warm_caches_minver
#define benchmark_body benchmark_body_minver
#define a a_minver
#define b b_minver
#define c c_minver
#define d d_minver
#include "src/libminver.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef a
#undef b
#undef c
#undef d
#endif

//==============================================================================
// NBODY
//==============================================================================
#if EMBENCH_NBODY
#define benchmark benchmark_nbody
#define initialise_benchmark initialise_benchmark_nbody
#define verify_benchmark verify_benchmark_nbody
#define warm_caches warm_caches_nbody
#define benchmark_body benchmark_body_nbody
#include "src/nbody.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// NETTLE-AES
//==============================================================================
#if EMBENCH_NETTLE_AES
#define benchmark benchmark_nettle_aes
#define initialise_benchmark initialise_benchmark_nettle_aes
#define verify_benchmark verify_benchmark_nettle_aes
#define warm_caches warm_caches_nettle_aes
#define benchmark_body benchmark_body_nettle_aes
#include "src/nettle-aes.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// NETTLE-SHA256
//==============================================================================
#if EMBENCH_NETTLE_SHA256
#define benchmark benchmark_nettle_sha256
#define initialise_benchmark initialise_benchmark_nettle_sha256
#define verify_benchmark verify_benchmark_nettle_sha256
#define warm_caches warm_caches_nettle_sha256
#define benchmark_body benchmark_body_nettle_sha256
#include "src/nettle-sha256.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// NSICHNEU
//==============================================================================
#if EMBENCH_NSICHNEU
#define benchmark benchmark_nsichneu
#define initialise_benchmark initialise_benchmark_nsichneu
#define verify_benchmark verify_benchmark_nsichneu
#define warm_caches warm_caches_nsichneu
#define benchmark_body benchmark_body_nsichneu
#include "src/libnsichneu.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// PICOJPEG
//==============================================================================
#if EMBENCH_PICOJPEG
#define benchmark benchmark_picojpeg
#define initialise_benchmark initialise_benchmark_picojpeg
#define verify_benchmark verify_benchmark_picojpeg
#define warm_caches warm_caches_picojpeg
#define benchmark_body benchmark_body_picojpeg
#define init init_picojpeg
#include "src/libpicojpeg.c"
#include "src/picojpeg_test.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef init
#endif

//==============================================================================
// PRIMECOUNT
//==============================================================================
#if EMBENCH_PRIMECOUNT
#define benchmark benchmark_primecount
#define initialise_benchmark initialise_benchmark_primecount
#define verify_benchmark verify_benchmark_primecount
#define warm_caches warm_caches_primecount
#define benchmark_body benchmark_body_primecount
#include "src/primecount.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// QRDUINO
//==============================================================================
#if EMBENCH_QRDUINO
#define benchmark benchmark_qrduino
#define initialise_benchmark initialise_benchmark_qrduino
#define verify_benchmark verify_benchmark_qrduino
#define warm_caches warm_caches_qrduino
#define benchmark_body benchmark_body_qrduino
#define heap heap_qrduino
#include "src/qrtest.c"
#include "src/qrencode.c"
#include "src/qrframe.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef heap
#endif

//==============================================================================
// SGLIB-COMBINED
//==============================================================================
#if EMBENCH_SGLIB_COMBINED
#define benchmark benchmark_sglib_combined
#define initialise_benchmark initialise_benchmark_sglib_combined
#define verify_benchmark verify_benchmark_sglib_combined
#define warm_caches warm_caches_sglib_combined
#define benchmark_body benchmark_body_sglib_combined
#define heap heap_sglib_combined
#include "src/combined.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef heap
#endif

//==============================================================================
// SLRE
//==============================================================================
#if EMBENCH_SLRE
#define benchmark benchmark_slre
#define initialise_benchmark initialise_benchmark_slre
#define verify_benchmark verify_benchmark_slre
#define warm_caches warm_caches_slre
#define benchmark_body benchmark_body_slre
#include "src/libslre.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#endif

//==============================================================================
// ST
//==============================================================================
#if EMBENCH_ST
#define benchmark benchmark_st
#define initialise_benchmark initialise_benchmark_st
#define verify_benchmark verify_benchmark_st
#define warm_caches warm_caches_st
#define benchmark_body benchmark_body_st
#define Initialize Initialize_st
#define InitSeed InitSeed_st
#define RandomInteger RandomInteger_st
#define ArrayA ArrayA_st
#define ArrayB ArrayB_st
#include "src/libst.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef Initialize
#undef InitSeed
#undef RandomInteger
#undef ArrayA
#undef ArrayB
#endif

//==============================================================================
// STATEMATE
//==============================================================================
#if EMBENCH_STATEMATE
#define benchmark benchmark_statemate
#define initialise_benchmark initialise_benchmark_statemate
#define verify_benchmark verify_benchmark_statemate
#define warm_caches warm_caches_statemate
#define benchmark_body benchmark_body_statemate
#define time time_statemate
#define init init_statemate
#include "src/libstatemate.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef time
#undef init
#endif

//==============================================================================
// UD
//==============================================================================
#if EMBENCH_UD
#define benchmark benchmark_ud
#define initialise_benchmark initialise_benchmark_ud
#define verify_benchmark verify_benchmark_ud
#define warm_caches warm_caches_ud
#define benchmark_body benchmark_body_ud
#define a a_ud
#define b b_ud
#include "src/libud.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef a
#undef b
#endif

//==============================================================================
// WIKISORT
//==============================================================================
#if EMBENCH_WIKISORT
#define benchmark benchmark_wikisort
#define initialise_benchmark initialise_benchmark_wikisort
#define verify_benchmark verify_benchmark_wikisort
#define warm_caches warm_caches_wikisort
#define benchmark_body benchmark_body_wikisort
#define Test Test_wikisort
#include "src/libwikisort.c"
#undef benchmark
#undef initialise_benchmark
#undef verify_benchmark
#undef warm_caches
#undef benchmark_body
#undef Test
#endif