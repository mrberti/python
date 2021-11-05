#%%
import re
try:
    import utils
    import machine
    machine.freq(160000000)
    utils.do_connect()
except:
    pass

try:
    import ntptime
    ntptime.settime()
except ImportError:
    pass

from http_serv import *

def index(request):
    data = "This is my data :)"
    return data

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
    return make_response("asd")

def j(request):
    data = {
        "a": 123,
    }
    if request.params:
        data["params"] = request.params
    return data

def s(request):
    return request.path

routes = [
    ("/", index),
    ("/home", home),
    ("/fail", fail),
    ("/req", req, ["GET", "POST"]),
    ("/j", j),
    (re.compile(r"^/s/(.*)"), s)
]

server = HTTPServer(routes)
server.run()

# %%
