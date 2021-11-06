#%%
import re
import gc
import os
try:
    import utils
    import machine
    import ntptime
    import board
    from rf433 import RF433
    machine.freq(160000000)
    utils.STA_IF.config(dhcp_hostname="http_serv")
    utils.do_connect()
    ntptime.settime()
    LED = utils.LED(board.LED_PIN_NO, board.LED_LOGIC_INVERTED)
    RF433 = RF433(board.TX_PIN_NO)
    HOST = utils.STA_IF.ifconfig()[0]
except ImportError:
    HOST = "localhost"

gc.collect()

import http_serv as http


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
    retries = int(params.get("retries", 10))
    channels_set = []
    for ch in CODE_DICT.keys():
        if ch in params:
            state = params[ch]
            ch_code = CODE_DICT.get(ch)
            if ch_code:
                code = ch_code.get(state)
                rf433.send_code(code, retries)
                channels_set.append(ch)
    if not channels_set:
        return "parameter `ch#` was not set", 400

    result = {"rf": params}
    return result

routes = [
    ("/", index),
    ("/api/led", api_led, ["GET", "POST"]),
    ("/api/rf", api_rf, ["POST"]),
    (re.compile(r"^/(.+\..+)"), static),
]

server = http.HTTPServer(routes)
server.run()
