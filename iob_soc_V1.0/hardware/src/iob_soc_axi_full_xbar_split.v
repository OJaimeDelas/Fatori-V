`timescale 1ns / 1ps
`include "iob_soc_axi_full_xbar_split_conf.vh"

module iob_soc_axi_full_xbar_split #(
   parameter ID_W  = `IOB_SOC_AXI_FULL_XBAR_SPLIT_ID_W,
   parameter LEN_W = `IOB_SOC_AXI_FULL_XBAR_SPLIT_LEN_W
) (
   // clk_en_rst_s
   input              clk_i,
   input              cke_i,
   input              arst_i,
   // reset_i
   input              rst_i,
   // s_s
   input  [   30-1:0] s_axi_araddr_i,
   input  [    3-1:0] s_axi_arprot_i,
   input              s_axi_arvalid_i,
   output             s_axi_arready_o,
   output [   32-1:0] s_axi_rdata_o,
   output [    2-1:0] s_axi_rresp_o,
   output             s_axi_rvalid_o,
   input              s_axi_rready_i,
   input  [ ID_W-1:0] s_axi_arid_i,
   input  [LEN_W-1:0] s_axi_arlen_i,
   input  [    3-1:0] s_axi_arsize_i,
   input  [    2-1:0] s_axi_arburst_i,
   input              s_axi_arlock_i,
   input  [    4-1:0] s_axi_arcache_i,
   input  [    4-1:0] s_axi_arqos_i,
   output [ ID_W-1:0] s_axi_rid_o,
   output             s_axi_rlast_o,
   input  [   30-1:0] s_axi_awaddr_i,
   input  [    3-1:0] s_axi_awprot_i,
   input              s_axi_awvalid_i,
   output             s_axi_awready_o,
   input  [   32-1:0] s_axi_wdata_i,
   input  [    4-1:0] s_axi_wstrb_i,
   input              s_axi_wvalid_i,
   output             s_axi_wready_o,
   output [    2-1:0] s_axi_bresp_o,
   output             s_axi_bvalid_o,
   input              s_axi_bready_i,
   input  [ ID_W-1:0] s_axi_awid_i,
   input  [LEN_W-1:0] s_axi_awlen_i,
   input  [    3-1:0] s_axi_awsize_i,
   input  [    2-1:0] s_axi_awburst_i,
   input              s_axi_awlock_i,
   input  [    4-1:0] s_axi_awcache_i,
   input  [    4-1:0] s_axi_awqos_i,
   input              s_axi_wlast_i,
   output [ ID_W-1:0] s_axi_bid_o,
   // m_0_m
   output [   28-1:0] m0_axi_araddr_o,
   output [    3-1:0] m0_axi_arprot_o,
   output             m0_axi_arvalid_o,
   input              m0_axi_arready_i,
   input  [   32-1:0] m0_axi_rdata_i,
   input  [    2-1:0] m0_axi_rresp_i,
   input              m0_axi_rvalid_i,
   output             m0_axi_rready_o,
   output [ ID_W-1:0] m0_axi_arid_o,
   output [LEN_W-1:0] m0_axi_arlen_o,
   output [    3-1:0] m0_axi_arsize_o,
   output [    2-1:0] m0_axi_arburst_o,
   output             m0_axi_arlock_o,
   output [    4-1:0] m0_axi_arcache_o,
   output [    4-1:0] m0_axi_arqos_o,
   input  [ ID_W-1:0] m0_axi_rid_i,
   input              m0_axi_rlast_i,
   output [   28-1:0] m0_axi_awaddr_o,
   output [    3-1:0] m0_axi_awprot_o,
   output             m0_axi_awvalid_o,
   input              m0_axi_awready_i,
   output [   32-1:0] m0_axi_wdata_o,
   output [    4-1:0] m0_axi_wstrb_o,
   output             m0_axi_wvalid_o,
   input              m0_axi_wready_i,
   input  [    2-1:0] m0_axi_bresp_i,
   input              m0_axi_bvalid_i,
   output             m0_axi_bready_o,
   output [ ID_W-1:0] m0_axi_awid_o,
   output [LEN_W-1:0] m0_axi_awlen_o,
   output [    3-1:0] m0_axi_awsize_o,
   output [    2-1:0] m0_axi_awburst_o,
   output             m0_axi_awlock_o,
   output [    4-1:0] m0_axi_awcache_o,
   output [    4-1:0] m0_axi_awqos_o,
   output             m0_axi_wlast_o,
   input  [ ID_W-1:0] m0_axi_bid_i,
   // m_1_m
   output [   28-1:0] m1_axi_araddr_o,
   output [    3-1:0] m1_axi_arprot_o,
   output             m1_axi_arvalid_o,
   input              m1_axi_arready_i,
   input  [   32-1:0] m1_axi_rdata_i,
   input  [    2-1:0] m1_axi_rresp_i,
   input              m1_axi_rvalid_i,
   output             m1_axi_rready_o,
   output [ ID_W-1:0] m1_axi_arid_o,
   output [LEN_W-1:0] m1_axi_arlen_o,
   output [    3-1:0] m1_axi_arsize_o,
   output [    2-1:0] m1_axi_arburst_o,
   output             m1_axi_arlock_o,
   output [    4-1:0] m1_axi_arcache_o,
   output [    4-1:0] m1_axi_arqos_o,
   input  [ ID_W-1:0] m1_axi_rid_i,
   input              m1_axi_rlast_i,
   output [   28-1:0] m1_axi_awaddr_o,
   output [    3-1:0] m1_axi_awprot_o,
   output             m1_axi_awvalid_o,
   input              m1_axi_awready_i,
   output [   32-1:0] m1_axi_wdata_o,
   output [    4-1:0] m1_axi_wstrb_o,
   output             m1_axi_wvalid_o,
   input              m1_axi_wready_i,
   input  [    2-1:0] m1_axi_bresp_i,
   input              m1_axi_bvalid_i,
   output             m1_axi_bready_o,
   output [ ID_W-1:0] m1_axi_awid_o,
   output [LEN_W-1:0] m1_axi_awlen_o,
   output [    3-1:0] m1_axi_awsize_o,
   output [    2-1:0] m1_axi_awburst_o,
   output             m1_axi_awlock_o,
   output [    4-1:0] m1_axi_awcache_o,
   output [    4-1:0] m1_axi_awqos_o,
   output             m1_axi_wlast_o,
   input  [ ID_W-1:0] m1_axi_bid_i,
   // m_2_m
   output [   28-1:0] m2_axi_araddr_o,
   output [    3-1:0] m2_axi_arprot_o,
   output             m2_axi_arvalid_o,
   input              m2_axi_arready_i,
   input  [   32-1:0] m2_axi_rdata_i,
   input  [    2-1:0] m2_axi_rresp_i,
   input              m2_axi_rvalid_i,
   output             m2_axi_rready_o,
   output [ ID_W-1:0] m2_axi_arid_o,
   output [LEN_W-1:0] m2_axi_arlen_o,
   output [    3-1:0] m2_axi_arsize_o,
   output [    2-1:0] m2_axi_arburst_o,
   output             m2_axi_arlock_o,
   output [    4-1:0] m2_axi_arcache_o,
   output [    4-1:0] m2_axi_arqos_o,
   input  [ ID_W-1:0] m2_axi_rid_i,
   input              m2_axi_rlast_i,
   output [   28-1:0] m2_axi_awaddr_o,
   output [    3-1:0] m2_axi_awprot_o,
   output             m2_axi_awvalid_o,
   input              m2_axi_awready_i,
   output [   32-1:0] m2_axi_wdata_o,
   output [    4-1:0] m2_axi_wstrb_o,
   output             m2_axi_wvalid_o,
   input              m2_axi_wready_i,
   input  [    2-1:0] m2_axi_bresp_i,
   input              m2_axi_bvalid_i,
   output             m2_axi_bready_o,
   output [ ID_W-1:0] m2_axi_awid_o,
   output [LEN_W-1:0] m2_axi_awlen_o,
   output [    3-1:0] m2_axi_awsize_o,
   output [    2-1:0] m2_axi_awburst_o,
   output             m2_axi_awlock_o,
   output [    4-1:0] m2_axi_awcache_o,
   output [    4-1:0] m2_axi_awqos_o,
   output             m2_axi_wlast_o,
   input  [ ID_W-1:0] m2_axi_bid_i
);
   // active_transaction_read_reg_en_rst
   wire                 active_transaction_read_reg_en;
   wire                 active_transaction_read_reg_rst;
   // active_transaction_read_reg_data_i
   wire                 active_transaction_read_reg_i;
   // active_transaction_read_reg_data_o
   wire                 active_transaction_read_reg_o;
   // read_sel_reg_data_i
   wire [        2-1:0] read_sel;
   // read_sel_reg_data_o
   wire [        2-1:0] read_sel_reg;
   // active_transaction_write_reg_en_rst
   wire                 active_transaction_write_reg_en;
   wire                 active_transaction_write_reg_rst;
   // active_transaction_write_reg_data_i
   wire                 active_transaction_write_reg_i;
   // active_transaction_write_reg_data_o
   wire                 active_transaction_write_reg_o;
   // data_burst_complete_write_reg_en_rst
   wire                 data_burst_complete_write_reg_en;
   wire                 data_burst_complete_write_reg_rst;
   // data_burst_complete_write_reg_data_i
   wire                 data_burst_complete_write_reg_i;
   // data_burst_complete_write_reg_data_o
   wire                 data_burst_complete_write_reg_o;
   // write_sel_reg_data_i
   wire [        2-1:0] write_sel;
   // write_sel_reg_data_o
   wire [        2-1:0] write_sel_reg;
   // demux_axi_awaddr_o
   wire [   3 * 30-1:0] demux_axi_awaddr;
   // demux_axi_awprot_o
   wire [    3 * 3-1:0] demux_axi_awprot;
   // demux_axi_awvalid_i
   wire                 demux_axi_awvalid_i;
   // demux_axi_awvalid_o
   wire [    3 * 1-1:0] demux_axi_awvalid;
   // mux_axi_awready_i
   wire [    3 * 1-1:0] mux_axi_awready;
   // mux_axi_awready_o
   wire                 mux_axi_awready_o;
   // demux_axi_wdata_o
   wire [   3 * 32-1:0] demux_axi_wdata;
   // demux_axi_wstrb_o
   wire [    3 * 4-1:0] demux_axi_wstrb;
   // demux_axi_wvalid_i
   wire                 demux_axi_wvalid_i;
   // demux_axi_wvalid_o
   wire [    3 * 1-1:0] demux_axi_wvalid;
   // mux_axi_wready_i
   wire [    3 * 1-1:0] mux_axi_wready;
   // mux_axi_wready_o
   wire                 mux_axi_wready_o;
   // mux_axi_bresp_i
   wire [    3 * 2-1:0] mux_axi_bresp;
   // mux_axi_bvalid_i
   wire [    3 * 1-1:0] mux_axi_bvalid;
   // demux_axi_bready_o
   wire [    3 * 1-1:0] demux_axi_bready;
   // demux_axi_awid_o
   wire [ 3 * ID_W-1:0] demux_axi_awid;
   // demux_axi_awlen_o
   wire [3 * LEN_W-1:0] demux_axi_awlen;
   // demux_axi_awsize_o
   wire [    3 * 3-1:0] demux_axi_awsize;
   // demux_axi_awburst_o
   wire [    3 * 2-1:0] demux_axi_awburst;
   // demux_axi_awlock_o
   wire [    3 * 1-1:0] demux_axi_awlock;
   // demux_axi_awcache_o
   wire [    3 * 4-1:0] demux_axi_awcache;
   // demux_axi_awqos_o
   wire [    3 * 4-1:0] demux_axi_awqos;
   // demux_axi_wlast_o
   wire [    3 * 1-1:0] demux_axi_wlast;
   // mux_axi_bid_i
   wire [ 3 * ID_W-1:0] mux_axi_bid;
   // demux_axi_araddr_o
   wire [   3 * 30-1:0] demux_axi_araddr;
   // demux_axi_arprot_o
   wire [    3 * 3-1:0] demux_axi_arprot;
   // demux_axi_arvalid_i
   wire                 demux_axi_arvalid_i;
   // demux_axi_arvalid_o
   wire [    3 * 1-1:0] demux_axi_arvalid;
   // mux_axi_arready_i
   wire [    3 * 1-1:0] mux_axi_arready;
   // mux_axi_arready_o
   wire                 mux_axi_arready_o;
   // mux_axi_rdata_i
   wire [   3 * 32-1:0] mux_axi_rdata;
   // mux_axi_rresp_i
   wire [    3 * 2-1:0] mux_axi_rresp;
   // mux_axi_rvalid_i
   wire [    3 * 1-1:0] mux_axi_rvalid;
   // demux_axi_rready_o
   wire [    3 * 1-1:0] demux_axi_rready;
   // demux_axi_arid_o
   wire [ 3 * ID_W-1:0] demux_axi_arid;
   // demux_axi_arlen_o
   wire [3 * LEN_W-1:0] demux_axi_arlen;
   // demux_axi_arsize_o
   wire [    3 * 3-1:0] demux_axi_arsize;
   // demux_axi_arburst_o
   wire [    3 * 2-1:0] demux_axi_arburst;
   // demux_axi_arlock_o
   wire [    3 * 1-1:0] demux_axi_arlock;
   // demux_axi_arcache_o
   wire [    3 * 4-1:0] demux_axi_arcache;
   // demux_axi_arqos_o
   wire [    3 * 4-1:0] demux_axi_arqos;
   // mux_axi_rid_i
   wire [ 3 * ID_W-1:0] mux_axi_rid;
   // mux_axi_rlast_i
   wire [    3 * 1-1:0] mux_axi_rlast;


   // Default description
   iob_reg_re #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) active_transaction_read_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (active_transaction_read_reg_en),
      .rst_i (active_transaction_read_reg_rst),
      // data_i port
      .data_i(active_transaction_read_reg_i),
      // data_o port
      .data_o(active_transaction_read_reg_o)
   );

   // Default description
   iob_reg_r #(
      .DATA_W (2),
      .RST_VAL(2'b0)
   ) read_sel_reg_r (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // rst_i port
      .rst_i (rst_i),
      // data_i port
      .data_i(read_sel),
      // data_o port
      .data_o(read_sel_reg)
   );

   // Default description
   iob_reg_re #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) active_transaction_write_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (active_transaction_write_reg_en),
      .rst_i (active_transaction_write_reg_rst),
      // data_i port
      .data_i(active_transaction_write_reg_i),
      // data_o port
      .data_o(active_transaction_write_reg_o)
   );

   // Default description
   iob_reg_re #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) data_burst_complete_write_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (data_burst_complete_write_reg_en),
      .rst_i (data_burst_complete_write_reg_rst),
      // data_i port
      .data_i(data_burst_complete_write_reg_i),
      // data_o port
      .data_o(data_burst_complete_write_reg_o)
   );

   // Default description
   iob_reg_r #(
      .DATA_W (2),
      .RST_VAL(2'b0)
   ) write_sel_reg_r (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // rst_i port
      .rst_i (rst_i),
      // data_i port
      .data_i(write_sel),
      // data_o port
      .data_o(write_sel_reg)
   );

   // Default description
   iob_demux #(
      .DATA_W(30),
      .N     (3)
   ) iob_demux_axi_awaddr (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awaddr_i),
      // data_o port
      .data_o(demux_axi_awaddr)
   );

   // Default description
   iob_demux #(
      .DATA_W(3),
      .N     (3)
   ) iob_demux_axi_awprot (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awprot_i),
      // data_o port
      .data_o(demux_axi_awprot)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_awvalid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(demux_axi_awvalid_i),
      // data_o port
      .data_o(demux_axi_awvalid)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_awready (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awready),
      // data_o port
      .data_o(mux_axi_awready_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(32),
      .N     (3)
   ) iob_demux_axi_wdata (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_wdata_i),
      // data_o port
      .data_o(demux_axi_wdata)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (3)
   ) iob_demux_axi_wstrb (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_wstrb_i),
      // data_o port
      .data_o(demux_axi_wstrb)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_wvalid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(demux_axi_wvalid_i),
      // data_o port
      .data_o(demux_axi_wvalid)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_wready (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_wready),
      // data_o port
      .data_o(mux_axi_wready_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(2),
      .N     (3)
   ) iob_mux_axi_bresp (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(mux_axi_bresp),
      // data_o port
      .data_o(s_axi_bresp_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_bvalid (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(mux_axi_bvalid),
      // data_o port
      .data_o(s_axi_bvalid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_bready (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(s_axi_bready_i),
      // data_o port
      .data_o(demux_axi_bready)
   );

   // Default description
   iob_demux #(
      .DATA_W(ID_W),
      .N     (3)
   ) iob_demux_axi_awid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awid_i),
      // data_o port
      .data_o(demux_axi_awid)
   );

   // Default description
   iob_demux #(
      .DATA_W(LEN_W),
      .N     (3)
   ) iob_demux_axi_awlen (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awlen_i),
      // data_o port
      .data_o(demux_axi_awlen)
   );

   // Default description
   iob_demux #(
      .DATA_W(3),
      .N     (3)
   ) iob_demux_axi_awsize (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awsize_i),
      // data_o port
      .data_o(demux_axi_awsize)
   );

   // Default description
   iob_demux #(
      .DATA_W(2),
      .N     (3)
   ) iob_demux_axi_awburst (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awburst_i),
      // data_o port
      .data_o(demux_axi_awburst)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_awlock (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awlock_i),
      // data_o port
      .data_o(demux_axi_awlock)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (3)
   ) iob_demux_axi_awcache (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awcache_i),
      // data_o port
      .data_o(demux_axi_awcache)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (3)
   ) iob_demux_axi_awqos (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_awqos_i),
      // data_o port
      .data_o(demux_axi_awqos)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_wlast (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(s_axi_wlast_i),
      // data_o port
      .data_o(demux_axi_wlast)
   );

   // Default description
   iob_mux #(
      .DATA_W(ID_W),
      .N     (3)
   ) iob_mux_axi_bid (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(mux_axi_bid),
      // data_o port
      .data_o(s_axi_bid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(30),
      .N     (3)
   ) iob_demux_axi_araddr (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_araddr_i),
      // data_o port
      .data_o(demux_axi_araddr)
   );

   // Default description
   iob_demux #(
      .DATA_W(3),
      .N     (3)
   ) iob_demux_axi_arprot (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arprot_i),
      // data_o port
      .data_o(demux_axi_arprot)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_arvalid (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(demux_axi_arvalid_i),
      // data_o port
      .data_o(demux_axi_arvalid)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_arready (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arready),
      // data_o port
      .data_o(mux_axi_arready_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(32),
      .N     (3)
   ) iob_mux_axi_rdata (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rdata),
      // data_o port
      .data_o(s_axi_rdata_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(2),
      .N     (3)
   ) iob_mux_axi_rresp (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rresp),
      // data_o port
      .data_o(s_axi_rresp_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_rvalid (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rvalid),
      // data_o port
      .data_o(s_axi_rvalid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_rready (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(s_axi_rready_i),
      // data_o port
      .data_o(demux_axi_rready)
   );

   // Default description
   iob_demux #(
      .DATA_W(ID_W),
      .N     (3)
   ) iob_demux_axi_arid (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arid_i),
      // data_o port
      .data_o(demux_axi_arid)
   );

   // Default description
   iob_demux #(
      .DATA_W(LEN_W),
      .N     (3)
   ) iob_demux_axi_arlen (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arlen_i),
      // data_o port
      .data_o(demux_axi_arlen)
   );

   // Default description
   iob_demux #(
      .DATA_W(3),
      .N     (3)
   ) iob_demux_axi_arsize (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arsize_i),
      // data_o port
      .data_o(demux_axi_arsize)
   );

   // Default description
   iob_demux #(
      .DATA_W(2),
      .N     (3)
   ) iob_demux_axi_arburst (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arburst_i),
      // data_o port
      .data_o(demux_axi_arburst)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (3)
   ) iob_demux_axi_arlock (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arlock_i),
      // data_o port
      .data_o(demux_axi_arlock)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (3)
   ) iob_demux_axi_arcache (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arcache_i),
      // data_o port
      .data_o(demux_axi_arcache)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (3)
   ) iob_demux_axi_arqos (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(s_axi_arqos_i),
      // data_o port
      .data_o(demux_axi_arqos)
   );

   // Default description
   iob_mux #(
      .DATA_W(ID_W),
      .N     (3)
   ) iob_mux_axi_rid (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rid),
      // data_o port
      .data_o(s_axi_rid_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (3)
   ) iob_mux_axi_rlast (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rlast),
      // data_o port
      .data_o(s_axi_rlast_o)
   );




   //
   // Read
   //

   // Only switch slaves when there is no current active transaction
   assign read_sel = active_transaction_read_reg_o ? read_sel_reg : s_axi_araddr_i[29-:2];

   // Block address valid/ready signals of current slave if there is still an active transaction
   assign s_axi_arready_o = ~active_transaction_read_reg_o & mux_axi_arready_o;
   assign demux_axi_arvalid_i = ~active_transaction_read_reg_o & s_axi_arvalid_i;

   assign active_transaction_read_reg_en = s_axi_arvalid_i & s_axi_arready_o;
   assign active_transaction_read_reg_rst = (s_axi_rlast_o & s_axi_rvalid_o & s_axi_rready_i) | rst_i;
   assign active_transaction_read_reg_i = 1'b1;

   //
   // Write
   //

   // NOTE: Current logic does not allow wvalid to be asserted before awvalid!
   //       If the wvalid comes before, the data will go to the currently selected slave_interface, and that may not be the intended destination (real destination will be given later by awvalid)

   // Only switch slaves when there is no current active transaction
   assign write_sel = active_transaction_write_reg_o ? write_sel_reg : s_axi_awaddr_i[29-:2];

   // Block address valid/ready signals of current slave if there is still an active transaction
   assign s_axi_awready_o = ~active_transaction_write_reg_o & mux_axi_awready_o;
   assign demux_axi_awvalid_i = ~active_transaction_write_reg_o & s_axi_awvalid_i;

   assign active_transaction_write_reg_en = s_axi_awvalid_i & s_axi_awready_o;
   assign active_transaction_write_reg_rst = (s_axi_bvalid_o & s_axi_bready_i) | rst_i;
   assign active_transaction_write_reg_i = 1'b1;

   // Block data valid/ready signals of current slave if there is still an active transaction
   assign s_axi_wready_o = ~data_burst_complete_write_reg_o & mux_axi_wready_o;
   assign demux_axi_wvalid_i = ~data_burst_complete_write_reg_o & s_axi_wvalid_i;

   assign data_burst_complete_write_reg_en = s_axi_wlast_i & s_axi_wvalid_i & s_axi_wready_o;
   assign data_burst_complete_write_reg_rst = active_transaction_write_reg_rst;
   assign data_burst_complete_write_reg_i = 1'b1;



   assign m0_axi_araddr_o = demux_axi_araddr[0+:28];
   assign m0_axi_awaddr_o = demux_axi_awaddr[0+:28];

   assign m1_axi_araddr_o = demux_axi_araddr[30+:28];
   assign m1_axi_awaddr_o = demux_axi_awaddr[30+:28];

   assign m2_axi_araddr_o = demux_axi_araddr[60+:28];
   assign m2_axi_awaddr_o = demux_axi_awaddr[60+:28];

   assign m0_axi_awprot_o = demux_axi_awprot[0*3+:3];

   assign m1_axi_awprot_o = demux_axi_awprot[1*3+:3];

   assign m2_axi_awprot_o = demux_axi_awprot[2*3+:3];

   assign m0_axi_awvalid_o = demux_axi_awvalid[0*1+:1];

   assign m1_axi_awvalid_o = demux_axi_awvalid[1*1+:1];

   assign m2_axi_awvalid_o = demux_axi_awvalid[2*1+:1];
   assign mux_axi_awready = {m2_axi_awready_i, m1_axi_awready_i, m0_axi_awready_i};

   assign m0_axi_wdata_o = demux_axi_wdata[0*32+:32];

   assign m1_axi_wdata_o = demux_axi_wdata[1*32+:32];

   assign m2_axi_wdata_o = demux_axi_wdata[2*32+:32];

   assign m0_axi_wstrb_o = demux_axi_wstrb[0*4+:4];

   assign m1_axi_wstrb_o = demux_axi_wstrb[1*4+:4];

   assign m2_axi_wstrb_o = demux_axi_wstrb[2*4+:4];

   assign m0_axi_wvalid_o = demux_axi_wvalid[0*1+:1];

   assign m1_axi_wvalid_o = demux_axi_wvalid[1*1+:1];

   assign m2_axi_wvalid_o = demux_axi_wvalid[2*1+:1];
   assign mux_axi_wready = {m2_axi_wready_i, m1_axi_wready_i, m0_axi_wready_i};
   assign mux_axi_bresp = {m2_axi_bresp_i, m1_axi_bresp_i, m0_axi_bresp_i};
   assign mux_axi_bvalid = {m2_axi_bvalid_i, m1_axi_bvalid_i, m0_axi_bvalid_i};

   assign m0_axi_bready_o = demux_axi_bready[0*1+:1];

   assign m1_axi_bready_o = demux_axi_bready[1*1+:1];

   assign m2_axi_bready_o = demux_axi_bready[2*1+:1];

   assign m0_axi_awid_o = demux_axi_awid[0*ID_W+:ID_W];

   assign m1_axi_awid_o = demux_axi_awid[1*ID_W+:ID_W];

   assign m2_axi_awid_o = demux_axi_awid[2*ID_W+:ID_W];

   assign m0_axi_awlen_o = demux_axi_awlen[0*LEN_W+:LEN_W];

   assign m1_axi_awlen_o = demux_axi_awlen[1*LEN_W+:LEN_W];

   assign m2_axi_awlen_o = demux_axi_awlen[2*LEN_W+:LEN_W];

   assign m0_axi_awsize_o = demux_axi_awsize[0*3+:3];

   assign m1_axi_awsize_o = demux_axi_awsize[1*3+:3];

   assign m2_axi_awsize_o = demux_axi_awsize[2*3+:3];

   assign m0_axi_awburst_o = demux_axi_awburst[0*2+:2];

   assign m1_axi_awburst_o = demux_axi_awburst[1*2+:2];

   assign m2_axi_awburst_o = demux_axi_awburst[2*2+:2];

   assign m0_axi_awlock_o = demux_axi_awlock[0*1+:1];

   assign m1_axi_awlock_o = demux_axi_awlock[1*1+:1];

   assign m2_axi_awlock_o = demux_axi_awlock[2*1+:1];

   assign m0_axi_awcache_o = demux_axi_awcache[0*4+:4];

   assign m1_axi_awcache_o = demux_axi_awcache[1*4+:4];

   assign m2_axi_awcache_o = demux_axi_awcache[2*4+:4];

   assign m0_axi_awqos_o = demux_axi_awqos[0*4+:4];

   assign m1_axi_awqos_o = demux_axi_awqos[1*4+:4];

   assign m2_axi_awqos_o = demux_axi_awqos[2*4+:4];

   assign m0_axi_wlast_o = demux_axi_wlast[0*1+:1];

   assign m1_axi_wlast_o = demux_axi_wlast[1*1+:1];

   assign m2_axi_wlast_o = demux_axi_wlast[2*1+:1];
   assign mux_axi_bid = {m2_axi_bid_i, m1_axi_bid_i, m0_axi_bid_i};

   assign m0_axi_arprot_o = demux_axi_arprot[0*3+:3];

   assign m1_axi_arprot_o = demux_axi_arprot[1*3+:3];

   assign m2_axi_arprot_o = demux_axi_arprot[2*3+:3];

   assign m0_axi_arvalid_o = demux_axi_arvalid[0*1+:1];

   assign m1_axi_arvalid_o = demux_axi_arvalid[1*1+:1];

   assign m2_axi_arvalid_o = demux_axi_arvalid[2*1+:1];
   assign mux_axi_arready = {m2_axi_arready_i, m1_axi_arready_i, m0_axi_arready_i};
   assign mux_axi_rdata = {m2_axi_rdata_i, m1_axi_rdata_i, m0_axi_rdata_i};
   assign mux_axi_rresp = {m2_axi_rresp_i, m1_axi_rresp_i, m0_axi_rresp_i};
   assign mux_axi_rvalid = {m2_axi_rvalid_i, m1_axi_rvalid_i, m0_axi_rvalid_i};

   assign m0_axi_rready_o = demux_axi_rready[0*1+:1];

   assign m1_axi_rready_o = demux_axi_rready[1*1+:1];

   assign m2_axi_rready_o = demux_axi_rready[2*1+:1];

   assign m0_axi_arid_o = demux_axi_arid[0*ID_W+:ID_W];

   assign m1_axi_arid_o = demux_axi_arid[1*ID_W+:ID_W];

   assign m2_axi_arid_o = demux_axi_arid[2*ID_W+:ID_W];

   assign m0_axi_arlen_o = demux_axi_arlen[0*LEN_W+:LEN_W];

   assign m1_axi_arlen_o = demux_axi_arlen[1*LEN_W+:LEN_W];

   assign m2_axi_arlen_o = demux_axi_arlen[2*LEN_W+:LEN_W];

   assign m0_axi_arsize_o = demux_axi_arsize[0*3+:3];

   assign m1_axi_arsize_o = demux_axi_arsize[1*3+:3];

   assign m2_axi_arsize_o = demux_axi_arsize[2*3+:3];

   assign m0_axi_arburst_o = demux_axi_arburst[0*2+:2];

   assign m1_axi_arburst_o = demux_axi_arburst[1*2+:2];

   assign m2_axi_arburst_o = demux_axi_arburst[2*2+:2];

   assign m0_axi_arlock_o = demux_axi_arlock[0*1+:1];

   assign m1_axi_arlock_o = demux_axi_arlock[1*1+:1];

   assign m2_axi_arlock_o = demux_axi_arlock[2*1+:1];

   assign m0_axi_arcache_o = demux_axi_arcache[0*4+:4];

   assign m1_axi_arcache_o = demux_axi_arcache[1*4+:4];

   assign m2_axi_arcache_o = demux_axi_arcache[2*4+:4];

   assign m0_axi_arqos_o = demux_axi_arqos[0*4+:4];

   assign m1_axi_arqos_o = demux_axi_arqos[1*4+:4];

   assign m2_axi_arqos_o = demux_axi_arqos[2*4+:4];
   assign mux_axi_rid = {m2_axi_rid_i, m1_axi_rid_i, m0_axi_rid_i};
   assign mux_axi_rlast = {m2_axi_rlast_i, m1_axi_rlast_i, m0_axi_rlast_i};




endmodule
