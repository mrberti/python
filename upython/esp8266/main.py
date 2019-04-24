import wemos
import time

from machine import Pin, ADC
import onewire
import ds18x20

PORT = 6265
HOST = "192.168.1.80"

# Initialize pins
print("\n\n")
adc0 = ADC(0)
led = Pin(2, Pin.OUT)
led.off() # On wemos D1 board inverted logic

# Initialize periphery
ow = onewire.OneWire(Pin(14))
ds = ds18x20.DS18X20(ow)
roms = ds.scan()

def meas_temp():
    global roms, ds
    temp = "-999"
    print("Measure temperature...")
    ds.convert_temp()
    time.sleep_ms(750)
    temp = str(ds.read_temp(roms[0]))
    return temp

print("Try to connect to Wifi")
try_counter = 1000
while not wemos.STA_IF.isconnected():
    try_counter -= 1
    time.sleep(.1)
    print(".", end="")
    if led.value():
        led.off()
    else:
        led.on()
    if try_counter < 0:
        print("Could not connect to Wifi")
        print("Go to sleep...")
        wemos.go_to_sleep(10000)

led.off()
print("Connected. {} {}".format(wemos.STA_IF.ifconfig(), wemos.STA_IF.status("rssi")))
str_send = "{}\n".format(meas_temp())
try:
    wemos.tcp_send(str_send, HOST, PORT)
except OSError as exc:
    print("Could not send data: {}".format(exc))
finally:
    print("Go to sleep...")
    # You have to wait until all data has been sent out
    time.sleep(1)
    wemos.go_to_sleep(60*1000)
