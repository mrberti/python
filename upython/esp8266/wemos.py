"""
https://wiki.wemos.cc/products:d1:d1_mini
"""
import machine
import network
try:
    import socket
except ImportError:
    import usocket as socket


# Pin defines
D0 = 16
SCL = D1 = 5
SDA = D2 = 4
D3 = 0
LED = D4 = 2
SCK = D5 = 14
MISO = D6 = 12
MOSI = D7 = 13
SS = D8 = 15

# WLAN interface
STA_IF = network.WLAN(network.STA_IF)


# Some convenience functions
def do_connect(essid, password):
    global STA_IF
    if not STA_IF.isconnected():
        print("connecting to network '{}'...".format(essid))
        STA_IF.active(True)
        STA_IF.connect(essid, password)
        while not STA_IF.isconnected():
            pass
    print('network config: {}'.format(STA_IF.ifconfig()))

def go_to_sleep(sleep_ms):
    """
    Borowed from: http://docs.micropython.org/en/v1.9.2/esp8266/esp8266/tutorial/powerctrl.html
    """
    # configure RTC.ALARM0 to be able to wake the device
    rtc = machine.RTC()
    rtc.irq(trigger=rtc.ALARM0, wake=machine.DEEPSLEEP)
    # set RTC.ALARM0 to fire after 10 seconds (waking the device)
    rtc.alarm(rtc.ALARM0, sleep_ms)
    # put the device to sleep
    machine.deepsleep()

def is_deepsleep_reset():
    return bool(machine.reset_cause() == machine.DEEPSLEEP_RESET)

def udp_send(msg, host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        msg_raw = msg.encode("utf-8")
    except AttributeError:
        msg_raw = msg
    print(msg_raw)
    sock.sendto(msg_raw, (host, port))
    sock.close()

def tcp_connect(host, port, timeout=10):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.settimeout(timeout)
    sock_addr = socket.getaddrinfo(host, port)[0][-1]
    sock.connect(sock_addr)
    return sock

def tcp_send(msg, sock):
    sock.send(msg.encode("utf-8"))
