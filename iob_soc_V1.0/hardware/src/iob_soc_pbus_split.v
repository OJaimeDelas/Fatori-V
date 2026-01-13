`timescale 1ns / 1ps
`include "iob_soc_pbus_split_conf.vh"

module iob_soc_pbus_split (
   // clk_en_rst_s
   input           clk_i,
   input           cke_i,
   input           arst_i,
   // reset_i
   input           rst_i,
   // input_s
   input           input_iob_valid_i,
   input  [28-1:0] input_iob_addr_i,
   input  [32-1:0] input_iob_wdata_i,
   input  [ 4-1:0] input_iob_wstrb_i,
   output          input_iob_rvalid_o,
   output [32-1:0] input_iob_rdata_o,
   output          input_iob_ready_o,
   // output_0_m
   output          output0_iob_valid_o,
   output [26-1:0] output0_iob_addr_o,
   output [32-1:0] output0_iob_wdata_o,
   output [ 4-1:0] output0_iob_wstrb_o,
   input           output0_iob_rvalid_i,
   input  [32-1:0] output0_iob_rdata_i,
   input           output0_iob_ready_i,
   // output_1_m
   output          output1_iob_valid_o,
   output [26-1:0] output1_iob_addr_o,
   output [32-1:0] output1_iob_wdata_o,
   output [ 4-1:0] output1_iob_wstrb_o,
   input           output1_iob_rvalid_i,
   input  [32-1:0] output1_iob_rdata_i,
   input           output1_iob_ready_i,
   // output_2_m
   output          output2_iob_valid_o,
   output [26-1:0] output2_iob_addr_o,
   output [32-1:0] output2_iob_wdata_o,
   output [ 4-1:0] output2_iob_wstrb_o,
   input           output2_iob_rvalid_i,
   input  [32-1:0] output2_iob_rdata_i,
   input           output2_iob_ready_i,
   // output_3_m
   output          output3_iob_valid_o,
   output [26-1:0] output3_iob_addr_o,
   output [32-1:0] output3_iob_wdata_o,
   output [ 4-1:0] output3_iob_wstrb_o,
   input           output3_iob_rvalid_i,
   input  [32-1:0] output3_iob_rdata_i,
   input           output3_iob_ready_i
);
   // sel_reg_data_i
   wire [  2-1:0] sel;
   // sel_reg_data_o
   wire [  2-1:0] sel_reg;
   // demux_valid_data_o
   wire [  4-1:0] demux_valid_output;
   // demux_addr_data_o
   wire [112-1:0] demux_addr_output;
   // demux_wdata_data_o
   wire [128-1:0] demux_wdata_output;
   // demux_wstrb_data_o
   wire [ 16-1:0] demux_wstrb_output;
   // mux_rdata_data_i
   wire [128-1:0] mux_rdata_input;
   // mux_rvalid_data_i
   wire [  4-1:0] mux_rvalid_input;
   // mux_ready_data_i
   wire [  4-1:0] mux_ready_input;


   // Default description
   iob_reg_re #(
      .DATA_W (2),
      .RST_VAL(2'b0)
   ) sel_reg_re (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_rst_i port
      .en_i  (input_iob_valid_i),
      .rst_i (rst_i),
      // data_i port
      .data_i(sel),
      // data_o port
      .data_o(sel_reg)
   );

   // Default description
   iob_demux #(
      .DATA_W(1),
      .N     (4)
   ) iob_demux_valid (
      // sel_i port
      .sel_i (sel),
      // data_i port
      .data_i(input_iob_valid_i),
      // data_o port
      .data_o(demux_valid_output)
   );

   // Default description
   iob_demux #(
      .DATA_W(28),
      .N     (4)
   ) iob_demux_addr (
      // sel_i port
      .sel_i (sel),
      // data_i port
      .data_i(input_iob_addr_i),
      // data_o port
      .data_o(demux_addr_output)
   );

   // Default description
   iob_demux #(
      .DATA_W(32),
      .N     (4)
   ) iob_demux_wdata (
      // sel_i port
      .sel_i (sel),
      // data_i port
      .data_i(input_iob_wdata_i),
      // data_o port
      .data_o(demux_wdata_output)
   );

   // Default description
   iob_demux #(
      .DATA_W(4),
      .N     (4)
   ) iob_demux_wstrb (
      // sel_i port
      .sel_i (sel),
      // data_i port
      .data_i(input_iob_wstrb_i),
      // data_o port
      .data_o(demux_wstrb_output)
   );

   // Default description
   iob_mux #(
      .DATA_W(32),
      .N     (4)
   ) iob_mux_rdata (
      // sel_i port
      .sel_i (sel_reg),
      // data_i port
      .data_i(mux_rdata_input),
      // data_o port
      .data_o(input_iob_rdata_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (4)
   ) iob_mux_rvalid (
      // sel_i port
      .sel_i (sel_reg),
      // data_i port
      .data_i(mux_rvalid_input),
      // data_o port
      .data_o(input_iob_rvalid_o)
   );

   // Default description
   iob_mux #(
      .DATA_W(1),
      .N     (4)
   ) iob_mux_ready (
      // sel_i port
      .sel_i (sel),
      // data_i port
      .data_i(mux_ready_input),
      // data_o port
      .data_o(input_iob_ready_o)
   );



   assign sel = input_iob_addr_i[27-:2];

   assign output0_iob_valid_o = demux_valid_output[0+:1];
   assign output0_iob_addr_o = demux_addr_output[0+:26];
   assign output0_iob_wdata_o = demux_wdata_output[0+:32];
   assign output0_iob_wstrb_o = demux_wstrb_output[0+:4];

   assign output1_iob_valid_o = demux_valid_output[1+:1];
   assign output1_iob_addr_o = demux_addr_output[28+:26];
   assign output1_iob_wdata_o = demux_wdata_output[32+:32];
   assign output1_iob_wstrb_o = demux_wstrb_output[4+:4];

   assign output2_iob_valid_o = demux_valid_output[2+:1];
   assign output2_iob_addr_o = demux_addr_output[56+:26];
   assign output2_iob_wdata_o = demux_wdata_output[64+:32];
   assign output2_iob_wstrb_o = demux_wstrb_output[8+:4];

   assign output3_iob_valid_o = demux_valid_output[3+:1];
   assign output3_iob_addr_o = demux_addr_output[84+:26];
   assign output3_iob_wdata_o = demux_wdata_output[96+:32];
   assign output3_iob_wstrb_o = demux_wstrb_output[12+:4];

   assign mux_rdata_input = {
      output3_iob_rdata_i, output2_iob_rdata_i, output1_iob_rdata_i, output0_iob_rdata_i
   };
   assign mux_rvalid_input = {
      output3_iob_rvalid_i, output2_iob_rvalid_i, output1_iob_rvalid_i, output0_iob_rvalid_i
   };
   assign mux_ready_input = {
      output3_iob_ready_i, output2_iob_ready_i, output1_iob_ready_i, output0_iob_ready_i
   };




endmodule
