import time
import asyncio
from utils import *

from autobahn.asyncio.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from autobahn.asyncio.websocket import WebSocketClientProtocol, \
    WebSocketClientFactory

# IP = "172.19.72.42"
# IP = "192.168.1.80"
# IP = "217.160.241.208"
# IP = "192.168.1.17"
# IP = "localhost"
IP = "127.0.0.1"
PORT = 54321
URI = f"ws://{IP}:{PORT}"
ADDR = (IP, PORT)
print(ADDR)

N = 10000
DATA = b"x"*1

class ServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connected: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        # Echo
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class ClientProtocol(WebSocketClientProtocol):
    def onConnect(self, response):
        print(f"Connected to server: {response.peer}")
        self.i = 0
        self.t = init_t(N)

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))

    def onOpen(self):
        print("WebSocket connection open.")
        self.t[self.i] = time.time()
        self.i += 1
        self.sendMessage(DATA)

    def onMessage(self, payload, isBinary):
        if self.i < N:
            self.t[self.i] = time.time()
            self.i += 1
            self.sendMessage(payload)
        else:
            self.sendClose()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

async def server():
    factory = WebSocketServerFactory(URI)
    factory.protocol = ServerProtocol

    loop = asyncio.get_running_loop()
    server = await loop.create_server(factory, IP, PORT)
    async with server:
        await server.serve_forever()

async def client():
    factory = WebSocketClientFactory(URI)
    factory.protocol = ClientProtocol
    loop = asyncio.get_running_loop()
    transport, proto = await loop.create_connection(factory, IP, PORT)
    await proto.is_open
    try:
        await proto.is_closed
        print("Connection was closed")
    finally:
        transport.close()
    t = normalize_t(proto.t)
    print_statistics(t, len(DATA), N)
    plot_statistics(t)

if is_server():
    task = server
else:
    task = client

try:
    asyncio.run(task())
except KeyboardInterrupt:
    print("CANCALCALS")
