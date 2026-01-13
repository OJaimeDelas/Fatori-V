`timescale 1ns / 1ps
`include "iob_r_conf.vh"

module iob_r #(
   parameter DATA_W  = `IOB_R_DATA_W,
   parameter RST_VAL = `IOB_R_RST_VAL
) (
   // clk_rst_s
   input                   clk_i,
   input                   arst_i,
   // iob_r_data_i
   input      [DATA_W-1:0] iob_r_data_i,
   // iob_r_data_o
   output reg [DATA_W-1:0] iob_r_data_o
);

   always @(posedge clk_i, posedge arst_i) begin
      if (arst_i) begin
         iob_r_data_o <= RST_VAL;
      end else begin
         iob_r_data_o <= iob_r_data_i;
      end
   end




endmodule
