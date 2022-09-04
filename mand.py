#!/usr/bin/python

from numpy import interp
from numpy import complex

p = [" ", ".", "o"]

for py in range(40):
	s = ""
	for px in range(80):
  		x0 = interp(px, [0, 60], [-2.5, 1.0])
 		y0 = interp(py, [0, 40], [-1.0, 1.0])
		x = 0.0
		y = 0.0
		i = 0
		max = 1000
		#while(x*x + y*y <= 2*2 and i < max):
		#	xtemp = x*x - y*y + x0
		#	y = 2*x*y + y0
		#	x = xtemp
		#	i = i + 1
		rs = 0
		iis = 0
		zs = 0
		while(rs + iis <= 4 and i < max):
			x = rs - iis + x0
			y = zs - rs - iis + y0
			rs = x*x
			iis = y*y
			zs = (x + y)*(x + y)
			i = i + 1
		if i > 500:
			s = s + " "
		else:
			s = s + "."
	print(s)
