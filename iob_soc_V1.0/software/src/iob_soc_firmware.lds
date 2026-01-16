/*
 * SPDX-FileCopyrightText: 2025 IObundle
 * SPDX-License-Identifier: MIT
 */

/*
 * IOb-SoC Linker Script for RISC-V RV32I
 * 
 * Memory Configuration:
 *   - RAM: 256KB (mem_addr_w=18)
 *   - Start: 0x00000000
 *   - End:   0x00040000
 * 
 * Memory Layout:
 *   0x00000000: .text (code + read-only data)
 *   ...........: .data (initialized data)
 *   ...........: .bss (uninitialized data)
 *   ...........: heap (16KB, for future malloc support)
 *   ...........: stack (16KB, grows downward)
 *   0x00040000: End of RAM
 * 
 * Usage:
 *   - Works for all benchmarks: hello_world, CoreMark, Embench, etc.
 *   - Generous stack (16KB) supports deep recursion
 *   - Heap available if needed (currently unused)
 */

/* Entry point symbol */
/* ENTRY(_start) */

/* Memory layout */
MEMORY
{
    /* 256KB RAM starting at address 0 */
    RAM (rwx) : ORIGIN = 0x00000000, LENGTH = 256K
}

/* Section placement */
SECTIONS
{
    /* ===================================================================
     * CODE SECTION (.text)
     * Contains executable instructions and read-only data
     * =================================================================== */
    .text :
    {
        /* Startup code must be first */
        *(.init)
        *(.init.*)
        
        /* All executable code */
        *(.text)
        *(.text.*)
        
        /* Read-only data (string literals, const variables) */
        *(.rodata)
        *(.rodata.*)
        
        /* GNU linkonce sections (C++ template instantiations, etc.) */
        *(.gnu.linkonce.t.*)
        *(.gnu.linkonce.r.*)
        
        /* Ensure section is word-aligned */
        . = ALIGN(4);
        
        /* Mark end of code section */
        _etext = .;
        PROVIDE(etext = .);
    } > RAM

    /* ===================================================================
     * INITIALIZED DATA SECTION (.data)
     * Contains variables with initial values
     * =================================================================== */
    .data :
    {
        /* Mark start of data section */
        _sdata = .;
        PROVIDE(sdata = .);
        
        /* All initialized data */
        *(.data)
        *(.data.*)
        
        /* Small data (RISC-V specific, accessed via GP register) */
        *(.sdata)
        *(.sdata.*)
        *(.sdata2)
        *(.sdata2.*)
        
        /* GNU linkonce sections */
        *(.gnu.linkonce.d.*)
        *(.gnu.linkonce.s.*)
        
        /* Ensure section is word-aligned */
        . = ALIGN(4);
        
        /* Mark end of data section */
        _edata = .;
        PROVIDE(edata = .);
    } > RAM

    /* ===================================================================
     * UNINITIALIZED DATA SECTION (.bss)
     * Contains variables without initial values (zeroed at startup)
     * =================================================================== */
    .bss :
    {
        /* Mark start of BSS (needed by startup code for zeroing) */
        _sbss = .;
        PROVIDE(sbss = .);
        _bss_start = .;
        
        /* All uninitialized data */
        *(.bss)
        *(.bss.*)
        
        /* Small BSS */
        *(.sbss)
        *(.sbss.*)
        *(.sbss2)
        *(.sbss2.*)
        
        /* Common symbols (old-style uninitialized globals) */
        *(COMMON)
        
        /* GNU linkonce sections */
        *(.gnu.linkonce.b.*)
        *(.gnu.linkonce.sb.*)
        
        /* Ensure section is word-aligned */
        . = ALIGN(4);
        
        /* Mark end of BSS (needed by startup code) */
        _ebss = .;
        PROVIDE(ebss = .);
        _bss_end = .;
    } > RAM

    /* ===================================================================
     * HEAP SECTION (optional, for malloc/free)
     * Currently unused but available for future use
     * =================================================================== */
    . = ALIGN(16);
    _heap_start = .;
    PROVIDE(__heap_start = _heap_start);
    
    /* Reserve 8KB for heap */
    . = . + 0x2000;  /* 8KB */
    
    _heap_end = .;
    PROVIDE(__heap_end = _heap_end);
    PROVIDE(__heap_size = _heap_end - _heap_start);

    /* ===================================================================
     * STACK SECTION
     * Grows downward from high addresses
     * 32KB supports deep soft-float printf operations
     * =================================================================== */
    . = ALIGN(16);
    _stack_start = .;
    PROVIDE(__stack_start = _stack_start);
    
    /* Reserve 32KB for stack */
    . = . + 0x8000;  /* 32KB */
    
    _stack_end = .;
    
    /* Stack pointer initialization (used by startup assembly) */
    PROVIDE(__stack = _stack_end);
    PROVIDE(_sp = _stack_end);
    PROVIDE(__stack_size = _stack_end - _stack_start);

    /* ===================================================================
     * END MARKERS
     * =================================================================== */
    _end = .;
    PROVIDE(end = .);
    
    /* Verify we haven't exceeded available RAM */
    ASSERT(_end <= 0x00040000, "ERROR: Program exceeds 256KB RAM!")

    /* ===================================================================
     * DEBUG SECTIONS (not loaded into target)
     * These sections contain debugging information for GDB, objdump, etc.
     * =================================================================== */
    
    /* DWARF debug sections */
    .debug          0 : { *(.debug) }
    .debug_abbrev   0 : { *(.debug_abbrev) }
    .debug_aranges  0 : { *(.debug_aranges) }
    .debug_frame    0 : { *(.debug_frame) }
    .debug_info     0 : { *(.debug_info) }
    .debug_line     0 : { *(.debug_line) }
    .debug_loc      0 : { *(.debug_loc) }
    .debug_macinfo  0 : { *(.debug_macinfo) }
    .debug_pubnames 0 : { *(.debug_pubnames) }
    .debug_pubtypes 0 : { *(.debug_pubtypes) }
    .debug_ranges   0 : { *(.debug_ranges) }
    .debug_str      0 : { *(.debug_str) }
    
    /* Other informational sections */
    .comment        0 : { *(.comment) }
    .note           0 : { *(.note) }
    
    /* Discard unwanted sections */
    /DISCARD/ :
    {
        *(.eh_frame)
        *(.eh_frame_hdr)
    }
}

/* ===================================================================
 * MEMORY MAP SUMMARY (typical sizes)
 * ===================================================================
 * 
 * Hello World (~3KB total):
 *   0x00000000: .text       ~2KB
 *   0x00000800: .data/bss   ~1KB
 *   0x00000C00: heap        16KB (unused)
 *   0x00004C00: stack       16KB
 *   0x00008C00: end         (~35KB used, 221KB free)
 * 
 * CoreMark RV32I (~33KB total):
 *   0x00000000: .text       ~27KB
 *   0x00006C00: .data/bss   ~6KB
 *   0x00008400: heap        16KB (unused)
 *   0x0000C400: stack       16KB
 *   0x00010400: end         (~65KB used, 191KB free)
 * 
 * CoreMark RV32IMC (~24KB total):
 *   0x00000000: .text       ~18KB (compressed)
 *   0x00004800: .data/bss   ~6KB
 *   0x00006000: heap        16KB (unused)
 *   0x0000A000: stack       16KB
 *   0x0000E000: end         (~56KB used, 200KB free)
 * 
 * Maximum supported program:
 *   Code + Data: ~224KB (256KB - 16KB heap - 16KB stack)
 * 
 * =================================================================== */