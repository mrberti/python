"""
Extremely simple and basic HTTP handling! Do not expect anything.

For small devices, e.g. ESP8266, it is required to compile this file
into a *.mpy file. Use the `mpy_cross` tool to do that.
"""
import json
import socket
import os
import time # delete
import gc

# wrap datetime handling
try:
    from machine import RTC
    rtc = RTC()
    USE_RTC = True
    IS_MICROPYTHON = True
except ImportError:
    from datetime import datetime
    USE_RTC = False
    IS_MICROPYTHON = False

HEADER_DEFAULT_SERVER = "http_serv/0.0.1a"
HEADER_DEFAULT_CONTENT_TYPE = "text/plain"
HEADER_DEFAULT_BINARY_TYPE = "application/octet-stream"
HEADER_ENCODING = "ascii"
RECV_BUF_SIZE = 1024
SEND_CHUNK_SIZE = 1024

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
    "HTTP/1.1",
]

http_status_codes = {
    # Just the most important HTTP status codes
    200: "OK",
    301: "Moved Permanently",
    400: "Bad Request",
    404: "Not Found",
    500: "Internal Server Error",
    505: "HTTP Version not supported",
}

mime_types = {
    # Just the basic stuff
    ".css": "text/css",
    ".csv": "text/csv",
    ".gif": "image/gif",
    ".htm": "text/html,",
    ".html": "text/html,",
    ".ico": "image/vnd.microsoft.icon",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".js": "text/javascript",
    ".json": "application/json",
    ".png": "image/png",
    ".pdf": "application/pdf",
    ".svg": "image/svg+xml",
    ".txt": "text/plain",
    ".xhtml": "application/xhtml+xml",
    ".zip": "application/zip",
}

def create_headers(headers):
    header = ""
    for k in headers.keys():
        header += "{}: {}\r\n".format(k, headers[k])
    return header

def create_date():
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
        wd=wd, d=d, mo=mo, y=y, h=h, m=m, s=s)
    return date_str

def guess_mime_type(path):
    extension = "." + path.split(".")[-1].lower()
    return mime_types.get(extension, HEADER_DEFAULT_CONTENT_TYPE)


class HTTPRequest(object):
    def __init__(self, socket=None):
        self.method = None
        self.url = None
        self.path = None
        self.path_matches = []
        self.params = {}
        self.protocol = None
        self.is_1_0 = None
        self.headers = {}
        self.data = None
        if socket is not None:
            self.parse(socket)

    def parse(self, socket):
        # See also:
        # https://github.com/micropython/micropython/blob/master/examples/network/http_server.py
        if IS_MICROPYTHON:
            stream = socket
        else:
            stream = socket.makefile("rwb")

        # First Line
        first_line = stream.readline().decode(HEADER_ENCODING).strip()
        print("<" * 40)
        print(first_line)
        try:
            self.method, self.url, self.protocol = first_line.split(" ")
        except ValueError:
            raise Exception("The first line is not valid HTTP: {}".format(first_line))
        self.method = self.method.upper()
        if self.method not in http_methods:
            raise Exception("Unsupported HTTP method: {}".format(self.method))
        self.protocol = self.protocol.upper()
        if self.protocol not in http_protocols:
            raise Exception("Unsupported HTTP protocol: {}".format(self.protocol))
        self.is_1_0 = "1.0" in self.protocol
        self.parse_url()

        # Headers (until empty line found)
        while True:
            line = stream.readline().decode(HEADER_ENCODING)
            if line == "\r\n":
                break
            try:
                k, v = line.strip().split(": ")
                self.headers[k.lower()] = v
            except ValueError:
                raise Exception("Invalid header: {}".format(line))
        print(create_headers(self.headers))

        # Data
        data_length = int(self.headers.get("content-length", 0))
        if data_length > 0:
            # HACK: This is still a little bit strange...
            socket.settimeout(10.)
            if IS_MICROPYTHON:
                self.data = stream.recv(1024)
            else:
                self.data = stream.peek()
            if len(self.data) > 40:
                print(self.data[0:20], "...", self.data[-20:])
            else:
                print(self.data)

        if not IS_MICROPYTHON:
            stream.close()
        print("<" * 40)

    def parse_url(self):
        self.path_matches = []
        self.params = {}
        splitted_url = self.url.split("?")
        self.path = splitted_url[0]
        if len(splitted_url) > 1:
            splitted_params = splitted_url[1].split("&")
            for param in splitted_params:
                k, v = param.split("=")
                self.params[k] = v

    def __str__(self):
        return (
            "{method} {url} {protocol}\r\n"
            "{headers}"
            "\r\n"
            "{data}".format(
                method=self.method,
                url=self.url,
                protocol=self.protocol,
                headers=create_headers(self.headers),
                data=self.data if self.data else ""
            ))

class HTTPResponse(object):
    def __init__(self, data, status_code=200, headers=None, protocol="HTTP/1.1"):
        self.status_code = status_code
        self.reason = http_status_codes.get(status_code, "NA")
        if headers is None:
            self.headers = {}
        else:
            self.headers = headers
        self.data = data
        self.protocol = protocol.upper()
        self._create_basic_headers()

    def __str__(self):
        return (
            "{protocol} {status_code} {reason}\r\n"
            "{headers}"
            "\r\n"
            "{data}".format(
                protocol=self.protocol,
                status_code=self.status_code,
                reason=self.reason,
                headers=create_headers(self.headers),
                data=self.data if self.data and not self.is_binary_data() else ""
            ))

    def is_binary_data(self):
        return isinstance(self.data, bytes)

    def encoded(self):
        response = str(self).encode(HEADER_ENCODING)
        if self.is_binary_data():
            response = response + self.data
        return response

    def _create_basic_headers(self):
        self._headers_lower = [k.lower() for k in self.headers.keys()]
        if "date" not in self._headers_lower:
            self.headers["Date"] = create_date()
        if "server" not in self._headers_lower:
            self.headers["Server"] = HEADER_DEFAULT_SERVER
        if "connection" not in self._headers_lower:
            self.headers["Connection"] = "close"
        if "content-length" not in self._headers_lower:
            if self.data:
                self.headers["Content-Length"] = len(self.data)
            # else:
            #     self.headers["Content-Length"] = 0
        if "content-type" not in self._headers_lower:
            if self.data:
                if self.is_binary_data():
                    self.headers["Content-Type"] = HEADER_DEFAULT_BINARY_TYPE
                else:
                    self.headers["Content-Type"] = HEADER_DEFAULT_CONTENT_TYPE
        if "access-control-allow-origin" not in self._headers_lower:
            # experimental
            self.headers["Access-Control-Allow-Origin"] = "*"

class HTTPFileResponse(HTTPResponse):
    def __init__(self, filepath, status_code=200, headers=None, protocol="HTTP/1.1", mime_type=None):
        super().__init__(data=b"", status_code=status_code, headers=headers, protocol=protocol)
        self.filepath = filepath
        self.set_mime_type(mime_type)
        self.set_content_length()
        # Let this escalate. The creator shall handle the errors.
        self._file = open(filepath, "rb")

    def __del__(self):
        self.close()

    def set_mime_type(self, mime_type=None):
        if mime_type is None:
            mime_type = guess_mime_type(self.filepath)
        self.headers["Content-Type"] = mime_type

    def set_content_length(self, length=None):
        if length is None:
            length = os.stat(self.filepath)[6]
        self.length = length
        self.headers["Content-Length"] = length

    def get_chunk(self, chunk_size=SEND_CHUNK_SIZE):
        return self._file.read(chunk_size)

    def close(self):
        if self._file:
            self._file.close()
            self._file = None

class HTTPServer(object):
    def __init__(self, routes, server_address=("", 80)):
        self.routes = routes
        self.server_address = server_address
        self.running = False

    def __del__(self):
        self.close()

    def close(self):
        self.socket.close()

    def run(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.socket.listen(5)
        self.running = True
        while self.running:
            print("Waiting for clients...")
            self.remote_socket, remote_info = self.socket.accept()
            print("Remote connected: {}".format(remote_info))
            start = time.time_ns()

            # Parse the HTTP Request
            try:
                request = HTTPRequest(self.remote_socket)
            except Exception as exc:
                self.bad_request(str(exc))
                continue

            # Get the route and execute the callback
            cb = self._get_route_cb(request)
            if not cb:
                self.not_found()
                continue
            try:
                cb_res = cb(request)
            except Exception as exc:
                self.internal_error(str(exc))
                continue

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
            print("Required time: {} ms".format((time.time_ns() - start) / 1000000))
            if IS_MICROPYTHON:
                print("Memory free: {} kB".format(gc.mem_free() / 1024))

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
    
    def internal_error(self, data=None):
        response = HTTPResponse(data, 500)
        self.finish(response)

    def finish(self, response):
        if isinstance(response, HTTPFileResponse):
            self.remote_socket.send(response.encoded())
            while True:
                chunk = response.get_chunk()
                if not chunk:
                    break
                try:
                    self.remote_socket.sendall(chunk)
                except OSError:
                    break
            response.close()
        else:
            self.remote_socket.send(response.encoded())
        self.remote_socket.close()
        print(">" * 40)
        print(response)
        print(">" * 40)

def jsonify(data, status_code=200, headers=None):
    if headers is None:
        headers = {}
    headers["Content-Type"] = "application/json"
    data = json.dumps(data)
    return HTTPResponse(data, status_code, headers)
