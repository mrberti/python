# Wemods D1
[Wemos D1](https://wiki.wemos.cc/products:d1:d1_mini)

Pin  |  Function                      |  ESP-8266 Pin
-----|--------------------------------|---------
TX   |  TXD                           |  TXD
RX   |  RXD                           |  RXD
A0   |  Analog input, max 3.3V input  |  A0
D0   |  IO                            |  16
D1   |  IO, SCL                       |  5
D2   |  IO, SDA                       |  4
D3   |  IO, 10k Pull-up               |  0
D4   |  IO, 10k Pull-up, BUILTIN_LED  |  2
D5   |  IO, SCK                       |  14
D6   |  IO, MISO                      |  12
D7   |  IO, MOSI                      |  13
D8   |  IO, 10k Pull-down, SS         |  15
G    |  Ground                        |  GND
5V   |  5V                            |  -
3V3  |  3.3V                          |  3.3V
RST  |  Reset                         |  RST

# Sample Code
[Micropython Doc](http://docs.micropython.org/en/latest/esp8266/quickref.html#general-board-control)

## GPIO
```Python
>>> from machine import Pin
>>> d4 = Pin(wemos.D4, Pin.OUT)
```

## PWM
```Python
>>> from machine import Pin, PWM
>>> pwm4 = PWM(Pin(wemos.D4))
>>> pwm4.duty(200)
```

## ADC
```Python
>>> from machine import ADC
>>> adc = ADC(0)
>>> adc.read()
```
## SPI
Hardware SPI uses D5 (SCK), D6 (MISO), D7 (MOSI).
```Python
>>> hspi = SPI(1, baudrate=80000000, polarity=0, phase=0)
>>> hspi.read(10)            # read 10 bytes on MISO
>>> hspi.read(10, 0xff)      # read 10 bytes while outputing 0xff on MOSI
>>> buf = bytearray(50)     # create a buffer
>>> hspi.readinto(buf)       # read into the given buffer (reads 50 bytes in this case)
>>> hspi.readinto(buf, 0xff) # read into the given buffer and output 0xff on MOSI
>>> hspi.write(b'12345')     # write 5 bytes on MOSI
>>> buf = bytearray(4)      # create a buffer
>>> hspi.write_readinto(b'1234', buf) # write to MOSI and read from MISO into the buffer
>>> hspi.write_readinto(buf, buf) # write buf to MOSI and read MISO back into buf
```
