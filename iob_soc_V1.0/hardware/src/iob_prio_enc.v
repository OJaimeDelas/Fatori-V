`timescale 1ns / 1ps
`include "iob_prio_enc_conf.vh"

module iob_prio_enc #(
   parameter W    = `IOB_PRIO_ENC_W,
   parameter MODE = `IOB_PRIO_ENC_MODE
) (
   // unencoded_i
   input      [        W-1:0] unencoded_i,
   // encoded_o
   output reg [$clog2(W)-1:0] encoded_o
);

   integer pos;
   generate
      if (MODE == "LOW") begin : gen_low_prio
         always @* begin
            encoded_o = {$clog2(W) {1'd0}};  //In case input is 0
            for (pos = W - 1; pos != -1; pos = pos - 1) begin
               if (unencoded_i[pos]) begin
                  encoded_o = pos[$clog2(W)-1:0];
               end
            end
         end
      end else begin : gen_highest_prio  //MODE == "HIGH"
         always @* begin
            encoded_o = {$clog2(W) {1'd0}};  //In case input is 0
            for (pos = 0; pos < W; pos = pos + 1) begin
               if (unencoded_i[pos]) begin
                  encoded_o = pos[$clog2(W)-1:0];
               end
            end
         end
      end
   endgenerate




endmodule
