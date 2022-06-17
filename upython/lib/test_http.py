#%%
import re
import gc
import os
try:
    import utils
    import machine
    import ntptime
    import board
    import rf433
    import gy21
    # machine.freq(160000000)
    # Creating HW interfaces
    LED = utils.LED(board.LED_PIN_NO, board.LED_LOGIC_INVERTED)
    RF433 = rf433.RF433(board.TX_PIN_NO)
    I2C = machine.I2C(freq=400000, scl=machine.Pin(board.SCL_PIN_NO), sda=machine.Pin(board.SDA_PIN_NO))
    GY21 = gy21.GY21(I2C)
except ImportError:
    # For usage on normal PC
    class LED():
        def __init__(self):
            self.state = False
        def on(self):
            self.state = True
        def off(self):
            self.state = False
        def toggle(self):
            self.state = not self.state
        def is_on(self):
            return self.state
    LED = LED()

gc.collect()

import http_serv as http

HOST = "localhost"
STATIC_DIR = "static/"
TEMPLATES_DIR = STATIC_DIR + "templates/"

CODE_DICT = {
    "ch1": {
        "on": "000101010001010101010111" + "0",
        "off": "000101010001010101010100" + "0",
    },
    "ch2": {
        "on": "000101010100010101010111" + "0",
        "off": "000101010100010101010100" + "0",
    },
    "ch3": {
        "on": "000101010101000101010111" + "0",
        "off": "000101010101000101010100" + "0",
    }
}

def init_index_file():
    context = {
        "host": HOST,
    }
    re_var = re.compile(r"{{ (.*?) }}")
    with open(TEMPLATES_DIR + "index.html", "r") as f_in:
        with open(STATIC_DIR + "index.html", "w") as f_out:
            while True:
                line = f_in.readline()
                if not line:
                    break
                if re_var.search(line):
                    for k in context.keys():
                        line = line.replace("{{ " + k + " }}", context[k])
                f_out.write(line)

init_index_file()

def index(request):
    headers = {
        "Location": "/index.html",
    }
    return "", 301, headers

def static(request):
    filepath = STATIC_DIR + request.path_matches[1]
    if "../" in filepath:
        return "Relative filepaths are not allowed!", 400
    try:
        return http.HTTPFileResponse(filepath)
    except Exception as exc:
        return str(exc), 404

def api_led(request):
    if request.method == "GET":
        state = "on" if LED.is_on() else "off"
        result = {"led": {"state": state}}
    else:
        params = request.params
        if not "state" in params:
            return "Parameter `state` is not set", 400
        state = params["state"].lower()
        if state == "on":
            LED.on()
        elif state == "off":
            LED.off()
        elif state == "toggle":
            LED.toggle()
            state = "on" if LED.is_on() else "off"
        else:
            return "Parameter `state` is wrong", 400
        result = {"led": {"state": state}}
    return result

def api_rf(request):
    """Usage:
    `/api/rf?ch1=on&ch2=off&retries=10`
    """
    params = request.params
    retries = int(params.get("retries", 20))
    channels_set = []
    for ch in CODE_DICT.keys():
        if ch in params:
            state = params[ch]
            ch_code = CODE_DICT.get(ch)
            if ch_code:
                code = ch_code.get(state)
                RF433.send_code(code, retries)
                channels_set.append(ch)
    if not channels_set:
        return "parameter `ch#` was not set", 400

    result = {"rf": params}
    return result

def api_room(request):
    params = request.params
    type = params.get("type", "").lower()

    if type == "temp":
        meas_val = GY21.measure_temperature()
        result = {
            "temperature": meas_val,
            "temperature_unit": GY21.unit_temperature
        }
    elif type == "humidity":
        meas_val = GY21.measure_humidity()
        result = {
            "humidity": meas_val,
            "humidity_unit": GY21.unit_humidity
        }
    else:
        result = {
            "temperature": GY21.measure_temperature(),
            "temperature_unit": GY21.unit_temperature,
            "humidity": GY21.measure_humidity(),
            "humidity_unit": GY21.unit_humidity
        }
    return result

routes = [
    ("/", index),
    ("/api/led", api_led, ["GET", "POST"]),
    ("/api/rf", api_rf, ["POST"]),
    ("/api/room", api_room, ["GET"]),
    (re.compile(r"^/(.+\..+)"), static),
]

#%% CONNECT
LED.on()
while not utils.is_connected():
    utils.do_connect()
HOST = utils.host()
ntptime.settime()
LED.off()

#%% RUN SERVER
server = http.HTTPServer(routes)
try:
    server.run()
except KeyboardInterrupt:
    print("User cancelled")
except Exception as exc:
    print("Exception: {}".format(exc))
    try:
        machine.reset()
    except:
        pass
