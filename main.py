#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from inky import InkyPHAT
from PIL import Image, ImageDraw, ImageFont
import inkyphat
from time import localtime, strftime
import buttonshim as btn
import signal
import os
import re
from numpy import interp
import geocoder

ink = InkyPHAT("black")
ink.set_border(ink.WHITE)

#print("w:" + str(ink.WIDTH) + " h:" + str(ink.HEIGHT))

img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the FredokaOne font
#font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 22)
font_large = ImageFont.truetype("/usr/local/lib/python2.7/dist-packages/font_source_sans_pro/files/SourceSansPro-Black.ttf", 22)
font_small = ImageFont.truetype("/usr/local/lib/python2.7/dist-packages/font_source_sans_pro/files/SourceSansPro-Black.ttf", 16)
btn.set_pixel(0, 0, 0)

is_busy = False

def blink():
	btn.set_pixel(0,255,0)
        time.sleep(0.1)
        btn.set_pixel(0,0,0)

def text(x, y, text, font):
	draw.text((x, y), text, ink.BLACK, font=font)
	#print("[" + str(x) + "," +str(y) + "] " + text);

def winfo():
	out = os.popen('echo `iwconfig wlan0 | egrep "ESSID|Link Quality"`').read()
	m = re.search('^.*ESSID:"([\w.]*)".*Link Quality=(\d*)/(\d*).*$', out)
	id = m.group(1)
	n = int(m.group(2))
	d = int(m.group(3))
	s = int(interp(n, [0, d], [0, 100]))
	#print(id + " " + str(n) + "/" + str(d) + " " + str(s) + "/" + str(width))
	return [id, s]

def busy():
	global is_busy
	if(is_busy):
		return True
	else:
		is_busy = True
		return False

def free():
	global is_busy
	if(is_busy):
		is_busy = False
		return False
	else:
		return True
def do(func):
	if(busy()):
		print("busy: " + func.__name__)
		return
	print("free: " + func.__name__)
	blink()
	btn.set_pixel(0, 0, 127)
	func()
	btn.set_pixel(0, 0, 0)
	free()
	
def show():
	ink.set_image(img)
	ink.show()

def clear():
	draw.rectangle([(0, 0), (ink.WIDTH, ink.HEIGHT)], fill=ink.WHITE)

def blank():
	clear()
	show()

def clock():
	clear()
	now = localtime()
	text(30, 0, strftime("%a %b %d %Y", now), font_large)
	text(45, 22, strftime("%I:%M:%S %p", now), font_large)

	here = geocoder.ip('me')
	text(30, 22*2, here.city + " " + here.state, font_large)

	show()

def ip():
	clear()
	[wfid, wfsig] = winfo()
	myip = os.popen('echo `ifconfig | grep -A1 wlan0` | awk \'{print $6}\'').read()
	text(10, 0,  "ssid: " + wfid, font_large)
	text(10, 30, "str: " + str(wfsig) + "%", font_large)
	text(10, 60, "ip: " +  myip, font_large)
	show()

def info():
	clear()
	temp = os.popen("vcgencmd measure_temp").read()
	tm = re.search("temp=([\d]*).?([\d]*)'C", temp)
	tc = int(tm.group(1))
	tf = tc * (9 / 5) + 32
	text(10, 0, "temp: " + str(tf) + "'F / " + str(tc) + "'C", font_small)

	volt = os.popen("vcgencmd measure_volts").read()
	vm = re.search("volt=([\d]*).?([\d]*)V", volt)
	v = float(vm.group(1) + "." + vm.group(2))
	text(10, 16, "volts: " + str(v) + "v", font_small)

	stor = os.popen("echo `df -h | grep /dev/root | awk '{ print $4\"/\"$2 }'`").read()
	text(10, 16*2, "disk: " + str(stor), font_small)

	up = os.popen("uptime").read()
	um1 = re.search("[\d:]*\s+up\s+([\d:]*)", up)
	um2 = re.search("[\d:]*\s+up\s+([\d]*)\s+(\w*),", up)
	if(um2 and um2.group(1) and um2.group(2)):
		text(10, 16*3, "up: " + str(um2.group(1) + " " + um2.group(2)), font_small)
	elif(um1 and um1.group(1)):
		text(10, 16*3, "up: " + str(um1.group(1)), font_small)
	else:
		text(10, 16*3, "up: (error)", font_small)

	[wfid, wfsig] = winfo()
	myip = os.popen('echo `ifconfig | grep -A1 wlan0` | awk \'{print $6}\'').read()
	text(10, 16*4,  "wifi: " + wfid + " (" + str(wfsig) + "%)", font_small)
	text(10, 16*5, "ip: " +  myip, font_small)
	show()

@btn.on_hold(btn.BUTTON_E, hold_time=1)
def handler(button):
	do(clock)

@btn.on_hold(btn.BUTTON_D, hold_time=1)
def handler(button):
	do(ip)

@btn.on_hold(btn.BUTTON_B, hold_time=1)
def handler(button):
	do(info)

@btn.on_hold(btn.BUTTON_A, hold_time=1)
def handler(button):
	do(blank)

do(clock)
signal.pause()

