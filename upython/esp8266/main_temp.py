import wemos as board
import utils

from time import sleep_ms #pylint: disable=no-name-in-module
from machine import Pin, ADC #pylint: disable=import-error
import onewire #pylint: disable=import-error
import ds18x20 #pylint: disable=import-error

PORT = 6265
HOST = "192.168.1.80"

# Initialize pins
print("\n\n")
adc0 = ADC(0)
led = utils.LED(board.LED_PIN_NO, inverted=board.LED_LOGIC_INVERTED)
led.on()

# Initialize periphery
ow = onewire.OneWire(Pin(board.D5))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()

def meas_temps():
    global roms, ds
    print("Measure temperature...")
    ds.convert_temp()
    sleep_ms(750)
    temps = []
    for rom in roms:
        temps.append(str(ds.read_temp(rom)))
    return temps

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
print("Connected. {} {}".format(utils.STA_IF.ifconfig(), utils.STA_IF.status("rssi")))
str_send = "{}\n".format(",".join(meas_temps()))
# str_send = "moin"
while 1:
    # str_send = str(adc0.read()*5.4/1024) + "\n"
    try:
        utils.tcp_send(str_send, HOST, PORT)
    except OSError as exc:
        print("Could not send data: {}".format(exc))
    finally:
        # print("Go to sleep...")
        # You have to wait until all data has been sent out
        sleep_ms(2000)
        # led.off()
        utils.go_to_sleep(60*1000)
