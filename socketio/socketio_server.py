import os
import pathlib
import eventlet
import socketio

static = pathlib.Path(__file__).parent / "static"

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': str(static.absolute())
})

@sio.event
def connect(sid, environ):
    print('connect ', sid)

@sio.event
def my_message(sid, data):
    print('message ', data)

@sio.event
def disconnect(sid):
    print('disconnect ', sid)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 5000)), app)
