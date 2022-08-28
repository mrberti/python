import time
import asyncio
import webbrowser
import pathlib
from aiohttp import web
import socketio

host = "localhost"
port = 5000
static = pathlib.Path(__file__).parent / "static"

sio = socketio.AsyncServer(async_mode='aiohttp')
app = web.Application()
sio.attach(app)

@sio.event
def connect(sid, environ):
    print("connect ", sid)

@sio.event
async def chat_message(sid, data):
    await sio.emit("hey", {"data": "tach"})
    print("message ", data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

app.router.add_static('/', static)

async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print("running")

    while True:
        try:
            await asyncio.sleep(3600)  # sleep forever
        except KeyboardInterrupt:
            break

if __name__ == '__main__':
    # webbrowser.open(f"http://{host}:{port}/index.html", autoraise=False)
    web.run_app(
        app,
        host=host,
        port=port,
    )
    # asyncio.run(main())
