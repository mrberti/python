import nodemcu32s as board
import utils

from time import sleep_ms # pylint: disable=no-name-in-module

PORT = 6265
HOST = "192.168.1.40"

# Initialize pins
print("\n\n")
led = utils.LED(board.LED_PIN_NO, inverted=board.LED_LOGIC_INVERTED)
led.on()

print("Try to connect to Wifi")
try_counter = 1000
while not utils.STA_IF.isconnected():
    try_counter -= 1
    sleep_ms(100)
    print(".", end="")
    led.toggle()
    if try_counter < 0:
        print("Could not connect to Wifi")
        print("Go to sleep...")
        utils.go_to_sleep(10000)

led.on()
print("Connected. {}".format(utils.STA_IF.ifconfig()))
str_send = "moin"
try:
    utils.tcp_send(str_send, HOST, PORT)
except OSError as exc:
    print("Could not send data: {}".format(exc))
finally:
    print("Go to sleep...")
    # You have to wait until all data has been sent out
    sleep_ms(1000)
    led.off()
    utils.go_to_sleep(1*1000)
