#!/usr/bin/env python

import socket
import sys

argv = sys.argv

for i in range(len(argv)):
	arg = argv[i]
	print( arg )

# TCP_IP = argv[1]
TCP_IP = "localhost"
TCP_PORT = 80
BUFFER_SIZE = 1024
MESSAGE1 = b"GET / HTTP/1.1 \n\r"
MESSAGE2 = b"Host: mrberti.de\n\r\n\r"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

sent = s.send(MESSAGE1)
# print(sent)
sent = s.send(MESSAGE2)
# print(sent)

data = s.recv(BUFFER_SIZE)
print("closing...")
asd = s.close()
print("closed!")

print("received data: %s", data)

