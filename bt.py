# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin, UART
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 60 


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def ws2812():
    T1 = 2
    T2 = 5
    T3 = 3
    wrap_target()
    label("bitloop")
    out(x, 1)               .side(0)    [T3 - 1]
    jmp(not_x, "do_zero")   .side(1)    [T1 - 1]
    jmp("bitloop")          .side(1)    [T2 - 1]
    label("do_zero")
    nop()                   .side(0)    [T2 - 1]
    wrap()


# Create the StateMachine with the ws2812 program, outputting on Pin(22).
sm = rp2.StateMachine(0, ws2812, freq=8_000_000, sideset_base=Pin(22))

# Start the StateMachine, it will wait for data on its FIFO.
sm.active(1)

# Display a pattern on the LEDs via an array of LED RGB values.
ar = array.array("I", [0 for _ in range(NUM_LEDS)])

def set(i, r, g, b, w):
    # grb
    d = 0
    d |= g << 24
    d |= r << 16
    d |= b << 8
    d |= w
    ar[i] = d
    
def set_all(r, g, b, w):
    for i in range(NUM_LEDS):
        set(i, r, g, b, w)

def show():
    sm.put(ar, 0)

def hsv2rgb(h, s, v):
        if s == 0.0: v*=255; return (v, v, v)
        i = int(h*6.) # XXX assume int() truncates!
        f = (h*6.)-i; p,q,t = int(255*(v*(1.-s))), int(255*(v*(1.-s*f))), int(255*(v*(1.-s*(1.-f)))); v*=255; i%=6
        if i == 0: return (v, t, p)
        if i == 1: return (q, v, p)
        if i == 2: return (p, v, t)
        if i == 3: return (p, q, v)
        if i == 4: return (t, p, v)
        if i == 5: return (v, p, q)

#uart = UART(1, baudrate=9600, timeout=100, tx=Pin(4), rx=Pin(5))
uart = UART(1, baudrate=9600, tx=Pin(4), rx=Pin(5))

def on_bt(o):
    if o == 'r':
        set_all(255, 0, 0, 0)
    if o == 'g':
        set_all(0, 255, 0, 0)
    if o == 'b':
        set_all(0, 0, 255, 0)
    if o == 'w':
        set_all(0, 0, 0, 255)
    if o == 'y':
        set_all(255, 255, 0, 0)
    if o == 'm':
        set_all(255, 0, 255, 0)
    if o == 'c':
        set_all(0, 255, 255, 0)
    if o == 'a':
        set_all(255, 255, 255, 255)
    if o == 'h':
        for i in range(NUM_LEDS):
            r, g, b = hsv2rgb(float(i)/float(NUM_LEDS), 1., 1.)
            set(i, int(r), int(g), int(b), 0)
            
    show()

#uart.irq(UART.RX_ANY, 5, handler=on_bt, wake=machine.IDLE)
#while True:
#    for t in uart:
#        on_bt(t)
#        print(t)

data = bytes()

while True:
    if uart.any() > 0:
        o = uart.read(1)
        s = o.decode('utf-8')
        #data += s
        print(s)
        on_bt(s)
    
    
        