import socket
import sys
import time
import numpy as np


# IP = "172.23.172.248"
# IP = "192.168.1.80"
# IP = "192.168.1.17"
# IP = "localhost"
IP = "127.0.0.1"
PORT = 54321
ADDR = (IP, PORT)
print(ADDR)

N = 10000
DATA = b"x"*1024 * 1
RCV_BUF = 1024 * 10

argv = sys.argv

is_server = False
# is_udp = True
is_udp = False
is_closed = False
if len(argv) > 1:
    if argv[1] == "-s": is_server = True

con = None
if is_udp:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
else:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)

def establish_connection():
    global con, sock
    if is_server:
        if is_udp:
            sock.bind(ADDR)
        else:
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.bind(ADDR)
            sock.listen(5)
            con, _ = sock.accept()
            print(con)
    else:
        if is_udp:
            sock.bind(("0.0.0.0", PORT))
        sock.connect(ADDR)
        print(sock)

def benchmark():
    global con, sock, is_closed
    if is_server:
        if is_udp:
            data, addr = sock.recvfrom(RCV_BUF)
            if data == b"close":
                print("CLOSE!!!!!!!!")
                is_closed = True
        else:
            data = con.recv(RCV_BUF)
            # con.send(data)
    else:
        if is_udp:
            sock.sendto(DATA, ADDR)
        else:
            sock.send(DATA)
            time.sleep(0)
            # data = sock.recv(RCV_BUF)

def close_connection():
    global con, sock
    if is_server:
        if is_udp:
            pass
        else:
            # con.close()
            time.sleep(1)
            con.shutdown(0)
    else:
        if is_udp:
            sock.sendto(b"close", ADDR)
    if not is_udp:
        sock.close()

establish_connection()
start = time.time()
t = np.zeros(N) * np.nan
for i in range(1, int(N) + 1):
    try:
        benchmark()
    except (KeyboardInterrupt, ConnectionResetError):
        break
    t[i-1] = time.time_ns()
    if is_closed:
        break
end = time.time()
close_connection()
t = t[~np.isnan(t)]
delta = (t[-1] - t[0]) / 1e9
t = t - t[0]
dt = np.diff(t) / 1e6
print(f"{i}/{int(N)}\t{delta:.3f}s\t{i / delta:.3f} msg/s\t{delta * 1e6/i:.3f} µs/msg")
data_sent_mb = len(DATA) * i / 1000 / 1000
print(f"{data_sent_mb:.3f} MB\t{data_sent_mb/delta:.3f} MB/s")
print(f"Mean:\t{np.nanmean(dt):.3f} ms")
print(f"Min:\t{np.nanmin(dt):.3f} ms")
print(f"Max:\t{np.nanmax(dt):.3f} ms")
print(f"Std:\t{np.nanstd(dt):.3f} ms")

if not is_server:
    import matplotlib.pyplot as plt
    plt.subplot(2,1,1)
    plt.plot(t[1:], dt, '.')
    plt.ylabel("dt [ms]")
    plt.xlabel("time [s]")
    plt.subplot(2,1,2)
    plt.hist(dt, 100)
    plt.show()