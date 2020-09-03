#!/usr/bin/env python

import socket


TCP_IP = ''
TCP_PORT = 15672
BUFFER_SIZE = 20  # Normally 1024, but we want fast response

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((TCP_IP, TCP_PORT))
s.listen(1)

conn, addr = s.accept()
print('Connection address: %s', addr)
while 1:
    data = conn.recv(BUFFER_SIZE)
    if not data: break
    print("received data: %s", data)
    conn.send(data)  # echo
conn.close()
