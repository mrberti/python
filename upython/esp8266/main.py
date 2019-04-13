import mpu6050
import wemos
import time

# time.sleep(5)
while not wemos.STA_IF.isconnected():
    time.sleep(.1)
print("connected")
sock = wemos.tcp_connect("192.168.1.41", 1234)
i = 0
while 1:
    i += 1
    # str_send = "{}:{}:moin\n".format(i, time.ticks_ms())
    rssi = wemos.STA_IF.status("rssi")
    str_send = "{}\n".format(rssi)
    wemos.tcp_send(str_send, sock)
    # wemos.udp_send(str_send, "192.168.1.40", 1234)
    time.sleep(.1)

# mpu6050.main()
# wemos.go_to_sleep(1000)
