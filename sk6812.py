# Example using PIO to drive a set of WS2812 LEDs.

import array, time
from machine import Pin
import rp2

# Configure the number of WS2812 LEDs.
NUM_LEDS = 60 


@rp2.asm_pio(sideset_init=rp2.PIO.OUT_LOW, out_shiftdir=rp2.PIO.SHIFT_LEFT, autopull=True, pull_thresh=32)
def sk6812():
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


# Create the StateMachine with the sk6812 program, outputting on Pin(22).
sm = rp2.StateMachine(0, sk6812, freq=8_000_000, sideset_base=Pin(22))

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

def show(ms):
    sm.put(ar, 0)
    time.sleep_ms(ms)

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

while True:

    for i in range(NUM_LEDS):
        r = 255
        g = 0
        b = 0
        w = 0 

        set(i, r, g, b, w)
        show(40)

    for i in range(NUM_LEDS):
        r = 0
        g = 255
        b = 0
        w = 0 

        set(i, r, g, b, w)
        show(40)

    for i in range(NUM_LEDS):
        r = 0
        g = 0
        b = 255
        w = 0 

        set(i, r, g, b, w)
        show(40)

    for i in range(NUM_LEDS):
        r = 0
        g = 0
        b = 0
        w = 255 

        set(i, r, g, b, w)
        show(40)

    for i in range(NUM_LEDS):
        r = 255
        g = 255
        b = 255
        w = 255 

        set(i, r, g, b, w)
        show(40)
        
    for i in range(0, 60):
        set(i, 0, 0, 0, 0)
    show(40)

    for l in range(NUM_LEDS):
        hue = l / NUM_LEDS
        r, g, b = hsv2rgb(hue, 1, 1)
        set(l, r, g, b, 0)
        if l != 0:
            set(l - 1, 0, 0, 0, 0)
        show(40)

    for pos in range(0, NUM_LEDS):
        for l in range(0, NUM_LEDS):
            dist1 = abs(pos - l)
            dist2 = NUM_LEDS - dist1
            dist = min(dist1, dist2)
            dist = dist / NUM_LEDS
            prox = pow(1. - dist, 50) 
            hue = l / NUM_LEDS
            r, g, b = hsv2rgb(hue, 1., prox)
            r, g, b = int(r), int(g), int(b)
            set(l, r, g, b, 0)
        show(0)

    for l in range(NUM_LEDS):
        hue = l / NUM_LEDS
        r, g, b = hsv2rgb(hue, 1, 1)
        set(l, r, g, b, 0)
        show(40)
        
        
    for s in range(0, 360):
        for l in range(NUM_LEDS):
            hue = (l / NUM_LEDS * 360 + s) % 360
            r, g, b = hsv2rgb(hue / 360., 1, 1)
            set(l, r, g, b, 0)
        show(0)
    
    for l in range(NUM_LEDS):
        set(l, 0, 0, 0, 0)
        show(40)

    time.sleep_ms(1000)
    