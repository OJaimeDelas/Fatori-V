#ifndef H_IOB_SOC_CONF_H
#define H_IOB_SOC_CONF_H

#define IOB_SOC_ADDR_W 32
#define IOB_SOC_DATA_W 32
#define IOB_SOC_INIT_MEM 1
#define IOB_SOC_USE_INTMEM 1
#define IOB_SOC_MEM_ADDR_W 18
#define IOB_SOC_FW_BASEADDR 0
#define IOB_SOC_FW_ADDR_W 18
#define IOB_SOC_RST_POL 1
#define IOB_SOC_BOOTROM_ADDR_W 12
#define IOB_SOC_AXI_ID_W 0
#define IOB_SOC_AXI_ADDR_W 18
#define IOB_SOC_AXI_DATA_W 32
#define IOB_SOC_AXI_LEN_W 4
#define IOB_SOC_BOOTROM_MEM_HEXFILE "iob_soc_bootrom"
#define IOB_SOC_EXT_MEM_HEXFILE "iob_soc_firmware"
#define IOB_SOC_BOARD iob_aes_ku040_db_g
#define IOB_SOC_VERSION 0x0100

#endif // H_IOB_SOC_CONF_H
