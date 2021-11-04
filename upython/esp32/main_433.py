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
def _sleep(delay):
    _delay = delay / 100.
    end = time.ticks_us() + delay - _delay
    while time.ticks_us() < end:
        time.sleep_us(int(_delay))

def send_code(data, count=10):
    for _ in range(count):
        for bit in data:
            TX.value(1)
            if bit == "0":
                sleep = 350
            else:
                sleep = 3*350
            _sleep(sleep)
            TX.value(0)
            _sleep(4 * 350 - sleep)
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
    print(f"Client connected: {remote_info}")
    recv = remote.recv(1024).decode("utf-8")
    print(f"> {recv}")

    try:
        data = json.loads(recv)
    except ValueError as exc:
        finish(f"Could not parse JSON.")
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
        finish(f"{channel} or {state} unknown.")
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
            # print(f"Exception occured: {exc}")
            # running = False
    SOCK.close()
    print("Program finished")

# Initialize hardware
LED = utils.LED(board.LED_PIN_NO, inverted=board.LED_LOGIC_INVERTED)
TX = machine.Pin(23, machine.Pin.OUT)
utils.do_connect()

SOCK = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
SOCK.bind((TCP_IP, TCP_PORT))
SOCK.listen(5)

main()
