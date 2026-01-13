`timescale 1ns / 1ps
`include "iob_clock_conf.vh"

module iob_clock #(
   parameter CLK_PERIOD = `IOB_CLOCK_CLK_PERIOD
) (
   // clk_o
   output clk_o
);

   reg clk;
   assign clk_o = clk;
   initial clk = 0;
   always #(CLK_PERIOD / 2) clk = ~clk;




endmodule
