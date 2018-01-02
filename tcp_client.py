#!/usr/bin/env python

import socket
import sys

argv = sys.argv

for i in range(len(argv)):
	arg = argv[i]
        print( arg )

TCP_IP = argv[1]
TCP_PORT = 5005
BUFFER_SIZE = 1024
MESSAGE1 = "GET /wiki/Katzen HTTP/1.1\n"
MESSAGE2 = "Host: de.wikipedia.de\n\n"

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((TCP_IP, TCP_PORT))

sent = s.send(MESSAGE1)
print sent
sent = s.send(MESSAGE2)
print sent

data = s.recv(BUFFER_SIZE)
print "closing..."
asd = s.close()
print "closed!"

print "received data:", data

