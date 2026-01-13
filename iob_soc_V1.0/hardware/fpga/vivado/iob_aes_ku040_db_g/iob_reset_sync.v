`timescale 1ns / 1ps
`include "iob_reset_sync_conf.vh"

module iob_reset_sync (
   // clk_rst_s
   input  clk_i,
   input  arst_i,
   // arst_o
   output arst_o
);
   // data_int
   wire [2-1:0] data_int;
   // sync
   wire [2-1:0] sync;


   // Default description
   iob_r #(
      .DATA_W (2),
      .RST_VAL(2'd3)
   ) reg1 (
      // clk_rst_s port
      .clk_i       (clk_i),
      .arst_i      (arst_i),
      // iob_r_data_i port
      .iob_r_data_i(data_int),
      // iob_r_data_o port
      .iob_r_data_o(sync)
   );




   assign data_int = {sync[0], 1'b0};
   assign arst_o   = sync[1];




endmodule
