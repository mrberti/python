# Temp and Humidity sensor
import utime
from machine import Pin, I2C

class Commands:
    temperature = b"\xf3"
    humidity = b"\xf5"

class GY21:
    def __init__(self, i2c):
        self.i2c = i2c
        self.unit_temperature = "degC"
        self.unit_humidity = "%"
        self.sleep_ms = 50
        self.i2c_addr = 0x40

    def measure_temperature(self):
        cmd = Commands.temperature
        val_bytes = self._i2c_write_and_read(cmd)
        value_converted = -46.85 + 175.72 * float(val_bytes) / 65535.
        return value_converted

    def measure_humidity(self):
        cmd = Commands.humidity
        val_bytes = self._i2c_write_and_read(cmd)
        value_converted = -6. + 125. * float(val_bytes) / 65535.
        return value_converted
    
    def _i2c_write_and_read(self, cmd_byte):
        """
        addr: 0x40
        temp: b"\xf3"
        humi: b"\xf5"
        """
        self.i2c.writeto(self.i2c_addr, cmd_byte)
        utime.sleep_ms(self.sleep_ms)
        val_bytes = int.from_bytes(self.i2c.readfrom(self.i2c_addr, 2), "big") & 0xfffc
        return val_bytes

    def measure(self):
        """Measure humidity and temperature. Returns a `dict`."""
        value_t = 0
        value_rh = 0
        return {
            "temperature" : value_t,
            "unit_temperature": self.unit_temperature,
            "humidity": value_rh,
            "unit_humidity": self.unit_humidity,
        }
    
    def reset(self):
        pass

    def get_serial(self):
        pass

if __name__ == "__main__":
    i2c = I2C(freq=400000, scl=Pin(5), sda=Pin(4))
    gy21 = GY21(i2c)

    while True:
        # i2c.writeto(0x40, b"\xf3")
        # time.sleep(.05)
        # st = int.from_bytes(i2c.readfrom(0x40, 2), "big") & 0xfffc
        # i2c.writeto(0x40, b"\xf5")
        # time.sleep(.05)
        # sh = int.from_bytes(i2c.readfrom(0x40, 2), "big") & 0xfffc
        # rh = -6. + 125. * float(sh) / 65535.
        # t = -46.85 + 175.72 * float(st) / 65535.
        t = gy21.measure_temperature()
        rh = gy21.measure_humidity()
        print("{:.1f} degC, {:.1f} % RH".format(t, rh))
