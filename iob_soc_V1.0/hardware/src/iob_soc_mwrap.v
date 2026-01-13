`timescale 1ns / 1ps
`include "iob_soc_mwrap_conf.vh"

module iob_soc_mwrap #(
   parameter AXI_ID_W = `IOB_SOC_MWRAP_AXI_ID_W,  // Don't change this parameter value!
   parameter AXI_ADDR_W = `IOB_SOC_MWRAP_AXI_ADDR_W,  // Don't change this parameter value!
   parameter AXI_DATA_W = `IOB_SOC_MWRAP_AXI_DATA_W,  // Don't change this parameter value!
   parameter AXI_LEN_W = `IOB_SOC_MWRAP_AXI_LEN_W,  // Don't change this parameter value!
   parameter BOOTROM_MEM_HEXFILE = `IOB_SOC_MWRAP_BOOTROM_MEM_HEXFILE,  // Don't change this parameter value!
   parameter EXT_MEM_HEXFILE = `IOB_SOC_MWRAP_EXT_MEM_HEXFILE,  // Don't change this parameter value!
   parameter MEM_NO_READ_ON_WRITE = `IOB_SOC_MWRAP_MEM_NO_READ_ON_WRITE
) (
   // clk_en_rst_s
   input  clk_i,
   input  cke_i,
   input  arst_i,
   // rs232_m
   input  rs232_rxd_i,
   output rs232_txd_o,
   output rs232_rts_o,
   input  rs232_cts_i
);
   // rom_bus_m
   wire          bootrom_mem_clk;
   wire [10-1:0] bootrom_mem_addr;
   wire          bootrom_mem_en;
   reg  [32-1:0] bootrom_mem_r_data;
   // external_mem_bus_m
   wire          ext_mem_clk;
   reg  [32-1:0] ext_mem_r_data;
   wire          ext_mem_r_en;
   wire [13-1:0] ext_mem_r_addr;
   wire [32-1:0] ext_mem_w_data;
   wire [ 4-1:0] ext_mem_w_strb;
   wire [13-1:0] ext_mem_w_addr;


   // Default description
   iob_soc #(
      .AXI_ID_W           (AXI_ID_W),
      .AXI_ADDR_W         (AXI_ADDR_W),
      .AXI_DATA_W         (AXI_DATA_W),
      .AXI_LEN_W          (AXI_LEN_W),
      .BOOTROM_MEM_HEXFILE(BOOTROM_MEM_HEXFILE),
      .EXT_MEM_HEXFILE    (EXT_MEM_HEXFILE)
   ) iob_core_inst (
      // clk_en_rst_s port
      .clk_i               (clk_i),
      .cke_i               (cke_i),
      .arst_i              (arst_i),
      // rom_bus_m port
      .bootrom_mem_clk_o   (bootrom_mem_clk),
      .bootrom_mem_addr_o  (bootrom_mem_addr),
      .bootrom_mem_en_o    (bootrom_mem_en),
      .bootrom_mem_r_data_i(bootrom_mem_r_data),
      // external_mem_bus_m port
      .ext_mem_clk_o       (ext_mem_clk),
      .ext_mem_r_data_i    (ext_mem_r_data),
      .ext_mem_r_en_o      (ext_mem_r_en),
      .ext_mem_r_addr_o    (ext_mem_r_addr),
      .ext_mem_w_data_o    (ext_mem_w_data),
      .ext_mem_w_strb_o    (ext_mem_w_strb),
      .ext_mem_w_addr_o    (ext_mem_w_addr),
      // rs232_m port
      .rs232_rxd_i         (rs232_rxd_i),
      .rs232_txd_o         (rs232_txd_o),
      .rs232_rts_o         (rs232_rts_o),
      .rs232_cts_i         (rs232_cts_i)
   );

   // Default description
   iob_rom_sp #(
      .DATA_W (32),
      .ADDR_W (10),
      .HEXFILE(BOOTROM_MEM_HEXFILE)
   ) bootrom_mem_mem (
      // rom_sp_s port
      .clk_i   (bootrom_mem_clk),
      .addr_i  (bootrom_mem_addr),
      .en_i    (bootrom_mem_en),
      .r_data_o(bootrom_mem_r_data)
   );

   // Default description
   iob_ram_t2p_be #(
      .DATA_W              (32),
      .ADDR_W              (13),
      .HEXFILE             (EXT_MEM_HEXFILE),
      .MEM_NO_READ_ON_WRITE(MEM_NO_READ_ON_WRITE)
   ) ext_mem_mem (
      // ram_t2p_be_s port
      .clk_i   (ext_mem_clk),
      .r_data_o(ext_mem_r_data),
      .r_en_i  (ext_mem_r_en),
      .r_addr_i(ext_mem_r_addr),
      .w_data_i(ext_mem_w_data),
      .w_strb_i(ext_mem_w_strb),
      .w_addr_i(ext_mem_w_addr)
   );




endmodule
