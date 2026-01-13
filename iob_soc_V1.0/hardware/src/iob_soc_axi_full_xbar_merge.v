`timescale 1ns / 1ps
`include "iob_soc_axi_full_xbar_merge_conf.vh"

module iob_soc_axi_full_xbar_merge #(
   parameter ID_W  = `IOB_SOC_AXI_FULL_XBAR_MERGE_ID_W,
   parameter LEN_W = `IOB_SOC_AXI_FULL_XBAR_MERGE_LEN_W
) (
   // clk_en_rst_s
   input              clk_i,
   input              cke_i,
   input              arst_i,
   // reset_i
   input              rst_i,
   // m_m
   output [   29-1:0] m_axi_araddr_o,
   output [    3-1:0] m_axi_arprot_o,
   output             m_axi_arvalid_o,
   input              m_axi_arready_i,
   input  [   32-1:0] m_axi_rdata_i,
   input  [    2-1:0] m_axi_rresp_i,
   input              m_axi_rvalid_i,
   output             m_axi_rready_o,
   output [ ID_W-1:0] m_axi_arid_o,
   output [LEN_W-1:0] m_axi_arlen_o,
   output [    3-1:0] m_axi_arsize_o,
   output [    2-1:0] m_axi_arburst_o,
   output             m_axi_arlock_o,
   output [    4-1:0] m_axi_arcache_o,
   output [    4-1:0] m_axi_arqos_o,
   input  [ ID_W-1:0] m_axi_rid_i,
   input              m_axi_rlast_i,
   output [   29-1:0] m_axi_awaddr_o,
   output [    3-1:0] m_axi_awprot_o,
   output             m_axi_awvalid_o,
   input              m_axi_awready_i,
   output [   32-1:0] m_axi_wdata_o,
   output [    4-1:0] m_axi_wstrb_o,
   output             m_axi_wvalid_o,
   input              m_axi_wready_i,
   input  [    2-1:0] m_axi_bresp_i,
   input              m_axi_bvalid_i,
   output             m_axi_bready_o,
   output [ ID_W-1:0] m_axi_awid_o,
   output [LEN_W-1:0] m_axi_awlen_o,
   output [    3-1:0] m_axi_awsize_o,
   output [    2-1:0] m_axi_awburst_o,
   output             m_axi_awlock_o,
   output [    4-1:0] m_axi_awcache_o,
   output [    4-1:0] m_axi_awqos_o,
   output             m_axi_wlast_o,
   input  [ ID_W-1:0] m_axi_bid_i,
   // s_0_s
   input  [   28-1:0] s0_axi_araddr_i,
   input  [    3-1:0] s0_axi_arprot_i,
   input              s0_axi_arvalid_i,
   output             s0_axi_arready_o,
   output [   32-1:0] s0_axi_rdata_o,
   output [    2-1:0] s0_axi_rresp_o,
   output             s0_axi_rvalid_o,
   input              s0_axi_rready_i,
   input  [ ID_W-1:0] s0_axi_arid_i,
   input  [LEN_W-1:0] s0_axi_arlen_i,
   input  [    3-1:0] s0_axi_arsize_i,
   input  [    2-1:0] s0_axi_arburst_i,
   input              s0_axi_arlock_i,
   input  [    4-1:0] s0_axi_arcache_i,
   input  [    4-1:0] s0_axi_arqos_i,
   output [ ID_W-1:0] s0_axi_rid_o,
   output             s0_axi_rlast_o,
   input  [   28-1:0] s0_axi_awaddr_i,
   input  [    3-1:0] s0_axi_awprot_i,
   input              s0_axi_awvalid_i,
   output             s0_axi_awready_o,
   input  [   32-1:0] s0_axi_wdata_i,
   input  [    4-1:0] s0_axi_wstrb_i,
   input              s0_axi_wvalid_i,
   output             s0_axi_wready_o,
   output [    2-1:0] s0_axi_bresp_o,
   output             s0_axi_bvalid_o,
   input              s0_axi_bready_i,
   input  [ ID_W-1:0] s0_axi_awid_i,
   input  [LEN_W-1:0] s0_axi_awlen_i,
   input  [    3-1:0] s0_axi_awsize_i,
   input  [    2-1:0] s0_axi_awburst_i,
   input              s0_axi_awlock_i,
   input  [    4-1:0] s0_axi_awcache_i,
   input  [    4-1:0] s0_axi_awqos_i,
   input              s0_axi_wlast_i,
   output [ ID_W-1:0] s0_axi_bid_o,
   // s_1_s
   input  [   28-1:0] s1_axi_araddr_i,
   input  [    3-1:0] s1_axi_arprot_i,
   input              s1_axi_arvalid_i,
   output             s1_axi_arready_o,
   output [   32-1:0] s1_axi_rdata_o,
   output [    2-1:0] s1_axi_rresp_o,
   output             s1_axi_rvalid_o,
   input              s1_axi_rready_i,
   input  [ ID_W-1:0] s1_axi_arid_i,
   input  [LEN_W-1:0] s1_axi_arlen_i,
   input  [    3-1:0] s1_axi_arsize_i,
   input  [    2-1:0] s1_axi_arburst_i,
   input              s1_axi_arlock_i,
   input  [    4-1:0] s1_axi_arcache_i,
   input  [    4-1:0] s1_axi_arqos_i,
   output [ ID_W-1:0] s1_axi_rid_o,
   output             s1_axi_rlast_o,
   input  [   28-1:0] s1_axi_awaddr_i,
   input  [    3-1:0] s1_axi_awprot_i,
   input              s1_axi_awvalid_i,
   output             s1_axi_awready_o,
   input  [   32-1:0] s1_axi_wdata_i,
   input  [    4-1:0] s1_axi_wstrb_i,
   input              s1_axi_wvalid_i,
   output             s1_axi_wready_o,
   output [    2-1:0] s1_axi_bresp_o,
   output             s1_axi_bvalid_o,
   input              s1_axi_bready_i,
   input  [ ID_W-1:0] s1_axi_awid_i,
   input  [LEN_W-1:0] s1_axi_awlen_i,
   input  [    3-1:0] s1_axi_awsize_i,
   input  [    2-1:0] s1_axi_awburst_i,
   input              s1_axi_awlock_i,
   input  [    4-1:0] s1_axi_awcache_i,
   input  [    4-1:0] s1_axi_awqos_i,
   input              s1_axi_wlast_i,
   output [ ID_W-1:0] s1_axi_bid_o
);
   // busy_read_reg_en_rst
   wire                 busy_read_reg_en;
   wire                 busy_read_reg_rst;
   // busy_read_reg_data_i
   wire                 busy_read_reg_i;
   // busy_read_reg_data_o
   wire                 busy_read_reg_o;
   // active_transaction_read_reg_en_rst
   wire                 active_transaction_read_reg_en;
   wire                 active_transaction_read_reg_rst;
   // active_transaction_read_reg_data_i
   wire                 active_transaction_read_reg_i;
   // active_transaction_read_reg_data_o
   wire                 active_transaction_read_reg_o;
   // read_sel_reg_data_i
   wire                 read_sel;
   // read_sel_reg_data_o
   wire                 read_sel_reg;
   // busy_write_reg_en_rst
   wire                 busy_write_reg_en;
   wire                 busy_write_reg_rst;
   // busy_write_reg_data_i
   wire                 busy_write_reg_i;
   // busy_write_reg_data_o
   wire                 busy_write_reg_o;
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
   wire                 write_sel;
   // write_sel_reg_data_o
   wire                 write_sel_reg;
   // read_sel_prio_enc_i
   wire [    2 * 1-1:0] mux_axi_arvalid;
   // read_sel_prio_enc_o
   wire                 read_sel_prio_enc_o;
   // write_sel_prio_enc_i
   wire [    2 * 1-1:0] mux_axi_awvalid;
   // write_sel_prio_enc_o
   wire                 write_sel_prio_enc_o;
   // mux_axi_awaddr_i
   wire [   2 * 29-1:0] mux_axi_awaddr;
   // mux_axi_awprot_i
   wire [    2 * 3-1:0] mux_axi_awprot;
   // mux_axi_awvalid_o
   wire                 mux_axi_awvalid_o;
   // demux_axi_awready_i
   wire                 demux_axi_awready_i;
   // demux_axi_awready_o
   wire [    2 * 1-1:0] demux_axi_awready;
   // mux_axi_wdata_i
   wire [   2 * 32-1:0] mux_axi_wdata;
   // mux_axi_wstrb_i
   wire [    2 * 4-1:0] mux_axi_wstrb;
   // mux_axi_wvalid_i
   wire [    2 * 1-1:0] mux_axi_wvalid;
   // mux_axi_wvalid_o
   wire                 mux_axi_wvalid_o;
   // demux_axi_wready_i
   wire                 demux_axi_wready_i;
   // demux_axi_wready_o
   wire [    2 * 1-1:0] demux_axi_wready;
   // demux_axi_bresp_o
   wire [    2 * 2-1:0] demux_axi_bresp;
   // demux_axi_bvalid_o
   wire [    2 * 1-1:0] demux_axi_bvalid;
   // mux_axi_bready_i
   wire [    2 * 1-1:0] mux_axi_bready;
   // mux_axi_awid_i
   wire [ 2 * ID_W-1:0] mux_axi_awid;
   // mux_axi_awlen_i
   wire [2 * LEN_W-1:0] mux_axi_awlen;
   // mux_axi_awsize_i
   wire [    2 * 3-1:0] mux_axi_awsize;
   // mux_axi_awburst_i
   wire [    2 * 2-1:0] mux_axi_awburst;
   // mux_axi_awlock_i
   wire [    2 * 1-1:0] mux_axi_awlock;
   // mux_axi_awcache_i
   wire [    2 * 4-1:0] mux_axi_awcache;
   // mux_axi_awqos_i
   wire [    2 * 4-1:0] mux_axi_awqos;
   // mux_axi_wlast_i
   wire [    2 * 1-1:0] mux_axi_wlast;
   // demux_axi_bid_o
   wire [ 2 * ID_W-1:0] demux_axi_bid;
   // mux_axi_araddr_i
   wire [   2 * 29-1:0] mux_axi_araddr;
   // mux_axi_arprot_i
   wire [    2 * 3-1:0] mux_axi_arprot;
   // mux_axi_arvalid_o
   wire                 mux_axi_arvalid_o;
   // demux_axi_arready_i
   wire                 demux_axi_arready_i;
   // demux_axi_arready_o
   wire [    2 * 1-1:0] demux_axi_arready;
   // demux_axi_rdata_o
   wire [   2 * 32-1:0] demux_axi_rdata;
   // demux_axi_rresp_o
   wire [    2 * 2-1:0] demux_axi_rresp;
   // demux_axi_rvalid_o
   wire [    2 * 1-1:0] demux_axi_rvalid;
   // mux_axi_rready_i
   wire [    2 * 1-1:0] mux_axi_rready;
   // mux_axi_arid_i
   wire [ 2 * ID_W-1:0] mux_axi_arid;
   // mux_axi_arlen_i
   wire [2 * LEN_W-1:0] mux_axi_arlen;
   // mux_axi_arsize_i
   wire [    2 * 3-1:0] mux_axi_arsize;
   // mux_axi_arburst_i
   wire [    2 * 2-1:0] mux_axi_arburst;
   // mux_axi_arlock_i
   wire [    2 * 1-1:0] mux_axi_arlock;
   // mux_axi_arcache_i
   wire [    2 * 4-1:0] mux_axi_arcache;
   // mux_axi_arqos_i
   wire [    2 * 4-1:0] mux_axi_arqos;
   // demux_axi_rid_o
   wire [ 2 * ID_W-1:0] demux_axi_rid;
   // demux_axi_rlast_o
   wire [    2 * 1-1:0] demux_axi_rlast;


   // Default description
   iob_reg_re #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) busy_read_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (busy_read_reg_en),
      .rst_i (busy_read_reg_rst),
      // data_i port
      .data_i(busy_read_reg_i),
      // data_o port
      .data_o(busy_read_reg_o)
   );

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
      .DATA_W (1),
      .RST_VAL(1'b0)
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
   iob_prio_enc #(
      .W   (2),
      .MODE("HIGH")
   ) read_sel_enc (
      // unencoded_i port
      .unencoded_i(mux_axi_arvalid),
      // encoded_o port
      .encoded_o  (read_sel_prio_enc_o)
   );

   // Default description
   iob_reg_re #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) busy_write_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (busy_write_reg_en),
      .rst_i (busy_write_reg_rst),
      // data_i port
      .data_i(busy_write_reg_i),
      // data_o port
      .data_o(busy_write_reg_o)
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
      .DATA_W (1),
      .RST_VAL(1'b0)
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
   iob_prio_enc #(
      .W   (2),
      .MODE("HIGH")
   ) write_sel_enc (
      // unencoded_i port
      .unencoded_i(mux_axi_awvalid),
      // encoded_o port
      .encoded_o  (write_sel_prio_enc_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(29),
      .N     (2)
   ) iob_mux_axi_awaddr (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awaddr),
      // data_o port
      .data_o(m_axi_awaddr_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(3),
      .N     (2)
   ) iob_mux_axi_awprot (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awprot),
      // data_o port
      .data_o(m_axi_awprot_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_awvalid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awvalid),
      // data_o port
      .data_o(mux_axi_awvalid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_awready (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(demux_axi_awready_i),
      // data_o port
      .data_o(demux_axi_awready)
   );

   // Default description
   iob_mux #(
      .DATA_W(32),
      .N     (2)
   ) iob_mux_axi_wdata (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_wdata),
      // data_o port
      .data_o(m_axi_wdata_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(4),
      .N     (2)
   ) iob_mux_axi_wstrb (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_wstrb),
      // data_o port
      .data_o(m_axi_wstrb_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_wvalid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_wvalid),
      // data_o port
      .data_o(mux_axi_wvalid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_wready (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(demux_axi_wready_i),
      // data_o port
      .data_o(demux_axi_wready)
   );

   // Default description
   iob_demux #(
      .DATA_W(2),
      .N     (2)
   ) iob_demux_axi_bresp (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(m_axi_bresp_i),
      // data_o port
      .data_o(demux_axi_bresp)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_bvalid (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(m_axi_bvalid_i),
      // data_o port
      .data_o(demux_axi_bvalid)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_bready (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(mux_axi_bready),
      // data_o port
      .data_o(m_axi_bready_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(ID_W),
      .N     (2)
   ) iob_mux_axi_awid (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awid),
      // data_o port
      .data_o(m_axi_awid_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(LEN_W),
      .N     (2)
   ) iob_mux_axi_awlen (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awlen),
      // data_o port
      .data_o(m_axi_awlen_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(3),
      .N     (2)
   ) iob_mux_axi_awsize (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awsize),
      // data_o port
      .data_o(m_axi_awsize_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(2),
      .N     (2)
   ) iob_mux_axi_awburst (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awburst),
      // data_o port
      .data_o(m_axi_awburst_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_awlock (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awlock),
      // data_o port
      .data_o(m_axi_awlock_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(4),
      .N     (2)
   ) iob_mux_axi_awcache (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awcache),
      // data_o port
      .data_o(m_axi_awcache_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(4),
      .N     (2)
   ) iob_mux_axi_awqos (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_awqos),
      // data_o port
      .data_o(m_axi_awqos_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_wlast (
      // sel_i port
      .sel_i (write_sel),
      // data_i port
      .data_i(mux_axi_wlast),
      // data_o port
      .data_o(m_axi_wlast_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(ID_W),
      .N     (2)
   ) iob_demux_axi_bid (
      // sel_i port
      .sel_i (write_sel_reg),
      // data_i port
      .data_i(m_axi_bid_i),
      // data_o port
      .data_o(demux_axi_bid)
   );

   // Default description
   iob_mux #(
      .DATA_W(29),
      .N     (2)
   ) iob_mux_axi_araddr (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_araddr),
      // data_o port
      .data_o(m_axi_araddr_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(3),
      .N     (2)
   ) iob_mux_axi_arprot (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arprot),
      // data_o port
      .data_o(m_axi_arprot_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_arvalid (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arvalid),
      // data_o port
      .data_o(mux_axi_arvalid_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_arready (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(demux_axi_arready_i),
      // data_o port
      .data_o(demux_axi_arready)
   );

   // Default description
   iob_demux #(
      .DATA_W(32),
      .N     (2)
   ) iob_demux_axi_rdata (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(m_axi_rdata_i),
      // data_o port
      .data_o(demux_axi_rdata)
   );

   // Default description
   iob_demux #(
      .DATA_W(2),
      .N     (2)
   ) iob_demux_axi_rresp (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(m_axi_rresp_i),
      // data_o port
      .data_o(demux_axi_rresp)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_rvalid (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(m_axi_rvalid_i),
      // data_o port
      .data_o(demux_axi_rvalid)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_rready (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(mux_axi_rready),
      // data_o port
      .data_o(m_axi_rready_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(ID_W),
      .N     (2)
   ) iob_mux_axi_arid (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arid),
      // data_o port
      .data_o(m_axi_arid_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(LEN_W),
      .N     (2)
   ) iob_mux_axi_arlen (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arlen),
      // data_o port
      .data_o(m_axi_arlen_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(3),
      .N     (2)
   ) iob_mux_axi_arsize (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arsize),
      // data_o port
      .data_o(m_axi_arsize_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(2),
      .N     (2)
   ) iob_mux_axi_arburst (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arburst),
      // data_o port
      .data_o(m_axi_arburst_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (2)
   ) iob_mux_axi_arlock (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arlock),
      // data_o port
      .data_o(m_axi_arlock_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(4),
      .N     (2)
   ) iob_mux_axi_arcache (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arcache),
      // data_o port
      .data_o(m_axi_arcache_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(4),
      .N     (2)
   ) iob_mux_axi_arqos (
      // sel_i port
      .sel_i (read_sel),
      // data_i port
      .data_i(mux_axi_arqos),
      // data_o port
      .data_o(m_axi_arqos_o)
   );

   // Default description
   iob_demux #(
      .DATA_W(ID_W),
      .N     (2)
   ) iob_demux_axi_rid (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(m_axi_rid_i),
      // data_o port
      .data_o(demux_axi_rid)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (2)
   ) iob_demux_axi_rlast (
      // sel_i port
      .sel_i (read_sel_reg),
      // data_i port
      .data_i(m_axi_rlast_i),
      // data_o port
      .data_o(demux_axi_rlast)
   );




   //
   // Read
   //

   // Only switch masters when there is no current active transaction
   assign read_sel = busy_read_reg_o ? read_sel_reg : read_sel_prio_enc_o;

   assign busy_read_reg_en = m_axi_arvalid_o & !busy_read_reg_o;
   assign busy_read_reg_rst = (m_axi_rlast_i & m_axi_rvalid_i & m_axi_rready_o) | rst_i;
   assign busy_read_reg_i = 1'b1;

   // Block address valid/ready signals of current master if there is still an active transaction
   assign m_axi_arvalid_o = ~active_transaction_read_reg_o & mux_axi_arvalid_o;
   assign demux_axi_arready_i = ~active_transaction_read_reg_o & m_axi_arready_i;

   assign active_transaction_read_reg_en = m_axi_arvalid_o & m_axi_arready_i;
   assign active_transaction_read_reg_rst = busy_read_reg_rst;
   assign active_transaction_read_reg_i = 1'b1;

   //
   // Write
   //

   // NOTE: Current logic does not allow wvalid to be asserted before awvalid!
   //       If the wvalid comes before, the data will go to the currently selected master_interface, and that may not be the intended destination (real destination will be given later by awvalid)

   // Only switch masters when there is no current active transaction
   assign write_sel = busy_write_reg_o ? write_sel_reg : write_sel_prio_enc_o;

   assign busy_write_reg_en = m_axi_awvalid_o & !busy_write_reg_o;
   assign busy_write_reg_rst = (m_axi_bvalid_i & m_axi_bready_o) | rst_i;
   assign busy_write_reg_i = 1'b1;

   // Block address valid/ready signals of current master if there is still an active transaction
   assign m_axi_awvalid_o = ~active_transaction_write_reg_o & mux_axi_awvalid_o;
   assign demux_axi_awready_i = ~active_transaction_write_reg_o & m_axi_awready_i;

   assign active_transaction_write_reg_en = m_axi_awvalid_o & m_axi_awready_i;
   assign active_transaction_write_reg_rst = busy_write_reg_rst;
   assign active_transaction_write_reg_i = 1'b1;

   // Block data valid/ready signals of current master if there is still an active transaction
   assign m_axi_wvalid_o = ~data_burst_complete_write_reg_o & mux_axi_wvalid_o;
   assign demux_axi_wready_i = ~data_burst_complete_write_reg_o & m_axi_wready_i;

   assign data_burst_complete_write_reg_en = m_axi_wlast_o & m_axi_wvalid_o & m_axi_wready_i;
   assign data_burst_complete_write_reg_rst = busy_write_reg_rst;
   assign data_burst_complete_write_reg_i = 1'b1;

   assign mux_axi_awaddr = {{1'd1}, s1_axi_awaddr_i, {1'd0}, s0_axi_awaddr_i};
   assign mux_axi_awprot = {s1_axi_awprot_i, s0_axi_awprot_i};
   assign mux_axi_awvalid = {s1_axi_awvalid_i, s0_axi_awvalid_i};

   assign s0_axi_awready_o = demux_axi_awready[0*1+:1];

   assign s1_axi_awready_o = demux_axi_awready[1*1+:1];
   assign mux_axi_wdata = {s1_axi_wdata_i, s0_axi_wdata_i};
   assign mux_axi_wstrb = {s1_axi_wstrb_i, s0_axi_wstrb_i};
   assign mux_axi_wvalid = {s1_axi_wvalid_i, s0_axi_wvalid_i};

   assign s0_axi_wready_o = demux_axi_wready[0*1+:1];

   assign s1_axi_wready_o = demux_axi_wready[1*1+:1];

   assign s0_axi_bresp_o = demux_axi_bresp[0*2+:2];

   assign s1_axi_bresp_o = demux_axi_bresp[1*2+:2];

   assign s0_axi_bvalid_o = demux_axi_bvalid[0*1+:1];

   assign s1_axi_bvalid_o = demux_axi_bvalid[1*1+:1];
   assign mux_axi_bready = {s1_axi_bready_i, s0_axi_bready_i};
   assign mux_axi_awid = {s1_axi_awid_i, s0_axi_awid_i};
   assign mux_axi_awlen = {s1_axi_awlen_i, s0_axi_awlen_i};
   assign mux_axi_awsize = {s1_axi_awsize_i, s0_axi_awsize_i};
   assign mux_axi_awburst = {s1_axi_awburst_i, s0_axi_awburst_i};
   assign mux_axi_awlock = {s1_axi_awlock_i, s0_axi_awlock_i};
   assign mux_axi_awcache = {s1_axi_awcache_i, s0_axi_awcache_i};
   assign mux_axi_awqos = {s1_axi_awqos_i, s0_axi_awqos_i};
   assign mux_axi_wlast = {s1_axi_wlast_i, s0_axi_wlast_i};

   assign s0_axi_bid_o = demux_axi_bid[0*ID_W+:ID_W];

   assign s1_axi_bid_o = demux_axi_bid[1*ID_W+:ID_W];
   assign mux_axi_araddr = {{1'd1}, s1_axi_araddr_i, {1'd0}, s0_axi_araddr_i};
   assign mux_axi_arprot = {s1_axi_arprot_i, s0_axi_arprot_i};
   assign mux_axi_arvalid = {s1_axi_arvalid_i, s0_axi_arvalid_i};

   assign s0_axi_arready_o = demux_axi_arready[0*1+:1];

   assign s1_axi_arready_o = demux_axi_arready[1*1+:1];

   assign s0_axi_rdata_o = demux_axi_rdata[0*32+:32];

   assign s1_axi_rdata_o = demux_axi_rdata[1*32+:32];

   assign s0_axi_rresp_o = demux_axi_rresp[0*2+:2];

   assign s1_axi_rresp_o = demux_axi_rresp[1*2+:2];

   assign s0_axi_rvalid_o = demux_axi_rvalid[0*1+:1];

   assign s1_axi_rvalid_o = demux_axi_rvalid[1*1+:1];
   assign mux_axi_rready = {s1_axi_rready_i, s0_axi_rready_i};
   assign mux_axi_arid = {s1_axi_arid_i, s0_axi_arid_i};
   assign mux_axi_arlen = {s1_axi_arlen_i, s0_axi_arlen_i};
   assign mux_axi_arsize = {s1_axi_arsize_i, s0_axi_arsize_i};
   assign mux_axi_arburst = {s1_axi_arburst_i, s0_axi_arburst_i};
   assign mux_axi_arlock = {s1_axi_arlock_i, s0_axi_arlock_i};
   assign mux_axi_arcache = {s1_axi_arcache_i, s0_axi_arcache_i};
   assign mux_axi_arqos = {s1_axi_arqos_i, s0_axi_arqos_i};

   assign s0_axi_rid_o = demux_axi_rid[0*ID_W+:ID_W];

   assign s1_axi_rid_o = demux_axi_rid[1*ID_W+:ID_W];

   assign s0_axi_rlast_o = demux_axi_rlast[0*1+:1];

   assign s1_axi_rlast_o = demux_axi_rlast[1*1+:1];




endmodule
