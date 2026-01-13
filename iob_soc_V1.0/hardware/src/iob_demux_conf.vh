`define IOB_DEMUX_DATA_W 21
`define IOB_DEMUX_N 21
`define IOB_DEMUX_SEL_W ($clog2(N) == 0 ? 1 : $clog2(N))
`define IOB_DEMUX_VERSION 16'h0081
