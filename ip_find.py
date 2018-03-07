#!/bin/python

import subprocess

ip = [192,168,140,1]

for i in range(1,254):
	ip_str = str(ip[0]) + "." + str(ip[1]) + "." + str(ip[2]) + "." + str(i)
	cmd = "ping -n 1 -w 1000 " + ip_str + "| grep Reply"
	subprocess.Popen(cmd, shell=True)

