// SPDX-License-Identifier: MIT
#ifndef SUPPORT_H
#define SUPPORT_H

#include "boardsupport.h"
#include "beebsc.h"

// Dummy warm_caches (not used in baremetal)
// Each benchmark will #undef this and define its own
// But we provide a default to avoid errors
static inline void warm_caches_dummy(int temperature) { 
    (void)temperature; 
}

#endif