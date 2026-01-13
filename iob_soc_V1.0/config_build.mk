NAME=iob_soc
CSR_IF ?=iob
BUILD_DIR_NAME=iob_soc_V1.0
IS_FPGA=1

CONFIG_BUILD_DIR = $(dir $(lastword $(MAKEFILE_LIST)))
ifneq ($(wildcard $(CONFIG_BUILD_DIR)/custom_config_build.mk),)
include $(CONFIG_BUILD_DIR)/custom_config_build.mk
endif
