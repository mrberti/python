from utils import *
import asyncio

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

N = 10
DATA = b"x"*1024 * 2
DATA = b"x"
RCV_BUF = 1024 * 1

class ServerProtocol(WebSocketServerProtocol):
    def onConnect(self, request):
        print(f"Client connected: {request.peer}")

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

class ClientProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print(f"Connected to server: {response.peer}")

    def onConnecting(self, transport_details):
        print("Connecting; transport details: {}".format(transport_details))
        return None  # ask for defaults

    def onOpen(self):
        print("WebSocket connection open.")

        # def loop(loops, data):
        # loops = N
        # data = DATA
        # t = init_t(loops)
        # for i in range(loops):
        #     t[i] = time.time()
        #     self.sendMessage(data)
        # self.sendClose()
        # t = normalize_t(t)
        # print_statistics(t, len(data), loops)
        # plot_statistics(t)
        # loop(1000, DATA)

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

def server():
    factory = WebSocketServerFactory(URI)
    factory.protocol = ServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, IP, PORT)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()
        loop.close()

async def client():
    factory = WebSocketClientFactory(URI)
    factory.protocol = ClientProtocol
    loop = asyncio.get_running_loop()
    transport, protocol = await loop.create_connection(factory, IP, PORT)
    print("XXX")
    # transport.close()

if is_server():
    server()
else:
    asyncio.run(client())
