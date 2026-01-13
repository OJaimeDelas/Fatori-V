`timescale 1ns / 1ps
`include "iob_system_tester_conf.vh"

module iob_system_tester #(
   parameter AXI_ID_W = `IOB_SYSTEM_TESTER_AXI_ID_W,  // Don't change this parameter value!
   parameter AXI_ADDR_W = `IOB_SYSTEM_TESTER_AXI_ADDR_W,  // Don't change this parameter value!
   parameter AXI_DATA_W = `IOB_SYSTEM_TESTER_AXI_DATA_W,  // Don't change this parameter value!
   parameter AXI_LEN_W = `IOB_SYSTEM_TESTER_AXI_LEN_W,  // Don't change this parameter value!
   parameter BOOTROM_MEM_HEXFILE = `IOB_SYSTEM_TESTER_BOOTROM_MEM_HEXFILE,  // Don't change this parameter value!
   parameter EXT_MEM_HEXFILE =
   `IOB_SYSTEM_TESTER_EXT_MEM_HEXFILE  // Don't change this parameter value!
) (
   // clk_en_rst_s
   input                     clk_i,
   input                     cke_i,
   input                     arst_i,
   // rs232_m
   input                     rs232_rxd_i,
   output                    rs232_txd_o,
   output                    rs232_rts_o,
   input                     rs232_cts_i,
   // iob_s
   input                     iob_valid_i,
   input  [AXI_ADDR_W-2-1:0] iob_addr_i,
   input  [  AXI_DATA_W-1:0] iob_wdata_i,
   input  [AXI_DATA_W/8-1:0] iob_wstrb_i,
   output                    iob_rvalid_o,
   output [  AXI_DATA_W-1:0] iob_rdata_o,
   output                    iob_ready_o
);
   // interrupts
   wire [          32-1:0] interrupts;
   // iob_periphs_cbus
   wire                    periphs_iob_valid;
   wire [          30-1:0] periphs_iob_addr;
   wire [  AXI_DATA_W-1:0] periphs_iob_wdata;
   wire [AXI_DATA_W/8-1:0] periphs_iob_wstrb;
   wire                    periphs_iob_rvalid;
   wire [  AXI_DATA_W-1:0] periphs_iob_rdata;
   wire                    periphs_iob_ready;
   // sut_rs232
   wire                    sut_rs232_rxd;
   wire                    sut_rs232_txd;
   wire                    sut_rs232_rts;
   wire                    sut_rs232_cts;
   // uart0_cbus
   wire                    uart0_cbus_iob_valid;
   wire [          25-1:0] uart0_cbus_iob_addr;
   wire [          32-1:0] uart0_cbus_iob_wdata;
   wire [           4-1:0] uart0_cbus_iob_wstrb;
   wire                    uart0_cbus_iob_rvalid;
   wire [          32-1:0] uart0_cbus_iob_rdata;
   wire                    uart0_cbus_iob_ready;
   // timer0_cbus
   wire                    timer0_cbus_iob_valid;
   wire [          25-1:0] timer0_cbus_iob_addr;
   wire [          32-1:0] timer0_cbus_iob_wdata;
   wire [           4-1:0] timer0_cbus_iob_wstrb;
   wire                    timer0_cbus_iob_rvalid;
   wire [          32-1:0] timer0_cbus_iob_rdata;
   wire                    timer0_cbus_iob_ready;
   // uart1_cbus
   wire                    uart1_cbus_iob_valid;
   wire [          25-1:0] uart1_cbus_iob_addr;
   wire [          32-1:0] uart1_cbus_iob_wdata;
   wire [           4-1:0] uart1_cbus_iob_wstrb;
   wire                    uart1_cbus_iob_rvalid;
   wire [          32-1:0] uart1_cbus_iob_rdata;
   wire                    uart1_cbus_iob_ready;
   // clint_cbus
   wire                    clint_cbus_iob_valid;
   wire [          25-1:0] clint_cbus_iob_addr;
   wire [          32-1:0] clint_cbus_iob_wdata;
   wire [           4-1:0] clint_cbus_iob_wstrb;
   wire                    clint_cbus_iob_rvalid;
   wire [          32-1:0] clint_cbus_iob_rdata;
   wire                    clint_cbus_iob_ready;
   // plic_cbus
   wire                    plic_cbus_iob_valid;
   wire [          25-1:0] plic_cbus_iob_addr;
   wire [          32-1:0] plic_cbus_iob_wdata;
   wire [           4-1:0] plic_cbus_iob_wstrb;
   wire                    plic_cbus_iob_rvalid;
   wire [          32-1:0] plic_cbus_iob_rdata;
   wire                    plic_cbus_iob_ready;


   // Split between peripherals
   iob_system_tester_pbus_split iob_pbus_split (
      // clk_en_rst_s port
      .clk_i               (clk_i),
      .cke_i               (cke_i),
      .arst_i              (arst_i),
      // reset_i port
      .rst_i               (arst_i),
      // input_s port
      .input_iob_valid_i   (iob_valid_i),
      .input_iob_addr_i    (iob_addr_i),
      .input_iob_wdata_i   (iob_wdata_i),
      .input_iob_wstrb_i   (iob_wstrb_i),
      .input_iob_rvalid_o  (iob_rvalid_o),
      .input_iob_rdata_o   (iob_rdata_o),
      .input_iob_ready_o   (iob_ready_o),
      // output_0_m port
      .output0_iob_valid_o (uart0_cbus_iob_valid),
      .output0_iob_addr_o  (uart0_cbus_iob_addr),
      .output0_iob_wdata_o (uart0_cbus_iob_wdata),
      .output0_iob_wstrb_o (uart0_cbus_iob_wstrb),
      .output0_iob_rvalid_i(uart0_cbus_iob_rvalid),
      .output0_iob_rdata_i (uart0_cbus_iob_rdata),
      .output0_iob_ready_i (uart0_cbus_iob_ready),
      // output_1_m port
      .output1_iob_valid_o (timer0_cbus_iob_valid),
      .output1_iob_addr_o  (timer0_cbus_iob_addr),
      .output1_iob_wdata_o (timer0_cbus_iob_wdata),
      .output1_iob_wstrb_o (timer0_cbus_iob_wstrb),
      .output1_iob_rvalid_i(timer0_cbus_iob_rvalid),
      .output1_iob_rdata_i (timer0_cbus_iob_rdata),
      .output1_iob_ready_i (timer0_cbus_iob_ready),
      // output_2_m port
      .output2_iob_valid_o (uart1_cbus_iob_valid),
      .output2_iob_addr_o  (uart1_cbus_iob_addr),
      .output2_iob_wdata_o (uart1_cbus_iob_wdata),
      .output2_iob_wstrb_o (uart1_cbus_iob_wstrb),
      .output2_iob_rvalid_i(uart1_cbus_iob_rvalid),
      .output2_iob_rdata_i (uart1_cbus_iob_rdata),
      .output2_iob_ready_i (uart1_cbus_iob_ready),
      // output_3_m port
      .output3_iob_valid_o (clint_cbus_iob_valid),
      .output3_iob_addr_o  (clint_cbus_iob_addr),
      .output3_iob_wdata_o (clint_cbus_iob_wdata),
      .output3_iob_wstrb_o (clint_cbus_iob_wstrb),
      .output3_iob_rvalid_i(clint_cbus_iob_rvalid),
      .output3_iob_rdata_i (clint_cbus_iob_rdata),
      .output3_iob_ready_i (clint_cbus_iob_ready),
      // output_4_m port
      .output4_iob_valid_o (plic_cbus_iob_valid),
      .output4_iob_addr_o  (plic_cbus_iob_addr),
      .output4_iob_wdata_o (plic_cbus_iob_wdata),
      .output4_iob_wstrb_o (plic_cbus_iob_wstrb),
      .output4_iob_rvalid_i(plic_cbus_iob_rvalid),
      .output4_iob_rdata_i (plic_cbus_iob_rdata),
      .output4_iob_ready_i (plic_cbus_iob_ready)
   );

   // UART peripheral
   iob_uart UART0 (
      // clk_en_rst_s port
      .clk_i                (clk_i),
      .cke_i                (cke_i),
      .arst_i               (arst_i),
      // rs232_m port
      .rs232_rxd_i          (rs232_rxd_i),
      .rs232_txd_o          (rs232_txd_o),
      .rs232_rts_o          (rs232_rts_o),
      .rs232_cts_i          (rs232_cts_i),
      // iob_csrs_cbus_s port
      .iob_csrs_iob_valid_i (uart0_cbus_iob_valid),
      .iob_csrs_iob_addr_i  (uart0_cbus_iob_addr[1-1:0]),
      .iob_csrs_iob_wdata_i (uart0_cbus_iob_wdata),
      .iob_csrs_iob_wstrb_i (uart0_cbus_iob_wstrb),
      .iob_csrs_iob_rvalid_o(uart0_cbus_iob_rvalid),
      .iob_csrs_iob_rdata_o (uart0_cbus_iob_rdata),
      .iob_csrs_iob_ready_o (uart0_cbus_iob_ready)
   );

   // Timer peripheral
   iob_timer TIMER0 (
      // clk_en_rst_s port
      .clk_i                (clk_i),
      .cke_i                (cke_i),
      .arst_i               (arst_i),
      // iob_csrs_cbus_s port
      .iob_csrs_iob_valid_i (timer0_cbus_iob_valid),
      .iob_csrs_iob_addr_i  (timer0_cbus_iob_addr[2-1:0]),
      .iob_csrs_iob_wdata_i (timer0_cbus_iob_wdata),
      .iob_csrs_iob_wstrb_i (timer0_cbus_iob_wstrb),
      .iob_csrs_iob_rvalid_o(timer0_cbus_iob_rvalid),
      .iob_csrs_iob_rdata_o (timer0_cbus_iob_rdata),
      .iob_csrs_iob_ready_o (timer0_cbus_iob_ready)
   );

   // UART peripheral for communication with SUT.
   iob_uart UART1 (
      // clk_en_rst_s port
      .clk_i                (clk_i),
      .cke_i                (cke_i),
      .arst_i               (arst_i),
      // rs232_m port
      .rs232_rxd_i          (sut_rs232_txd),
      .rs232_txd_o          (sut_rs232_rxd),
      .rs232_rts_o          (sut_rs232_cts),
      .rs232_cts_i          (sut_rs232_rts),
      // iob_csrs_cbus_s port
      .iob_csrs_iob_valid_i (uart1_cbus_iob_valid),
      .iob_csrs_iob_addr_i  (uart1_cbus_iob_addr[1-1:0]),
      .iob_csrs_iob_wdata_i (uart1_cbus_iob_wdata),
      .iob_csrs_iob_wstrb_i (uart1_cbus_iob_wstrb),
      .iob_csrs_iob_rvalid_o(uart1_cbus_iob_rvalid),
      .iob_csrs_iob_rdata_o (uart1_cbus_iob_rdata),
      .iob_csrs_iob_ready_o (uart1_cbus_iob_ready)
   );

   // Default description
   iob_soc_mwrap #(
      .AXI_ID_W  (AXI_ID_W),
      .AXI_LEN_W (AXI_LEN_W),
      .AXI_ADDR_W(AXI_ADDR_W),
      .AXI_DATA_W(AXI_DATA_W)
   ) iob_soc_memwrapper (
      // clk_en_rst_s port
      .clk_i      (clk_i),
      .cke_i      (cke_i),
      .arst_i     (arst_i),
      // rs232_m port
      .rs232_rxd_i(sut_rs232_rxd),
      .rs232_txd_o(sut_rs232_txd),
      .rs232_rts_o(sut_rs232_rts),
      .rs232_cts_i(sut_rs232_cts)
   );




   //assign interrupts = {{30{1'b0}}, uart_interrupt_o, 1'b0};
   assign interrupts = {{30{1'b0}}, 1'b0, 1'b0};




endmodule
