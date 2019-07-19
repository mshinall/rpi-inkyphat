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

ink = InkyPHAT("black")
ink.set_border(ink.BLACK)

#print("w:" + str(ink.WIDTH) + " h:" + str(ink.HEIGHT))

img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the FredokaOne font
#font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 22)
font = ImageFont.truetype("/usr/local/lib/python2.7/dist-packages/font_source_sans_pro/files/SourceSansPro-Black.ttf", 22)
btn.set_pixel(0, 0, 0)

def blink():
	btn.set_pixel(0,255,0)
        time.sleep(0.1)
        btn.set_pixel(0,0,0)

def text(x, y, text):
	global font
	#draw.text((x+2, y+2), text, ink.BLACK, font=font)
	#draw.text((x+1, y+1), text, ink.WHITE, font=font)
	draw.text((x+0, y+0), text, ink.BLACK, font=font)

def winfo():
	out = os.popen('echo `iwconfig wlan0 | egrep "ESSID|Link Quality"`').read()
	m = re.search('^.*ESSID:"([\w.]*)".*Link Quality=(\d*)/(\d*).*$', out)
	id = m.group(1)
	n = int(m.group(2))
	d = int(m.group(3))
	s = int(interp(n, [0, d], [0, 100]))
	#print(id + " " + str(n) + "/" + str(d) + " " + str(s) + "/" + str(width))
	return [id, s]

def show():
	ink.set_image(img)
	ink.show()

def clear():
	draw.rectangle([(0, 0), (ink.WIDTH, ink.HEIGHT)], fill=ink.WHITE)

def blank():
	blink()
	clear()
	show()

def clock():
	blink()
	clear()
	now = localtime()
	text(30, 20, strftime("%a %b %d %Y", now))
	text(45, 50, strftime("%I:%M:%S %p", now))
	show()

def ip():
	blink()
	clear()
	[wfid, wfsig] = winfo()
	myip = os.popen('echo `ifconfig | grep -A1 wlan0` | awk \'{print $6}\'').read()
	text(10, 0,  "ssid: " + wfid)
	text(10, 30, " str: " + str(wfsig) + "%")
	text(10, 60, "  ip: " +  myip)
	show()

def info():
	blink()
	clear()
	temp = os.popen("vcgencmd measure_temp").read()
	tm = re.search("temp=([\d]*).?([\d]*)'C", temp)
	tc = int(tm.group(1))
	tf = tc * (9 / 5) + 32
	text(10, 0, "temp: " + str(tf) + "'F / " + str(tc) + "'C")

	volt = os.popen("vcgencmd measure_volts").read()
	vm = re.search("volt=([\d]*).?([\d]*)V", volt)
	v = float(vm.group(1) + "." + vm.group(2))
	text(10, 30, "volts: " + str(v) + "v")

	stor = os.popen("echo `df -h | grep /dev/root | awk '{ print $4\"/\"$2 }'`").read()
	text(10, 60, "disk: " + str(stor))
	show()

@btn.on_hold(btn.BUTTON_E, hold_time=1)
def handler(button):
	clock()

@btn.on_hold(btn.BUTTON_D, hold_time=1)
def handler(button):
	ip()

@btn.on_hold(btn.BUTTON_B, hold_time=1)
def handler(button):
	info()

@btn.on_hold(btn.BUTTON_A, hold_time=1)
def handler(button):
	blank()

#clock()
signal.pause()

