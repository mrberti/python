#!/usr/bin/env python
from math import *

max_N = 999999

for i in range(max_N):
	x = sqrt(i)
	if i % (max_N/10) == 0:
		print "Loop: " + str(i) + ", x = " + str(x)
