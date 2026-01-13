`timescale 1ns / 1ps
`include "iob_system_tester_iob_aes_ku040_db_g_conf.vh"

module iob_system_tester_iob_aes_ku040_db_g #(
   parameter AXI_ID_W = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_AXI_ID_W,  // Don't change this parameter value!
   parameter AXI_LEN_W = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_AXI_LEN_W,  // Don't change this parameter value!
   parameter AXI_ADDR_W = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_AXI_ADDR_W,  // Don't change this parameter value!
   parameter AXI_DATA_W = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_AXI_DATA_W,  // Don't change this parameter value!
   parameter BAUD = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_BAUD,  // Don't change this parameter value!
   parameter FREQ = `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_FREQ,  // Don't change this parameter value!
   parameter XILINX =
   `IOB_SYSTEM_TESTER_IOB_AES_KU040_DB_G_XILINX  // Don't change this parameter value!
) (
   // clk_rst_i
   input  c0_sys_clk_clk_p_i,
   input  c0_sys_clk_clk_n_i,
   input  areset_i,
   // rs232_io
   output txd_o,
   input  rxd_i
);
   // clk_en_rst
   wire clk;
   wire cke;
   wire arst;
   // rs232_int
   wire rs232_rts;
   wire high;


   // Default description
   iob_system_tester_mwrap #(
      .AXI_ID_W  (AXI_ID_W),
      .AXI_LEN_W (AXI_LEN_W),
      .AXI_ADDR_W(AXI_ADDR_W),
      .AXI_DATA_W(AXI_DATA_W)
   ) iob_system_tester_memwrapper (
      // clk_en_rst_s port
      .clk_i      (clk),
      .cke_i      (cke),
      .arst_i     (arst),
      // rs232_m port
      .rs232_rxd_i(rxd_i),
      .rs232_txd_o(txd_o),
      .rs232_rts_o(rs232_rts),
      .rs232_cts_i(high)
   );

   // PLL to generate system clock
   iob_xilinx_clock_wizard #(
      .OUTPUT_PER(16.667),
      .INPUT_PER (4.0)
   ) clk_250_to_100_MHz (
      // clk_rst_i port
      .clk_p_i   (c0_sys_clk_clk_p_i),
      .clk_n_i   (c0_sys_clk_clk_n_i),
      .arst_i    (areset_i),
      // clk_rst_o port
      .clk_out1_o(clk),
      .rst_out1_o(arst)
   );




   // General connections
   assign high = 1'b1;
   assign cke  = 1'b1;




endmodule
