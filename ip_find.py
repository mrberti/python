#!/bin/python

import subprocess

ip = [192,168,1,1]

for i in range(1,254):
    ip_str = str(ip[0]) + "." + str(ip[1]) + "." + str(ip[2]) + "." + str(i)
    cmd = "ping -n 1 " + ip_str
    subprocess.call(cmd, shell=True)
