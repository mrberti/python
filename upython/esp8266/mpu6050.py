import struct
from machine import Pin, I2C

MPU6050_ADDR = 104

class MPU6050Error(Exception):
    pass

class MPU6050(object):
    def __init__(self, i2c, baudrate=400000, a0=0):
        self.i2c = i2c
        self.baudrate = baudrate
        self.buf_accel = bytearray(6)
        self.buf_gyro = bytearray(6)
        self.buf_temp = bytearray(1)
        self.offset_x = 5200
        self.offset_y = 0
        self.offset_z = -1816
        self._address = MPU6050_ADDR + a0

    def init(self):
        pass

    def is_connected(self):
        return bool(self._address in self.i2c.scan())

    def start(self):
        if not self.is_connected():
            raise MPU6050Error("MPU6050 is not connected on I2C bus.")
        self.i2c.writeto_mem(self._address, 107, b"\x00")

    def stop(self):
        pass

    def get_accel(self):
        self.i2c.readfrom_mem_into(self._address, 59, self.buf_accel)
        accel = struct.unpack(">hhh", self.buf_accel)
        return accel

    def get_gyro(self):
        self.i2c.readfrom_mem_into(self._address, 67, self.buf_gyro)
        gyro = struct.unpack(">hhh", self.buf_gyro)
        return gyro

    def get_temp(self):
        self.i2c.readfrom_mem_into(self._address, 65, self.buf_temp)
        temp = struct.unpack(">h", self.buf_temp)[0] / 340 + 36.53
        return temp


def main():
    import time
    from math import (sqrt, sin, cos, pi, acos)

    i2c = I2C(scl=Pin(5), sda=Pin(4), freq=400000)
    mpu = MPU6050(i2c)
    mpu.init()
    mpu.start()
    time.sleep(.1)
    while 1:
        # time.sleep(.2)
        val = mpu.get_accel()
        x = val[0]#/16384
        y = val[1]#/16384
        z = val[2]#/16384
        r = sqrt(x*x + y*y + z*z)
        sign = 1 if (y > 0) else -1
        phi = sign * acos(z / sqrt(y**2 + z**2))
        y2 = cos(phi) * y - sin(phi) * z
        z2 = sin(phi) * y + cos(phi) * z
        theta = acos(z2 / r)
        print("{:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.0f},{:6.1f},{:6.1f}"
            .format(x, y, z, y2, z2, r, phi * 180 / pi, theta * 180 / pi))


if __name__ == "__main__":
    main()
