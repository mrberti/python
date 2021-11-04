import time
import machine

import wemos as board
import utils

led = utils.LED(board.LED_PIN_NO, inverted=board.LED_LOGIC_INVERTED)

pin = machine.Pin(board.D0, machine.Pin.OUT)

data = bin(1381719)
data = "0001010100010101010101110"

t = [0]
i = 0
for bit in data:
    if bit == "0":
        sleep_ticks_us = 350
    else:
        sleep_ticks_us = 1018
    t.append(t[i - 1] + 310)
    t.append(t[i - 1] + 1410 - sleep_ticks_us)

del t[0]

print(t)

while True:
    start_us = time.ticks_us()
    pin.value(1)
    for tx in t:
        end_us = tx + start_us
        while time.ticks_us() < end_us:
            time.sleep_us(50)
        pin.value(not bool(pin.value()))
    pin.value(0)
    time.sleep(.1)

# def _sleep(delay):
#     _delay = delay / 100.
#     end = time.ticks_us() + delay - _delay
#     while time.ticks_us() < end:
#         time.sleep_us(int(_delay))

# while True:
#     for i in data:
#         pin.value(1)
#         if i == "0":
#             sleep = 310
#         else:
#             sleep = 1018
#         _sleep(sleep)
#         pin.value(0)
#         _sleep(1410 - sleep)
#     time.sleep(100e-3)
