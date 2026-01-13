`timescale 1ns / 1ps
`include "iob_xilinx_clock_wizard_conf.vh"

module iob_xilinx_clock_wizard #(
   parameter OUTPUT_PER = `IOB_XILINX_CLOCK_WIZARD_OUTPUT_PER,
   parameter INPUT_PER  = `IOB_XILINX_CLOCK_WIZARD_INPUT_PER
) (
   // clk_rst_i
   input  clk_p_i,
   input  clk_n_i,
   input  arst_i,
   // clk_rst_o
   output clk_out1_o,
   output rst_out1_o
);
   // reset_sync_clk_rst
   wire arst_out;


   // Default description
   iob_reset_sync rst_sync (
      // clk_rst_s port
      .clk_i (clk_out1_o),
      .arst_i(arst_out),
      // arst_o port
      .arst_o(rst_out1_o)
   );




   iob_clock_wizard #(
      .OUTPUT_PER(OUTPUT_PER),
      .INPUT_PER (INPUT_PER)
   ) clock_wizard_inst (
      .clk_in1_p(clk_p_i),
      .clk_in1_n(clk_n_i),
      .arst_i   (arst_i),
      .clk_out1 (clk_out1_o),
      .arst_out1(arst_out)
   );




endmodule
