###############################################################################
#
# The MIT License (MIT)
#
# Copyright (c) Crossbar.io Technologies GmbH
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

"""
Sample code for using websockets with Autobahn.

requires autobahn

> pip install autobahn
"""

import json
import asyncio
import logging
import random
from autobahn.asyncio.websocket import WebSocketServerProtocol, WebSocketServerFactory

class MyServerProtocol(WebSocketServerProtocol):

    def __init__(self):
        pass

    def onConnect(self, request):
        logging.info("Client connecting: {0}".format(request.peer))

    async def onOpen(self):
        logging.info("WebSocket connection open.")
        data = json.dumps("Welcome to the Autobahn server.").encode("UTF-8")
        self.sendMessage(data)

        packet = dict()
        while True:
            data = random.sample(range(0,1024), 20)
            packet["data_length"] = len(data)
            packet["data"] = data
            await asyncio.sleep(.05)
            self.sendMessage(json.dumps(packet).encode("UTF-8"))

    def onMessage(self, payload, isBinary):
        if isBinary:
            logging.info("Binary message received: {0} bytes".format(len(payload)))
        else:
            logging.info("Text message received: {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        logging.info("WebSocket connection closed: {0}".format(reason))

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s <%(levelname)s> %(message)s', level = logging.DEBUG)
    logging.info('Starting server')
    factory = WebSocketServerFactory(u"ws://127.0.0.1:5678")
    factory.protocol = MyServerProtocol

    loop = asyncio.get_event_loop()
    coro = loop.create_server(factory, '0.0.0.0', 5678)
    server = loop.run_until_complete(coro)

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
    finally:
        logging.info("Closing server...")
        server.close()
        loop.close()
        logging.info("Bye bye!")
