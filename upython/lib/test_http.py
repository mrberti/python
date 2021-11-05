#%%
import re
import gc
try:
    import utils
    import machine
    import ntptime
    import board
    machine.freq(160000000)
    utils.STA_IF.config(dhcp_hostname="http_serv")
    utils.do_connect()
    ntptime.settime()
    led = utils.LED(board.LED_PIN_NO, board.LED_LOGIC_INVERTED)
    del machine
    del ntptime
    del utils
except ImportError:
    pass

gc.collect()

import http_serv as http

def index(request):
    headers = {
        "Location": "/index.html",
    }
    return "", 301, headers

def static(request):
    filepath = "static/" + request.path_matches[1]
    if "../" in filepath:
        return "Relative filepaths are not allowed!", 400
    try:
        return http.HTTPFileResponse(filepath)
    except Exception as exc:
        return str(exc), 404

def api_led(request):
    if request.method == "GET":
        state = "on" if led.is_on() else "off"
        result = {"led": {"state": state}}
    else:
        params = request.params
        if not "state" in params:
            return "Parameter `state` is not set", 400
        state = params["state"].lower()
        if state == "on":
            led.on()
        elif state == "off":
            led.off()
        elif state == "toggle":
            led.toggle()
            state = "on" if led.is_on() else "off"
        else:
            return "Parameter `state` is wrong", 400
        result = {"led": {"state": state}}
    return result

routes = [
    ("/", index),
    ("/api/led", api_led, ["GET", "POST"]),
    (re.compile(r"^/(.+\..+)"), static),
]

server = http.HTTPServer(routes)
server.run()
