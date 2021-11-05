#%%
from http_serv import *
try:
    import utils
    utils.do_connect()
except:
    pass

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

routes = [
    ("/", index),
    ("/home", home),
    ("/fail", fail),
    ("/req", req, ["GET", "POST"]),
    ("/j", j),
]

server = HTTPServer(routes)
server.run()

# %%
