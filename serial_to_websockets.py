import asyncio
import websockets

import serial
import platform
import time

import json

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
print("Serial port '" + ser.name + "' opened (" + str(ser.baudrate) + " Baud).")

async def handler(websocket, path):
    print("User connected.")
    ser.flushInput()
    while True:
        await asyncio.sleep(.1)
        data = []
        lines = ser.read_all().splitlines()
        for line in lines:
            try:
                # line = ser.readline()
                x = int(line)
                data.append(x)
            except:
                None
        data_length = len(lines)
        packet = dict()
        packet["data_length"] = data_length
        packet["data"] = data
        await websocket.send(json.dumps(packet))

start_server = websockets.serve(handler, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()