import struct
from machine import Pin, I2C

HMC5883_ADDRESS = 0x1e

i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)

# Continuous mode
i2c.writeto_mem(HMC5883_ADDRESS, 0, b"\x10\x20\x00")

def measure():
    return struct.unpack(">hhh", i2c.readfrom_mem(HMC5883_ADDRESS, 3, 6))

def main():
    import time
    import math
    while 1:
        time.sleep(.1)
        val = measure()
        x = val[0]
        y = val[1]
        z = val[2]
        r = math.sqrt(x*x + y*y + z*z)
        print("{},{},{},{}".format(x, y, z, r))

if __name__ == "__main__":
    main()
