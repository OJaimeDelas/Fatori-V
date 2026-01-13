`timescale 1ns / 1ps
`include "iob_reg_r_conf.vh"

module iob_reg_r #(
   parameter DATA_W  = `IOB_REG_R_DATA_W,
   parameter RST_VAL = `IOB_REG_R_RST_VAL
) (
   // clk_en_rst_s
   input               clk_i,
   input               cke_i,
   input               arst_i,
   // rst_i
   input               rst_i,
   // data_i
   input  [DATA_W-1:0] data_i,
   // data_o
   output [DATA_W-1:0] data_o
);
   // data_next
   wire [DATA_W-1:0] data_next;


   // Default description
   iob_reg #(
      .DATA_W (DATA_W),
      .RST_VAL(RST_VAL)
   ) iob_reg_inst (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(data_next),
      // data_o port
      .data_o(data_o)
   );




   assign data_next = rst_i ? RST_VAL : data_i;




endmodule
