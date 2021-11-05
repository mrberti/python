#%%
import re
import gc
try:
    import utils
    import machine
    import ntptime
    machine.freq(160000000)
    utils.STA_IF.config(dhcp_hostname="http_serv")
    utils.do_connect()
    ntptime.settime()
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

def home(request):
    headers = {
        "Content-Type": "text"
    }
    return "home", headers

def fail(request):
    headers = {
        "Content-Type": "text/plain"
    }
    return "failed", 404, headers

def req(request):
    return http.HTTPResponse("asd")

def j(request):
    data = {
        "a": 123,
    }
    if request.params:
        data["params"] = request.params
    return data

def s(request):
    data = {
        "matches": request.path_matches
    }
    return data

def static(request):
    filepath = "static/" + request.path_matches[1]
    if "../" in filepath:
        return "Relative filepaths are not allowed!", 400
    try:
        return http.HTTPFileResponse(filepath)
    except Exception as exc:
        return str(exc), 404

routes = [
    ("/", index),
    ("/home", home),
    ("/fail", fail),
    ("/req", req, ["GET", "POST"]),
    ("/j", j),
    (re.compile(r"^/s/(.*)"), s),
    (re.compile(r"^/(.+\..+)"), static),
]

server = http.HTTPServer(routes)
server.run()
