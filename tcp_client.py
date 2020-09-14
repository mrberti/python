#!/usr/bin/env python
import socket
import sys

argv = {}
for i in range(len(sys.argv)):
    argv[i] = sys.argv[i]

TCP_IP = argv.get(1, "localhost")
TCP_PORT = int(argv.get(2, 8080))
BUFFER_SIZE = 1024
REQUEST_DEF = f"GET / HTTP/1.1\n"
REQUEST_DEF += f"Host: {TCP_IP}\n\n"
REQUEST_DEF += "asdasdasd"*1000
REQUEST = argv.get(3, REQUEST_DEF)

def send_and_receive(host, port, request):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, True)
    s.connect((host, port))
    n_bytes_sent = s.send(request.encode("utf-8"))
    data = ""
    while True:
        data_recv = s.recv(BUFFER_SIZE)
        if data_recv:
            data += data_recv.decode("utf-8")
        else:
            break
    s.close()
    return data

for i in range(1):
    data = send_and_receive(TCP_IP, TCP_PORT, REQUEST)
    # print(data)
