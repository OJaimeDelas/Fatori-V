`timescale 1ns / 1ps
`include "iob_ram_t2p_conf.vh"

module iob_ram_t2p #(
   parameter HEXFILE = `IOB_RAM_T2P_HEXFILE,
   parameter ADDR_W = `IOB_RAM_T2P_ADDR_W,
   parameter DATA_W = `IOB_RAM_T2P_DATA_W,
   parameter MEM_INIT_FILE_INT =
   `IOB_RAM_T2P_MEM_INIT_FILE_INT  // Don't change this parameter value!
) (
   // clk_i
   input               clk_i,
   // w_en_i
   input               w_en_i,
   // w_addr_i
   input  [ADDR_W-1:0] w_addr_i,
   // w_data_i
   input  [DATA_W-1:0] w_data_i,
   // r_en_i
   input               r_en_i,
   // r_addr_i
   input  [ADDR_W-1:0] r_addr_i,
   // r_data_o
   output [DATA_W-1:0] r_data_o
);




   localparam INIT_RAM = (MEM_INIT_FILE_INT != "none") ? 1 : 0;
   // Declare the RAM
   reg [DATA_W-1:0] mem    [(2**ADDR_W)-1:0];

   reg [DATA_W-1:0] r_data;
   // Initialize the RAM
   generate
      if (INIT_RAM) begin : mem_init
         initial $readmemh(MEM_INIT_FILE_INT, mem, 0, (2 ** ADDR_W) - 1);
      end
   endgenerate

   //read port
   always @(posedge clk_i) begin
      if (r_en_i) begin
         r_data <= mem[r_addr_i];
      end
   end

   //write port
   always @(posedge clk_i) begin
      if (w_en_i) begin
         mem[w_addr_i] <= w_data_i;
      end
   end

   assign r_data_o = r_data;




endmodule
