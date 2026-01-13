`timescale 1ns / 1ps
`include "iob_system_tester_iob_cyclonev_gt_dk_conf.vh"

module iob_system_tester_iob_cyclonev_gt_dk #(
   parameter AXI_ID_W = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_AXI_ID_W,  // Don't change this parameter value!
   parameter AXI_LEN_W = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_AXI_LEN_W,  // Don't change this parameter value!
   parameter AXI_ADDR_W = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_AXI_ADDR_W,  // Don't change this parameter value!
   parameter AXI_DATA_W = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_AXI_DATA_W,  // Don't change this parameter value!
   parameter BAUD = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_BAUD,  // Don't change this parameter value!
   parameter FREQ = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_FREQ,  // Don't change this parameter value!
   parameter MEM_NO_READ_ON_WRITE = `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_MEM_NO_READ_ON_WRITE,  // Don't change this parameter value!
   parameter INTEL =
   `IOB_SYSTEM_TESTER_IOB_CYCLONEV_GT_DK_INTEL  // Don't change this parameter value!
) (
   // clk_rst_i
   input  clk_i,
   input  resetn_i,
   // rs232_io
   output txd_o,
   input  rxd_i
);
   // clk_en_rst
   wire cke;
   wire arst;
   // rs232_int
   wire rs232_rts;
   wire high;
   // reset_sync_clk_rst
   wire resetn_inv;


   // Default description
   iob_system_tester #(
      .AXI_ID_W            (AXI_ID_W),
      .AXI_LEN_W           (AXI_LEN_W),
      .AXI_ADDR_W          (AXI_ADDR_W),
      .AXI_DATA_W          (AXI_DATA_W),
      .MEM_NO_READ_ON_WRITE(MEM_NO_READ_ON_WRITE)
   ) iob_system_tester_no_cpu (
      // clk_en_rst_s port
      .clk_i       (clk_i),
      .cke_i       (cke),
      .arst_i      (arst),
      // rs232_m port
      .rs232_rxd_i (rxd_i),
      .rs232_txd_o (txd_o),
      .rs232_rts_o (rs232_rts),
      .rs232_cts_i (high),
      // iob_s port
      .iob_valid_i (pbus_iob_valid_i),
      .iob_addr_i  (pbus_iob_addr_i),
      .iob_wdata_i (pbus_iob_wdata_i),
      .iob_wstrb_i (pbus_iob_wstrb_i),
      .iob_rvalid_o(pbus_iob_rvalid_o),
      .iob_rdata_o (pbus_iob_rdata_o),
      .iob_ready_o (pbus_iob_ready_o)
   );

   // Reset synchronizer
   iob_reset_sync rst_sync (
      // clk_rst_s port
      .clk_i (clk_i),
      .arst_i(resetn_inv),
      // arst_o port
      .arst_o(arst)
   );




   // General connections
   assign high       = 1'b1;
   assign cke        = 1'b1;


   assign resetn_inv = ~resetn_i;




endmodule
