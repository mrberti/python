"""
Extremely simple and basic HTTP handling! Do not expect anything.
"""
import json
import re
import socket

HEADER_DEFAULT_SERVER = "http_serv/0.0.1a"
HEADER_DEFAULT_CONTENT_TYPE = "text/plain"

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
    "HTTP/1.1",
]

http_status_codes = {
    200: "OK",
    400: "Bad Request",
    404: "Not Found",
    505: "HTTP Version not supported",
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

class HTTPRequest(object):
    def __init__(self, request=None):
        if request is None:
            self.method = None
            self.url = None
            self.protocol = None
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
        self.headers = parse_headers(lines[1:])
        self.method = self.method.upper()

class HTTPResponse(object):
    def __init__(self, data, status_code=200, headers={}, protocol="HTTP/1.1"):
        self.status_code = status_code
        self.reason = http_status_codes[status_code]
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
        return str(self).encode("ascii")

    def _create_basic_headers(self):
        self._headers_lower = [k.lower() for k in self.headers.keys()]
        # if "data" not in self._headers_lower:
        #     self.headers["Date"] = # TODO
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
            recv = self.remote_socket.recv(1024).decode("ascii")
            try:
                request = HTTPRequest(recv)
            except:
                self.bad_request()
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

    def _get_route_cb(self, request):
        for route in self.routes:
            if request.url == route[0]:
                if len(route) < 3:
                    if request.method == "GET":
                        return route[1]
                else:
                    if request.method in route[2]:
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
    headers["Content-Type"] = "text/json"
    data = json.dumps(data)
    return HTTPResponse(data, status_code, headers)
