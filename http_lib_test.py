import http.client
import time

host = "127.0.0.1"
# host = "192.168.1.80"
# host = "localhost"
port = 8080
timeout = None
n_runs = 1

conn_str = f"{host}:{port}"
# conn = http.client.HTTPConnection(conn_str, timeout=timeout)
conn = http.client.HTTPConnection(conn_str)
headers = {
    # "Connection": "keep-alive",
    "Connection": "close",
}
headers = {}
start_time = time.time()

for i in range(n_runs):
    conn.request("GET", "/", headers=headers)
    result = conn.getresponse()
    result.headers
    result.read()
diff_time = time.time() - start_time
print(f"Time needed: {diff_time:.2f} => {diff_time / n_runs:.2f} per request")

print("press ctrl+c to close the connection")
while True:
    try:
        time.sleep(1)
    except KeyboardInterrupt:
        break
