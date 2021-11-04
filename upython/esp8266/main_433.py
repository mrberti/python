import time
import socket
import json

# uPython specific
import machine

# Custom modules
import utils
import board

# Global parameters
PIN_TX = board.TX_PIN_NO
TCP_IP = ""
TCP_PORT = 1234

DELAY_US_SHORT = 355
DELAY_US_LONG = 3 * 355
if "8266" in board.__CPU__:
    TIMING_CORRECTION_US = 220
elif "esp32" in board.__CPU__:
    # TODO
    TIMING_CORRECTION_US = 0
else:
    raise NotImplementedError("No TIMING_CORRECTION_US defined.")

# Code dict
CODE_DICT = {
    1: { # Channel
        "on": "000101010001010101010111" + "0",
        "off": "000101010001010101010100" + "0",
    },
    2: { # Channel
        "on": "000101010100010101010111" + "0",
        "off": "000101010100010101010100" + "0",
    },
    3: { # Channel
        "on": "000101010101000101010111" + "0",
        "off": "000101010101000101010100" + "0",
    }
}

#-----------------------------------------------------------------------
# MODULE FUNCTIONS
#-----------------------------------------------------------------------
def create_time_vector(data):
    t = [0]
    i = 0
    for bit in data:
        if bit == "0":
            t_on = DELAY_US_SHORT + TIMING_CORRECTION_US + t[i]
            t_off = DELAY_US_LONG - TIMING_CORRECTION_US + t_on
        else:
            t_on = DELAY_US_LONG + TIMING_CORRECTION_US + t[i]
            t_off = DELAY_US_SHORT - TIMING_CORRECTION_US + t_on
        t.append(t_on)
        t.append(t_off)
        i += 2
    del t[0]
    return t

def send_code(data, count=10):
    t_vector = create_time_vector(data)
    print(t_vector)
    for _ in range(count):
        start = time.ticks_us()
        state = True
        # TX.on()
        for t in t_vector:
            TX.value(state)
            state = not state
            end = start + t
            while time.ticks_us() < end:
                pass
        TX.off()
        time.sleep(10e-3)

#-----------------------------------------------------------------------
# CODE
#-----------------------------------------------------------------------
def main_loop():
    def finish(msg):
        try:
            print(msg)
            remote.send(msg)
        finally:
            remote.close()
            LED.off()

    print("Waiting for client...")
    try:
        remote, remote_info = SOCK.accept()
    except KeyboardInterrupt as exc:
        # HACK: Keyboard interrupt is not properly handled in the REPL
        raise Exception("Keyboard Interrupt")
    LED.on()
    print("Client connected: {}".format(remote_info))
    recv = remote.recv(1024).decode("utf-8")
    print("> {recv}")

    try:
        data = json.loads(recv)
    except ValueError as exc:
        finish("Could not parse JSON.")
        return

    try:
        channel = int(data.get("ch"))
        state = str(data.get("state"))
        retries = int(data.get("retries", 10))
    except AttributeError:
        finish("Wrong JSON format")
        return

    if not channel or not state:
        finish("No `ch` and `state` set")
        return

    try:
        code = CODE_DICT[channel][state]
    except IndexError:
        finish("{} or {} unknown.".format(channel, state))
        return

    # TODO
    # - Pulse lengths and syncs
    # - Delay time modifiable
    # - Send raw data
    # - Accept hex and dec codes

    send_code(code, retries)
    finish("Success")

def main():
    running = True
    while running:
        # try:
        main_loop()
        # except Exception as exc:
            # print("Exception occured: {exc}")
            # running = False
    SOCK.close()
    print("Program finished")

# Initialize hardware
if "8266" in board.__CPU__:
    print("Setting CPU frequency to 160 MHz.")
    machine.freq(160000000)
LED = utils.LED(board.LED_PIN_NO, inverted=board.LED_LOGIC_INVERTED)
TX = machine.Pin(PIN_TX, machine.Pin.OUT)
utils.do_connect()

SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK.bind((TCP_IP, TCP_PORT))
SOCK.listen(5)

main()
