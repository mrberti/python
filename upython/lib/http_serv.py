"""
Extremely simple and basic HTTP handling! Do not expect anything.
"""
import json
import re
import socket
import time # delete

# wrap datetime handling
try:
    from machine import RTC
    rtc = RTC()
    USE_RTC = True
except ImportError:
    from datetime import datetime
    USE_RTC = False

HEADER_DEFAULT_SERVER = "http_serv/0.0.1a"
HEADER_DEFAULT_CONTENT_TYPE = "text/plain"
BASE_ENCODING = "utf-8"

try:
    IGNORECASE = re.IGNORECASE
except AttributeError:
    IGNORECASE = 2

http_methods = [
    "GET",
    "HEAD",
    "POST",
    "PUT",
    "DELETE",
    "CONNECT",
    "OPTIONS",
    "TRACE",
    "PATCH",
]

http_protocols = [
    "HTTP/1.0",
    "HTTP/1.1",
]

http_status_codes = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    505: "HTTP Version not supported",
}

week_days = {
    0: "Sun",
    1: "Mon",
    2: "Wed",
    3: "Thu",
    4: "Fri",
    5: "Sat",
    6: "Sun",
}

month = {
    1: "Jan",
    2: "Feb",
    3: "Mar",
    4: "Apr",
    5: "May",
    6: "Jun",
    7: "Jul",
    8: "Aug",
    9: "Sep",
    10: "Oct",
    11: "Nov",
    12: "Dec",
}

re_method_str = r"({})".format("|".join(http_methods))
re_path_str = r"(/[^ ]*)"
re_protocol_str = r"({})".format("|".join(http_protocols))
re_http_first_line_str = r"^" + re_method_str + r" " + re_path_str + r" " + re_protocol_str + r"\r?$"

# re_method = re.compile(re_method_str, IGNORECASE)
# re_url = re.compile(re_path_str, IGNORECASE)
# re_protocol = re.compile(re_protocol_str, IGNORECASE)
re_http_first_line = re.compile(re_http_first_line_str, IGNORECASE)

def get_lines(req, term):
    return req.split(term)

def splitted_packet(req):
    rnrn = req.find("\r\n\r\n")
    nn = req.find("\n\n")
    if rnrn > 0 and nn < 0:
        pos = rnrn + 4
        term = "\r\n"
    elif nn > 0 and rnrn < 0:
        pos = nn + 2
        term = "\n"
    else:
        raise NotImplementedError("Package splitting needs to be improved")
    return (req[0:pos], req[pos:], term)

def parse_headers(lines):
    headers = {}
    for line in lines:
        if line:
            try:
                k, v = line.split(": ")
                headers[k] = v.lower()
            except ValueError:
                raise Exception("INVALID HEADER: {}".format(line))
    return headers

def create_headers(headers):
    header = ""
    for k in headers.keys():
        header += "{}: {}\r\n".format(k, headers[k])
    return header

def create_date():
    if USE_RTC:
        date = rtc.datetime()
        y = str(date[0])
        mo = month.get(date[1])
        wd = week_days.get(date[3])
        d = date[2]
        h = date[4]
        m = date[5]
        s = date[6]
    else:
        # TODO: Timezone correction
        date = datetime.now()
        y = date.year
        mo = month.get(date.month)
        wd = week_days.get(date.weekday())
        d = date.day
        h = date.hour
        m = date.minute
        s = date.second
    date_str = "{wd}, {d:02} {mo} {y}, {h:02}:{m:02}:{s:02} GMT".format(
        wd=wd,
        d=d,
        mo=mo,
        y=y,
        h=h,
        m=m,
        s=s
    )
    return date_str


class HTTPRequest(object):
    def __init__(self, request=None):
        if request is None:
            self.method = None
            self.url = None
            self.path = None
            self.path_matches = []
            self.params = {}
            self.protocol = None
            self.is_1_0 = None
            self.headers = {}
            self.data = None
            self.term = None
        else:
            self.parse(request)

    def parse(self, request):
        http, self.data, self.term = splitted_packet(request)
        lines = get_lines(http, self.term)
        match = re_http_first_line.search(lines[0])
        self.method = match.group(1)
        self.url = match.group(2)
        self.protocol = match.group(3)
        self.is_1_0 = "1.0" in self.protocol
        self.headers = parse_headers(lines[1:])
        self.method = self.method.upper()
        self.path_matches = []
        self.parse_url()

    def parse_url(self):
        self.params = {}
        splitted_url = self.url.split("?")
        self.path = splitted_url[0]
        if len(splitted_url) > 1:
            splitted_params = splitted_url[1].split("&")
            for param in splitted_params:
                k, v = param.split("=")
                self.params[k] = v

class HTTPResponse(object):
    def __init__(self, data, status_code=200, headers={}, protocol="HTTP/1.1"):
        self.status_code = status_code
        self.reason = http_status_codes.get(status_code, "NA")
        self.headers = headers
        self.data = data
        self.protocol = protocol
        self._create_basic_headers()

    def __str__(self):
        return (
            "{protocol} {status_code} {reason}\r\n"
            "{headers}"
            "\r\n"
            "{data}".format(
                protocol=self.protocol.upper(),
                status_code=self.status_code,
                reason=self.reason,
                headers=create_headers(self.headers),
                data=self.data if self.data else ""
            ))

    def encoded(self):
        return str(self).encode(BASE_ENCODING)

    def _create_basic_headers(self):
        self._headers_lower = [k.lower() for k in self.headers.keys()]
        # if "data" not in self._headers_lower:
        #     self.headers["Date"] = # TODO
        if "date" not in self._headers_lower:
            self.headers["Date"] = create_date()
        if "server" not in self._headers_lower:
            self.headers["Server"] = HEADER_DEFAULT_SERVER
        if "connection" not in self._headers_lower:
            self.headers["Connection"] = "close"
        if "content-length" not in self._headers_lower:
            if self.data:
                self.headers["Content-Length"] = len(self.data)
            else:
                self.headers["Content-Length"] = 0
        if "content-type" not in self._headers_lower:
            if self.data:
                self.headers["Content-Type"] = HEADER_DEFAULT_CONTENT_TYPE

class HTTPServer(object):
    def __init__(self, routes, server_address=("", 80)):
        self.routes = routes
        self.server_address = server_address
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def __del__(self):
        self.close()

    def close(self):
        self.socket.close()

    def run(self):
        self.socket.bind(self.server_address)
        self.socket.listen(5)
        self.running = True
        while self.running:
            print("Wating for clients...")
            self.remote_socket, remote_info = self.socket.accept()
            print("Remote connected: {}".format(remote_info))
            start = time.time_ns()
            recv = self.remote_socket.recv(1024).decode(BASE_ENCODING)
            try:
                request = HTTPRequest(recv)
            except Exception as exc:
                self.bad_request(str(exc))
                continue

            # Get the route and execute the callback
            cb = self._get_route_cb(request)
            if not cb:
                self.not_found()
                continue
            cb_res = cb(request)

            # Parse the result of the callback
            # Result can be:
            # - string -> Interpreted as plain text data, if not
            #   otherwise specified
            # - dict -> jsonify
            # - HTTPResponse
            # - (data, status_code)
            # - (data, headers)
            # - (data, status_code, headers)
            if isinstance(cb_res, HTTPResponse):
                response = cb_res
            else:
                status_code = 200
                headers = {}
                data = None
                if isinstance(cb_res, tuple):
                    if len(cb_res) > 1:
                        data = cb_res[0]
                        if len(cb_res) > 2:
                            status_code = int(cb_res[1])
                            headers = cb_res[2]
                        else:
                            try:
                                status_code = int(cb_res[1])
                            except TypeError:
                                headers = cb_res[1]
                else:
                    data = cb_res

                # Create a HTTPResponse and send it to the client
                # Currently, the connection is closed directly therafter
                if isinstance(data, dict):
                    response = jsonify(data, status_code, headers)
                else:
                    response = HTTPResponse(data, status_code, headers)
            self.finish(response)
            print("Required ms: ", (time.time_ns() - start) / 1000000)

    def _get_route_cb(self, request):
        # TODO:
        # - Intuitive named dynamic parameters
        request_path = request.path
        request_method = request.method
        path_match = False
        for route in self.routes:
            if isinstance(route[0], str):
                path_match = request_path == route[0]
            else:
                match = route[0].match(request_path)
                if match:
                    path_match = True
                    request.path_matches = []
                    matches_left = True
                    i = 0
                    while matches_left:
                        try:
                            request.path_matches.append(match.group(i))
                            i += 1
                        except IndexError:
                            matches_left = False
            if path_match:
                if len(route) < 3:
                    if request_method == "GET":
                        return route[1]
                else:
                    if request_method in route[2]:
                        return route[1]
        return None

    def bad_request(self, data=None):
        response = HTTPResponse(data, 400)
        self.finish(response)

    def not_found(self, data=None):
        response = HTTPResponse(data, 404)
        self.finish(response)

    def finish(self, response):
        self.remote_socket.send(response.encoded())
        self.remote_socket.close()

def make_response(data, status_code=200, headers={}):
    return HTTPResponse(data=data, status_code=status_code, headers=headers)

def jsonify(data, status_code=200, headers={}):
    headers["Content-Type"] = "application/json"
    data = json.dumps(data)
    return HTTPResponse(data, status_code, headers)
