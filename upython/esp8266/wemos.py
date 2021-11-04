"""
https://wiki.wemos.cc/products:d1:d1_mini
"""
import network # pylint: disable=import-error
import machine # pylint: disable=import-error

# Pin defines
LED_PIN_NO = D4 = 2 # LED
SDA_PIN_NO = D2 = 4
SCL_PIN_NO = D1 = 5
SCK_PIN_NO = D5 = 14
MISO_PIN_NO = D6 = 12
MOSI_PIN_NO = D7 = 13
SS_PIN_NO = D8 = 15
RST_PIN_NO = D0 = 16
D3 = 0

# LED logic
LED_LOGIC_INVERTED = True
