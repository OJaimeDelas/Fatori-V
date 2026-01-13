`timescale 1ns / 1ps
`include "iob_uart_conf.vh"

module iob_uart #(
   parameter DATA_W = `IOB_UART_DATA_W
) (
   // clk_en_rst_s
   input                 clk_i,
   input                 cke_i,
   input                 arst_i,
   // rs232_m
   input                 rs232_rxd_i,
   output                rs232_txd_o,
   output                rs232_rts_o,
   input                 rs232_cts_i,
   // iob_csrs_cbus_s
   input                 iob_csrs_iob_valid_i,
   input                 iob_csrs_iob_addr_i,
   input  [  DATA_W-1:0] iob_csrs_iob_wdata_i,
   input  [DATA_W/8-1:0] iob_csrs_iob_wstrb_i,
   output                iob_csrs_iob_rvalid_o,
   output [  DATA_W-1:0] iob_csrs_iob_rdata_o,
   output                iob_csrs_iob_ready_o
);
   // softreset
   wire          softreset_wr;
   // div
   wire [16-1:0] div_wr;
   // txdata
   wire [ 8-1:0] txdata_wdata_wr;
   wire          txdata_wen_wr;
   wire          txdata_wready_wr;
   // txen
   wire          txen_wr;
   // rxen
   wire          rxen_wr;
   // txready
   wire          txready_rd;
   // rxready
   wire          rxready_rd;
   // rxdata
   wire [ 8-1:0] rxdata_rdata_rd;
   wire          rxdata_rvalid_rd;
   wire          rxdata_ren_rd;
   wire          rxdata_rready_rd;
   // iob_reg_rvalid_data_i
   wire          rxdata_rvalid_nxt;


   // Control/Status Registers
   iob_uart_csrs iob_csrs (
      // clk_en_rst_s port
      .clk_i          (clk_i),
      .cke_i          (cke_i),
      .arst_i         (arst_i),
      // control_if_s port
      .iob_valid_i    (iob_csrs_iob_valid_i),
      .iob_addr_i     (iob_csrs_iob_addr_i),
      .iob_wdata_i    (iob_csrs_iob_wdata_i),
      .iob_wstrb_i    (iob_csrs_iob_wstrb_i),
      .iob_rvalid_o   (iob_csrs_iob_rvalid_o),
      .iob_rdata_o    (iob_csrs_iob_rdata_o),
      .iob_ready_o    (iob_csrs_iob_ready_o),
      // softreset_o port
      .softreset_o    (softreset_wr),
      // div_o port
      .div_o          (div_wr),
      // txdata_io port
      .txdata_wdata_o (txdata_wdata_wr),
      .txdata_wen_o   (txdata_wen_wr),
      .txdata_wready_i(txdata_wready_wr),
      // txen_o port
      .txen_o         (txen_wr),
      // rxen_o port
      .rxen_o         (rxen_wr),
      // txready_i port
      .txready_i      (txready_rd),
      // rxready_i port
      .rxready_i      (rxready_rd),
      // rxdata_io port
      .rxdata_rdata_i (rxdata_rdata_rd),
      .rxdata_rvalid_i(rxdata_rvalid_rd),
      .rxdata_ren_o   (rxdata_ren_rd),
      .rxdata_rready_i(rxdata_rready_rd)
   );

   // Register for rxdata rvalid
   iob_reg #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) iob_reg_rvalid (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(rxdata_rvalid_nxt),
      // data_o port
      .data_o(rxdata_rvalid_rd)
   );

   // UART core driver
   iob_uart_core iob_uart_core_inst (
      // clk_rst_s port
      .clk_i          (clk_i),
      .arst_i         (arst_i),
      // reg_interface_io port
      .rst_soft_i     (softreset_wr),
      .tx_en_i        (txen_wr),
      .rx_en_i        (rxen_wr),
      .tx_ready_o     (txready_rd),
      .rx_ready_o     (rxready_rd),
      .tx_data_i      (txdata_wdata_wr),
      .rx_data_o      (rxdata_rdata_rd),
      .data_write_en_i(txdata_wen_wr),
      .data_read_en_i (rxdata_ren_rd),
      .bit_duration_i (div_wr),
      // rs232_m port
      .rs232_rxd_i    (rs232_rxd_i),
      .rs232_txd_o    (rs232_txd_o),
      .rs232_rts_o    (rs232_rts_o),
      .rs232_cts_i    (rs232_cts_i)
   );




   // txdata Manual logic
   assign txdata_wready_wr  = 1'b1;

   // rxdata Manual logic
   assign rxdata_rready_rd  = 1'b1;

   // rxdata rvalid is iob_valid registered
   assign rxdata_rvalid_nxt = rxdata_ren_rd;




endmodule
