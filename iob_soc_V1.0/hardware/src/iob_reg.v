`timescale 1ns / 1ps
`include "iob_reg_conf.vh"

module iob_reg #(
   parameter DATA_W  = `IOB_REG_DATA_W,
   parameter RST_VAL = `IOB_REG_RST_VAL
) (
   // clk_en_rst_s
   input                   clk_i,
   input                   cke_i,
   input                   arst_i,
   // data_i
   input      [DATA_W-1:0] data_i,
   // data_o
   output reg [DATA_W-1:0] data_o
);

   always @(posedge clk_i, posedge arst_i) begin
      if (arst_i) begin
         data_o <= RST_VAL;
      end else if (cke_i) begin
         data_o <= data_i;
      end
   end




endmodule
