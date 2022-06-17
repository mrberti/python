"""
Some util function for convenience.
"""
import machine # pylint: disable=import-error
import network # pylint: disable=import-error
try:
    import usocket as socket
except ImportError:
    import socket


# WLAN interface
STA_IF = network.WLAN(network.STA_IF)
AP_IF = network.WLAN(network.AP_IF)


class LED(object):
    """Convenince class for controlling the onboard LED. The actual
    logic can be inverted compared to a normal `machine.Pin`."""
    def __init__(self, led_pin_no, inverted=False):
        self._inverted = inverted
        self._led = machine.Pin(led_pin_no, machine.Pin.OUT)
        self.off()

    def on(self):
        if self._inverted:
            self._led.off()
        else:
            self._led.on()

    def off(self):
        if self._inverted:
            self._led.on()
        else:
            self._led.off()
    
    def is_on(self):
        return not bool(self._led.value()) ^ (not self._inverted)

    def toggle(self):
        if self.is_on():
            self.off()
        else:
            self.on()

def read_credentials():
    try:
        with open("credentials") as f:
            essid = f.readline().strip()
            password = f.readline().strip()
    except Exception as exc:
        exc_str = "Could not read credentials file. {exc}".format(exc=exc)
        raise Exception(exc_str)
    return (essid, password)

def do_connect(essid=None, password=None):
    global STA_IF
    STA_IF = network.WLAN(network.STA_IF)
    if essid is None or password is None:
        credentials = read_credentials()
        essid = credentials[0]
        password = credentials[1]
    if not STA_IF.isconnected():
        print("Trying to connect to network {!r}...".format(essid))
        STA_IF.active(True)
        STA_IF.connect(essid, password)
        while not STA_IF.isconnected():
            pass
    print('Connected to Wifi. ', STA_IF.ifconfig())
    return STA_IF.ifconfig()

def is_connected():
    return STA_IF.isconnected()

def host():
    return STA_IF.ifconfig()[0]

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
    # sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # sock.settimeout(timeout)
    sock_addr = socket.getaddrinfo(host, port)[0][-1]
    print("TCP connect: {}".format(sock_addr))
    sock.connect(sock_addr)
    return sock

def tcp_send(msg, host, port, timeout=10):
    sock = tcp_connect(host, port, timeout)
    print("Send data: {}".format(msg))
    sock.send(msg.encode("utf-8"))
    sock.close()
