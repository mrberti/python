"""
https://www.shenzhen2u.com/NodeMCU-32S
"""
import network # pylint: disable=import-error
import machine # pylint: disable=import-error

__BOARD__ = "nodemcu32s"
__CPU__ = "esp32"

# Pin defines
LED_PIN_NO = 2
SDA_PIN_NO = 23
SCL_PIN_NO = 22
TX_PIN_NO = 21
# RST_PIN_NO = 
# SDA = machine.Pin(SDA_PIN_NO, machine.Pin.OUT)
# SCL = machine.Pin(SCL_PIN_NO, machine.Pin.OUT)
# I2C = machine.I2C(scl=SCL, sda=SDA, freq=400000)

# LED logic
LED_LOGIC_INVERTED = False
