# SPDX-FileCopyrightText: 2024 IObundle
#
# SPDX-License-Identifier: MIT

#########################################
#            Embedded targets           #
#########################################
ROOT_DIR ?=..

include $(ROOT_DIR)/software/auto_sw_build.mk

# Local embedded makefile settings for custom bootloader and firmware targets.

#Function to obtain parameter named $(1) in verilog header file located in $(2)
#Usage: $(call GET_MACRO,<param_name>,<vh_path>)
GET_MACRO = $(shell grep "define $(1)" $(2) | rev | cut -d" " -f1 | rev)

#Function to obtain parameter named $(1) from iob_soc_conf.vh
GET_IOB_SOC_CONF_MACRO = $(call GET_MACRO,IOB_SOC_$(1),../src/iob_soc_conf.vh)

iob_soc_bootrom.hex: ../../software/iob_soc_preboot.bin ../../software/iob_soc_boot.bin
	../../scripts/makehex.py $^ 00000080 $(call GET_IOB_SOC_CONF_MACRO,BOOTROM_ADDR_W) $@

iob_soc_firmware.hex: iob_soc_firmware.bin
	../../scripts/makehex.py $< $(call GET_IOB_SOC_CONF_MACRO,MEM_ADDR_W) $@
	../../scripts/makehex.py --split $< $(call GET_IOB_SOC_CONF_MACRO,MEM_ADDR_W) $@

iob_soc_firmware.bin: ../../software/iob_soc_firmware.bin
	cp $< $@

../../software/%.bin:
	make -C ../../ fw-build

UTARGETS+=build_iob_soc_software

TEMPLATE_LDS=src/$@.lds

IOB_SOC_INCLUDES=-Isrc

IOB_SOC_LFLAGS=-Wl,-L,src,-Bstatic,-T,$(TEMPLATE_LDS),--strip-debug


# Assembly startup 
IOB_SOC_FW_SRC=src/iob_soc_firmware.S

# Universal wrapper
IOB_SOC_FW_SRC+=src/iob_soc_firmware.c

# Infrastructure 
IOB_SOC_FW_SRC+=src/iob_printf.c


#========================================
# Benchmark Configuration
#========================================
ifdef BENCHMARK_DIR
    # External benchmark mode
    BENCHMARK_SRC_DIR = $(BENCHMARK_DIR)
    $(info Building with external benchmark: $(BENCHMARK_DIR))
else
    # Default mode - use hello_world
    BENCHMARK_SRC_DIR = src/hello_world
    $(info Building with default benchmark: Hello World)
endif

#========================================
# BENCHMARK SOURCES 
#========================================
# Include benchmark directory in search path (for benchmark.h, port headers)
IOB_SOC_INCLUDES += -I$(BENCHMARK_SRC_DIR)

# Source .c files from benchmark top level (manual files)
IOB_SOC_FW_SRC += $(wildcard $(BENCHMARK_SRC_DIR)/*.c)

# If benchmark has a code/ subdirectory, include it and source from it
ifneq ($(wildcard $(BENCHMARK_SRC_DIR)/code/.),)
    BENCHMARK_CODE_DIR = $(BENCHMARK_SRC_DIR)/code
    IOB_SOC_INCLUDES += -I$(BENCHMARK_CODE_DIR)
    IOB_SOC_FW_SRC += $(wildcard $(BENCHMARK_CODE_DIR)/*.c)
    $(info   Including prepared code from: $(BENCHMARK_CODE_DIR))
endif


DRIVERS=$(addprefix src/,$(addsuffix .c,$(PERIPHERALS)))
# Only add driver files if they exist
IOB_SOC_FW_SRC+=$(foreach file,$(DRIVERS),$(wildcard $(file)*))
IOB_SOC_FW_SRC+=$(addprefix src/,$(addsuffix _csrs_emb.c,$(PERIPHERALS)))


IOB_SOC_BOOT_SRC+=src/iob_soc_boot.S
IOB_SOC_BOOT_SRC+=src/iob_soc_boot.c
IOB_SOC_BOOT_SRC+=src/iob_uart.c
IOB_SOC_BOOT_SRC+=src/iob_uart_csrs_emb.c


IOB_SOC_PREBOOT_SRC=src/iob_soc_preboot.S

build_iob_soc_software: iob_soc_firmware iob_soc_boot iob_soc_preboot

ifneq ($(USE_FPGA),)
WRAPPER_CONFS_PREFIX=iob_soc_$(BOARD)
else
WRAPPER_CONFS_PREFIX=iob_soc_sim
endif

iob_bsp:
	sed 's/$(WRAPPER_CONFS_PREFIX)/IOB_BSP/Ig' src/$(WRAPPER_CONFS_PREFIX)_conf.h > src/iob_bsp.h

iob_soc_firmware: iob_bsp
	make $@.elf INCLUDES="$(IOB_SOC_INCLUDES)" LFLAGS="$(IOB_SOC_LFLAGS) -Wl,-Map,$@.map" SRC="$(IOB_SOC_FW_SRC)" TEMPLATE_LDS="$(TEMPLATE_LDS)"

iob_soc_boot: iob_bsp
	make $@.elf INCLUDES="$(IOB_SOC_INCLUDES)" LFLAGS="$(IOB_SOC_LFLAGS) -Wl,-Map,$@.map" SRC="$(IOB_SOC_BOOT_SRC)" TEMPLATE_LDS="$(TEMPLATE_LDS)"

iob_soc_preboot:
	make $@.elf INCLUDES="$(IOB_SOC_INCLUDES)" LFLAGS="$(IOB_SOC_LFLAGS) -Wl,-Map,$@.map" SRC="$(IOB_SOC_PREBOOT_SRC)" TEMPLATE_LDS="$(TEMPLATE_LDS)"

.PHONY: build_iob_soc_software iob_bsp iob_soc_firmware iob_soc_boot iob_soc_preboot

#########################################
#         PC emulation targets          #
#########################################
# Local pc-emul makefile settings for custom pc emulation targets.
EMUL_HDR+=iob_bsp

# SOURCES
EMUL_SRC+=src/iob_soc_firmware.c
EMUL_SRC+=src/iob_printf.c

# PERIPHERAL SOURCES
EMUL_SRC+=$(addprefix src/,$(addsuffix .c,$(PERIPHERALS)))
EMUL_SRC+=$(addprefix src/,$(addsuffix _csrs_pc_emul.c,$(PERIPHERALS)))