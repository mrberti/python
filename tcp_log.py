"""
Just print everything we get on socket. Output is also written to
a csv file with timestamps.
"""
import socket
import time
import os

PORT = 6265
SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def loop():
    sock_remote, remote_addr = SOCK.accept()
    data_recv = sock_remote.recv(1024).decode("utf-8").replace("\n", "")
    if data_recv:
        line = "{},{}".format(int(time.time()), data_recv.strip())
        try:
            with open("/home/simon/temps.csv", "a") as f:
                f.write(line + "\n")
        except:
            pass
        print(line)
    sock_remote.close()

def main():
    addr = socket.getaddrinfo("192.168.1.80", PORT)[0][-1]
    SOCK.bind(addr)
    SOCK.listen(5)
    try:
        while 1:
            loop()
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
