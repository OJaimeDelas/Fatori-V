`timescale 1ns / 1ps
`include "iob_uart_csrs_conf.vh"

module iob_uart_csrs #(
   parameter ADDR_W = `IOB_UART_CSRS_ADDR_W,  // Don't change this parameter value!
   parameter DATA_W = `IOB_UART_CSRS_DATA_W
) (
   // clk_en_rst_s
   input                 clk_i,
   input                 cke_i,
   input                 arst_i,
   // control_if_s
   input                 iob_valid_i,
   input                 iob_addr_i,
   input  [  DATA_W-1:0] iob_wdata_i,
   input  [DATA_W/8-1:0] iob_wstrb_i,
   output                iob_rvalid_o,
   output [  DATA_W-1:0] iob_rdata_o,
   output                iob_ready_o,
   // softreset_o
   output                softreset_o,
   // div_o
   output [      16-1:0] div_o,
   // txdata_io
   output [       8-1:0] txdata_wdata_o,
   output                txdata_wen_o,
   input                 txdata_wready_i,
   // txen_o
   output                txen_o,
   // rxen_o
   output                rxen_o,
   // txready_i
   input                 txready_i,
   // rxready_i
   input                 rxready_i,
   // rxdata_io
   input  [       8-1:0] rxdata_rdata_i,
   input                 rxdata_rvalid_i,
   output                rxdata_ren_o,
   input                 rxdata_rready_i
);
   // internal_iob
   wire                internal_iob_valid;
   wire [  ADDR_W-1:0] internal_iob_addr;
   wire [  DATA_W-1:0] internal_iob_wdata;
   wire [DATA_W/8-1:0] internal_iob_wstrb;
   wire                internal_iob_rvalid;
   wire [  DATA_W-1:0] internal_iob_rdata;
   wire                internal_iob_ready;
   // state
   wire                state;
   // state_nxt
   reg                 state_nxt;
   // internal_iob_addr_stable
   wire [  ADDR_W-1:0] internal_iob_addr_stable;
   // internal_iob_addr_reg
   wire [  ADDR_W-1:0] internal_iob_addr_reg;
   // internal_iob_addr_reg_en
   wire                internal_iob_addr_reg_en;
   // softreset_wdata
   wire                softreset_wdata;
   // softreset_wen
   wire                softreset_wen;
   // div_wdata
   wire [      16-1:0] div_wdata;
   // div_wen
   wire                div_wen;
   // txdata_wdata
   wire [       8-1:0] txdata_wdata;
   // txen_wdata
   wire                txen_wdata;
   // txen_wen
   wire                txen_wen;
   // rxen_wdata
   wire                rxen_wdata;
   // rxen_wen
   wire                rxen_wen;
   // rvalid
   wire                rvalid;
   // rvalid_nxt
   reg                 rvalid_nxt;
   // rdata
   wire [      32-1:0] rdata;
   // rdata_nxt
   reg  [      32-1:0] rdata_nxt;
   // ready
   wire                ready;
   // ready_nxt
   reg                 ready_nxt;
   // rvalid_int
   reg                 rvalid_int;
   // wready_int
   reg                 wready_int;
   // rready_int
   reg                 rready_int;
   // iob_addr_i_0_0
   reg                 iob_addr_i_0_0;
   // iob_addr_i_0_8
   reg                 iob_addr_i_0_8;
   // iob_addr_i_4_0
   reg                 iob_addr_i_4_0;
   // iob_addr_i_4_16
   reg                 iob_addr_i_4_16;


   // store iob addr
   iob_reg_e #(
      .DATA_W (ADDR_W),
      .RST_VAL({ADDR_W{1'b0}})
   ) internal_addr_reg (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // en_i port
      .en_i  (internal_iob_addr_reg_en),
      // data_i port
      .data_i(internal_iob_addr),
      // data_o port
      .data_o(internal_iob_addr_reg)
   );

   // state register
   iob_reg #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) state_reg (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(state_nxt),
      // data_o port
      .data_o(state)
   );

   // rvalid register
   iob_reg #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) rvalid_reg (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(rvalid_nxt),
      // data_o port
      .data_o(rvalid)
   );

   // rdata register
   iob_reg #(
      .DATA_W (32),
      .RST_VAL(32'b0)
   ) rdata_reg (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(rdata_nxt),
      // data_o port
      .data_o(rdata)
   );

   // ready register
   iob_reg #(
      .DATA_W (1),
      .RST_VAL(1'b0)
   ) ready_reg (
      // clk_en_rst_s port
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      // data_i port
      .data_i(ready_nxt),
      // data_o port
      .data_o(ready)
   );




   // Include iob_functions for use in parameters
   // SPDX-FileCopyrightText: 2025 IObundle
   //
   // SPDX-License-Identifier: MIT

   function [31:0] iob_max;
      input [31:0] a;
      input [31:0] b;
      begin
         if (a > b) iob_max = a;
         else iob_max = b;
      end
   endfunction

   function [31:0] iob_min;
      input [31:0] a;
      input [31:0] b;
      begin
         if (a < b) iob_min = a;
         else iob_min = b;
      end
   endfunction

   function [31:0] iob_cshift_left;
      input [31:0] DATA;
      input integer DATA_W;
      input integer SHIFT;
      begin
         iob_cshift_left = (DATA << SHIFT) | (DATA >> (DATA_W - SHIFT));
      end
   endfunction

   function [31:0] iob_cshift_right;
      input [31:0] DATA;
      input integer DATA_W;
      input integer SHIFT;
      begin
         iob_cshift_right = (DATA >> SHIFT) | (DATA << (DATA_W - SHIFT));
      end
   endfunction
   `define IOB_NBYTES (DATA_W/8)
   `define IOB_NBYTES_W $clog2(`IOB_NBYTES)
   `define IOB_WORD_ADDR(ADDR) ((ADDR>>`IOB_NBYTES_W)<<`IOB_NBYTES_W)


   localparam WSTRB_W = DATA_W / 8;

   //FSM states
   localparam WAIT_REQ = 1'd0;
   localparam WAIT_RVALID = 1'd1;

   assign internal_iob_addr_reg_en = (state == WAIT_REQ);
   assign internal_iob_addr_stable = (state == WAIT_RVALID) ? internal_iob_addr_reg : internal_iob_addr;

   assign internal_iob_valid = iob_valid_i;
   assign internal_iob_addr = {iob_addr_i, 2'b0};
   assign internal_iob_wdata = iob_wdata_i;
   assign internal_iob_wstrb = iob_wstrb_i;
   assign iob_rvalid_o = internal_iob_rvalid;
   assign iob_rdata_o = internal_iob_rdata;
   assign iob_ready_o = internal_iob_ready;

   //write address
   wire [($clog2(WSTRB_W)+1)-1:0] byte_offset;
   iob_ctls #(
      .W     (WSTRB_W),
      .MODE  (0),
      .SYMBOL(0)
   ) bo_inst (
      .data_i (internal_iob_wstrb),
      .count_o(byte_offset)
   );
   wire [ADDR_W-1:0] waddr;
   assign waddr           = `IOB_WORD_ADDR(internal_iob_addr_stable) + byte_offset;


   //NAME: softreset;
   //TYPE: W; WIDTH: 1; RST_VAL: 0; ADDR: 0; SPACE (bytes): 1 (max); AUTO: True

   assign softreset_wdata = internal_iob_wdata[0+:1];
   wire softreset_addressed_w;
   assign softreset_addressed_w = (waddr >= 0) && (waddr < 1);
   assign softreset_wen = (internal_iob_valid & internal_iob_ready) & ((|internal_iob_wstrb) & softreset_addressed_w);
   iob_reg_e #(
      .DATA_W (1),
      .RST_VAL({1{1'd0}})
   ) softreset_datareg (
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      .en_i  (softreset_wen),
      .data_i(softreset_wdata),
      .data_o(softreset_o)
   );



   //NAME: div;
   //TYPE: W; WIDTH: 16; RST_VAL: 0; ADDR: 2; SPACE (bytes): 2 (max); AUTO: True

   assign div_wdata = internal_iob_wdata[16+:16];
   wire div_addressed_w;
   assign div_addressed_w = (waddr >= 2) && (waddr < 4);
   assign div_wen = (internal_iob_valid & internal_iob_ready) & ((|internal_iob_wstrb) & div_addressed_w);
   iob_reg_e #(
      .DATA_W (16),
      .RST_VAL({16{1'd0}})
   ) div_datareg (
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      .en_i  (div_wen),
      .data_i(div_wdata),
      .data_o(div_o)
   );



   //NAME: txdata;
   //TYPE: W; WIDTH: 8; RST_VAL: 0; ADDR: 4; SPACE (bytes): 1 (max); AUTO: False

   assign txdata_wdata = internal_iob_wdata[0+:8];
   wire txdata_addressed_w;
   assign txdata_addressed_w = (waddr >= 4) && (waddr < 5);
   assign txdata_wen_o = (txdata_addressed_w & internal_iob_valid) ? |internal_iob_wstrb : 1'b0;
   assign txdata_wdata_o = txdata_wdata;


   //NAME: txen;
   //TYPE: W; WIDTH: 1; RST_VAL: 0; ADDR: 5; SPACE (bytes): 1 (max); AUTO: True

   assign txen_wdata = internal_iob_wdata[8+:1];
   wire txen_addressed_w;
   assign txen_addressed_w = (waddr >= 5) && (waddr < 6);
   assign txen_wen = (internal_iob_valid & internal_iob_ready) & ((|internal_iob_wstrb) & txen_addressed_w);
   iob_reg_e #(
      .DATA_W (1),
      .RST_VAL({1{1'd0}})
   ) txen_datareg (
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      .en_i  (txen_wen),
      .data_i(txen_wdata),
      .data_o(txen_o)
   );



   //NAME: rxen;
   //TYPE: W; WIDTH: 1; RST_VAL: 0; ADDR: 6; SPACE (bytes): 1 (max); AUTO: True

   assign rxen_wdata = internal_iob_wdata[16+:1];
   wire rxen_addressed_w;
   assign rxen_addressed_w = (waddr >= 6) && (waddr < 7);
   assign rxen_wen = (internal_iob_valid & internal_iob_ready) & ((|internal_iob_wstrb) & rxen_addressed_w);
   iob_reg_e #(
      .DATA_W (1),
      .RST_VAL({1{1'd0}})
   ) rxen_datareg (
      .clk_i (clk_i),
      .cke_i (cke_i),
      .arst_i(arst_i),
      .en_i  (rxen_wen),
      .data_i(rxen_wdata),
      .data_o(rxen_o)
   );



   //NAME: txready;
   //TYPE: R; WIDTH: 1; RST_VAL: 0; ADDR: 0; SPACE (bytes): 1 (max); AUTO: True



   //NAME: rxready;
   //TYPE: R; WIDTH: 1; RST_VAL: 0; ADDR: 1; SPACE (bytes): 1 (max); AUTO: True



   //NAME: rxdata;
   //TYPE: R; WIDTH: 8; RST_VAL: 0; ADDR: 4; SPACE (bytes): 1 (max); AUTO: False

   wire rxdata_addressed_r;
   assign rxdata_addressed_r = (internal_iob_addr_stable >= 4) && (internal_iob_addr_stable < (4+(2**(0))));
   assign rxdata_ren_o = rxdata_addressed_r & internal_iob_valid & (~|internal_iob_wstrb);


   //NAME: version;
   //TYPE: R; WIDTH: 16; RST_VAL: 0081; ADDR: 6; SPACE (bytes): 2 (max); AUTO: True



   //RESPONSE SWITCH


   assign internal_iob_rvalid = rvalid;
   assign internal_iob_rdata = rdata;
   assign internal_iob_ready = ready;

   wire [7:0] byte_aligned_txready_i;
   assign byte_aligned_txready_i = txready_i;
   wire [7:0] byte_aligned_rxready_i;
   assign byte_aligned_rxready_i = rxready_i;
   wire [7:0] byte_aligned_rxdata_rdata_i;
   assign byte_aligned_rxdata_rdata_i = rxdata_rdata_i;

   always @* begin
      rdata_nxt      = 32'd0;
      rvalid_int     = (internal_iob_valid & internal_iob_ready) & (~(|internal_iob_wstrb));
      rready_int     = 1'b1;
      wready_int     = 1'b1;

      iob_addr_i_0_0 = (`IOB_WORD_ADDR(internal_iob_addr_stable) == 0);
      if (iob_addr_i_0_0) begin
         rdata_nxt[0+:8] = byte_aligned_txready_i | 8'd0;
      end

      iob_addr_i_0_8 = (`IOB_WORD_ADDR(internal_iob_addr_stable) == 0);
      if (iob_addr_i_0_8) begin
         rdata_nxt[8+:8] = byte_aligned_rxready_i | 8'd0;
      end

      iob_addr_i_4_0 = (`IOB_WORD_ADDR(internal_iob_addr_stable) == 4);
      if (iob_addr_i_4_0) begin

         rdata_nxt[0+:8] = byte_aligned_rxdata_rdata_i | 8'd0;
         rvalid_int      = rxdata_rvalid_i;
         rready_int      = rxdata_rready_i;
      end

      iob_addr_i_4_16 = ((
      `IOB_WORD_ADDR(internal_iob_addr_stable)
      >= 4) && (
      `IOB_WORD_ADDR(internal_iob_addr_stable)
      < 8));
      if (iob_addr_i_4_16) begin
         rdata_nxt[16+:16] = 16'h0081 | 16'd0;
      end

      if ((waddr >= 4) && (waddr < 5)) begin
         wready_int = txdata_wready_i;
      end


      // ######  FSM  #############

      //FSM default values
      ready_nxt  = 1'b0;
      rvalid_nxt = 1'b0;
      state_nxt  = state;

      //FSM state machine
      case (state)
         WAIT_REQ: begin
            if (internal_iob_valid & (!internal_iob_ready)) begin  // Wait for a valid request
               ready_nxt = |internal_iob_wstrb ? wready_int : rready_int;
               // If is read and ready, go to WAIT_RVALID
               if (ready_nxt && (!(|internal_iob_wstrb))) begin
                  state_nxt = WAIT_RVALID;
               end
            end
         end

         default: begin  // WAIT_RVALID
            if (rvalid_int) begin
               rvalid_nxt = 1'b1;
               state_nxt  = WAIT_REQ;
            end
         end
      endcase

   end  //always @*





endmodule
