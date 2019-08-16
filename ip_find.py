#!/usr/bin/python3
"""
A simple script to ping all ip addresses within the domain.
Currently only working with unix based interpreters
"""

import subprocess
import time

ip = [192,168,1,1]
pid = list()

for i in range(1,254):
	ip_str = str(ip[0]) + "." + str(ip[1]) + "." + str(ip[2]) + "." + str(i)
	cmd = "ping -c 1 -W 2 " + ip_str + " | grep -i 'bytes from'"
	pid.append(subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE))

for i in range(1,254):
	str = pid[i-1].stdout.read()
	if str != b'':
		print(str.decode())
