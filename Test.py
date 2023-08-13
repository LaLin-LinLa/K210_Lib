from fpioa_manager import fm

# maixduino board_info PIN10/PIN11
# from board import board_info
# fm.register(board_info.PIN10, fm.fpioa.UART1_TX, force=True)
# fm.register(board_info.PIN11, fm.fpioa.UART1_RX, force=True)

# need your connect hardware IO 10/11 to loopback
fm.register(10, fm.fpioa.UART1_TX, force=True)
fm.register(11, fm.fpioa.UART1_RX, force=True)

from machine import UART

uart_A = UART(UART.UART1, 115200, 8, 1, 0, timeout=1000, read_buf_len=4096)

import time

while True:
  FH = bytearray([0x01, 0x02, 0x03, 0x04, 0x05, 0x06])
  uart_A.write(FH)
  time.sleep_ms(100) # ohter event

uart_A.deinit()
del uart_A

