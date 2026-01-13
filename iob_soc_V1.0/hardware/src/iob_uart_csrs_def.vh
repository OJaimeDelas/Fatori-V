`include "iob_uart_csrs_conf.vh"
//These macros may be dependent on instance parameters
//address macros
//addresses
`define IOB_UART_SOFTRESET_ADDR 0
`define IOB_UART_SOFTRESET_W 1

`define IOB_UART_DIV_ADDR 2
`define IOB_UART_DIV_W 16

`define IOB_UART_TXDATA_ADDR 4
`define IOB_UART_TXDATA_W 8

`define IOB_UART_TXEN_ADDR 5
`define IOB_UART_TXEN_W 1

`define IOB_UART_RXEN_ADDR 6
`define IOB_UART_RXEN_W 1

`define IOB_UART_TXREADY_ADDR 0
`define IOB_UART_TXREADY_W 1

`define IOB_UART_RXREADY_ADDR 1
`define IOB_UART_RXREADY_W 1

`define IOB_UART_RXDATA_ADDR 4
`define IOB_UART_RXDATA_W 8

`define IOB_UART_VERSION_ADDR 6
`define IOB_UART_VERSION_W 16

