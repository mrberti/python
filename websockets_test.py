"""
An example for using websockets with python.

Requires 'websockets'

> pip install websockets
"""

import asyncio
import websockets

async def time(websocket, path):
    i = 0
    await websocket.send("Wilkommen!")
    # while True:
    #     i = i + 1
    #     data = str(i)
    #     await websocket.send(data)
    #     await asyncio.sleep(.1)

start_server = websockets.serve(time, '127.0.0.1', 5678)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()