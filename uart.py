from machine import Pin,UART

uart = UART(1, baudrate=9600, timeout=3000, tx=Pin(4), rx=Pin(5))



