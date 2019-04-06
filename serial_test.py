"""
Sample script to access a serial port.
Requires pyserial

> pip install pyserial
"""

import serial
import platform
import time

if platform.system() == "Windows":
    port = "COM7"
else:
    port = "/dev/ttyUSB0"
baud = 500000
timeout = None

try:
    ser = serial.Serial(
        port=port,
        baudrate=baud,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=timeout,
        xonxoff=0,
        rtscts=0,
        dsrdtr=1 # When using Arduino, dsr is used for resetting. Set to 1 to disable resetting on port open.
        )
except:
    print("Could not open serial port.")
    exit()

try:
    print("Serial port '" + ser.name + "' opened (" + str(ser.baudrate) + " Baud).")
    ser.flushInput()
    time.sleep(0.1)
    data = []
    lines = ser.read_all().splitlines()
    for line in lines:
        try:
            # line = ser.readline()
            x = int(line)
            data.append(x)
        except:
            None
finally:
    ser.close()
    print("Serial port closed.")

print(data)