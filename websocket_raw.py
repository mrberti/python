import socket
import base64
import binascii
import hashlib
import re
import time
import struct

PORT = 8000
GUID = b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11"


WSOP_CONT = 0x00
WSOP_TEXT = 0x01
WSOP_BIN = 0x02
WSOP_CLOSE = 0x08
WSOP_PING = 0x09
WSOP_PONG = 0x0A


def demask(payload, mask):
    demasked = ""
    print("Mask Key: {!r}".format(mask))
    for i in range(len(payload)):
        demasked += chr(payload[i] ^ mask[i % 4])
    return demasked

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", PORT))
    sock.listen(5)
    print("listening")
    sock_remote, remote_addr = sock.accept()
    sock_remote.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    data_recv = sock_remote.recv(1024).decode("utf-8")
    # if type(data_recv) == bytes: data_recv = data_recv.decode("utf-8")
    print("{}".format(data_recv))
    if not re.match(r"^GET .*\n\r?\n$", data_recv, re.S):
        sock_remote.close()
        sock.close()
        return
    sec_websocket_key = re.findall(r"sec-websocket-key: (.*)", data_recv, re.I)[0].strip().encode()
    hash_sha1 = hashlib.sha1(sec_websocket_key + GUID).digest()
    sec_websocket_key_response = base64.b64encode(hash_sha1).decode()
    response = (
        "HTTP/1.1 101 Web Socket Protocol Handshake\r\n"
        "Upgrade: WebSocket\r\n"
        "Connection: Upgrade\r\n"
        "Sec-WebSocket-Accept: {}\r\n"
        "Server: TestTest\r\n"
        "Access-Control-Allow-Origin: http://localhost\r\n"
        "Access-Control-Allow-Credentials: true\r\n"
        "\r\n"
    ).format(sec_websocket_key_response)
    print("{!r}".format(response))
    sock_remote.send(response.encode())
    try:
        while 1:
            data_recv = sock_remote.recv(1024)
            if not data_recv:
                raise Exception("Connection closed by remote.")
            print("Data recv: {!r}".format(data_recv))
            fin = True if data_recv[0] & (1<<7) else False
            opcode = data_recv[0] & ((1<<4) - 1)
            if opcode == 8:
                raise Exception("Connection closed by request.")
            is_masked = True if data_recv[1] & (1<<7) else False
            payload_length = data_recv[1] & ((1<<7) - 1)
            masking_key = data_recv[2:6]
            payload = data_recv[6:]
            # print(masking_key)
            data_demasked = demask(payload, masking_key)
            print("Data demasked: {!r}".format(data_demasked))

            # time.sleep(1)
            data_send = struct.pack("BB", data_recv[0], 5) + b"asd\x0d\x0a"
            # data_send = b"\x88\x00\x00\x00\x00\x00"
            print("Data send: {!r}".format(data_send))
            a = sock_remote.send(data_send)
            print(a)
    except KeyboardInterrupt:
        pass
    # except Exception as exc:
    #     print(exc)
    finally:
        sock_remote.close()
        sock.close()

if __name__ == "__main__":
    main()
