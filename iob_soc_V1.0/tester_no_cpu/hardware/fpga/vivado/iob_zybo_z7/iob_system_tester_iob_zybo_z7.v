`timescale 1ns / 1ps
`include "iob_system_tester_iob_zybo_z7_conf.vh"

module iob_system_tester_iob_zybo_z7 #(
   parameter AXI_ID_W = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_AXI_ID_W,  // Don't change this parameter value!
   parameter AXI_LEN_W = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_AXI_LEN_W,  // Don't change this parameter value!
   parameter AXI_ADDR_W = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_AXI_ADDR_W,  // Don't change this parameter value!
   parameter AXI_DATA_W = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_AXI_DATA_W,  // Don't change this parameter value!
   parameter BAUD = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_BAUD,  // Don't change this parameter value!
   parameter FREQ = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_FREQ,  // Don't change this parameter value!
   parameter XILINX = `IOB_SYSTEM_TESTER_IOB_ZYBO_Z7_XILINX  // Don't change this parameter value!
) (
   // clk_rst_i
   input  clk_i,
   input  arst_i,
   // rs232_io
   output txd_o,
   input  rxd_i
);
   // ps_clk_arstn
   wire                      ps_clk;
   wire                      ps_arstn;
   // ps_clk_rst
   wire                      clk;
   wire                      arst;
   // clk_en_rst
   wire                      cke;
   // rs232_int
   wire                      rs232_rxd;
   wire                      rs232_txd;
   wire                      rs232_rts;
   wire                      rs232_cts;
   // intercon_m_clk_rst
   wire                      intercon_m_clk;
   wire                      intercon_m_arst;
   // ps_axi
   wire [AXI_ADDR_W - 2-1:0] mem_axi_araddr;
   wire [             3-1:0] mem_axi_arprot;
   wire                      mem_axi_arvalid;
   wire                      mem_axi_arready;
   wire [    AXI_DATA_W-1:0] mem_axi_rdata;
   wire [             2-1:0] mem_axi_rresp;
   wire                      mem_axi_rvalid;
   wire                      mem_axi_rready;
   wire [      AXI_ID_W-1:0] mem_axi_arid;
   wire [     AXI_LEN_W-1:0] mem_axi_arlen;
   wire [             3-1:0] mem_axi_arsize;
   wire [             2-1:0] mem_axi_arburst;
   wire                      mem_axi_arlock;
   wire [             4-1:0] mem_axi_arcache;
   wire [             4-1:0] mem_axi_arqos;
   wire [      AXI_ID_W-1:0] mem_axi_rid;
   wire                      mem_axi_rlast;
   wire [AXI_ADDR_W - 2-1:0] mem_axi_awaddr;
   wire [             3-1:0] mem_axi_awprot;
   wire                      mem_axi_awvalid;
   wire                      mem_axi_awready;
   wire [    AXI_DATA_W-1:0] mem_axi_wdata;
   wire [  AXI_DATA_W/8-1:0] mem_axi_wstrb;
   wire                      mem_axi_wvalid;
   wire                      mem_axi_wready;
   wire [             2-1:0] mem_axi_bresp;
   wire                      mem_axi_bvalid;
   wire                      mem_axi_bready;
   wire [      AXI_ID_W-1:0] mem_axi_awid;
   wire [     AXI_LEN_W-1:0] mem_axi_awlen;
   wire [             3-1:0] mem_axi_awsize;
   wire [             2-1:0] mem_axi_awburst;
   wire                      mem_axi_awlock;
   wire [             4-1:0] mem_axi_awcache;
   wire [             4-1:0] mem_axi_awqos;
   wire                      mem_axi_wlast;
   wire [      AXI_ID_W-1:0] mem_axi_bid;


   // Default description
   iob_system_tester #(
      .AXI_ID_W  (AXI_ID_W),
      .AXI_LEN_W (AXI_LEN_W),
      .AXI_ADDR_W(AXI_ADDR_W),
      .AXI_DATA_W(AXI_DATA_W)
   ) iob_system_tester_no_cpu (
      // clk_en_rst_s port
      .clk_i       (clk),
      .cke_i       (cke),
      .arst_i      (arst),
      // rs232_m port
      .rs232_rxd_i (rs232_rxd),
      .rs232_txd_o (rs232_txd),
      .rs232_rts_o (rs232_rts),
      .rs232_cts_i (rs232_cts),
      // iob_s port
      .iob_valid_i (pbus_iob_valid_i),
      .iob_addr_i  (pbus_iob_addr_i),
      .iob_wdata_i (pbus_iob_wdata_i),
      .iob_wstrb_i (pbus_iob_wstrb_i),
      .iob_rvalid_o(pbus_iob_rvalid_o),
      .iob_rdata_o (pbus_iob_rdata_o),
      .iob_ready_o (pbus_iob_ready_o)
   );




   // General connections
   assign cke     = 1'b1;
   assign arst    = ~ps_arstn;
   assign ps_arst = ~ps_arstn;




endmodule
