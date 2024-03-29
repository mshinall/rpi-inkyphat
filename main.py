#!/usr/bin/python
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
import requests
from bs4 import BeautifulSoup
import random
import logging

logging.basicConfig(level=logging.ERROR)

ink = InkyPHAT("black")
ink.set_border(ink.WHITE)

logging.debug("w:" + str(ink.WIDTH) + " h:" + str(ink.HEIGHT))

img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
draw = ImageDraw.Draw(img)

# Load the FredokaOne font
#font = ImageFont.truetype(inkyphat.fonts.FredokaOne, 22)
font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 20)
font_small = ImageFont.truetype("usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf", 14)
btn.set_pixel(0, 0, 0)

is_busy = False
last_func = None

wth_summary_map = {
	"snow":                "Snow",
	"sleet":               "Sleet",
	"rain":                "Rain",
	"fog":                 "Fog",
	"cloudy":              "Cloudy",
	"partly-cloudy-day":   "Partly Cloudy",
	"partly-cloudy-night": "Partly Cloudy",
	"clear-day":           "Clear",
	"clear-night":         "Clear",
	"wind":                "Wind"
}

def blink():
	logging.debug("blink")
	btn.set_pixel(0,127,0)
	time.sleep(0.1)
	btn.set_pixel(0,0,0)
	logging.debug("blink done")

def text(x, y, text, font):
	logging.debug("text: " + text)
	if x < 0:
		logging.debug("text0.5")
		[l, t, r, b] = font.getbbox(text);
		w = r - l
		logging.debug("text0.51")
		x = (ink.WIDTH / 2) - (w / 2)
		logging.debug("text0.52")	
	logging.debug("text1")
	draw.text((x, y), text, ink.BLACK, font=font)
	#logging.debug("[" + str(x) + "," +str(y) + "] " + text);
	logging.debug("text done")

def winfo():
	out = os.popen('echo `iwconfig wlan0 | egrep "ESSID|Link Quality"`').read()
	m = re.search('^.*ESSID:"([\w\-.]*)".*Link Quality=(\d*)/(\d*).*$', out)
	id = m.group(1)
	n = int(m.group(2))
	d = int(m.group(3))
	s = int(interp(n, [0, d], [0, 100]))
	#logging.debug(id + " " + str(n) + "/" + str(d) + " " + str(s) + "/" + str(width))
	return [id, s]

def get_request(url):
	res = requests.get(url)
	if res.status_code != 200:
		return None
	soup = BeautifulSoup(res.content, "lxml")
	return soup

def weather(coords):
	weather = {}
	soup = get_request("https://darksky.net/forecast/{}/us12/en".format(",".join([str(c) for c in coords])))
	if soup == None:
		return None

	curr = soup.find_all("span", "currently")
	weather["summary"] = curr[0].img["alt"].split()[0]
	weather["temperature"] = int(curr[0].find("span", "summary").text.split()[0][:-1])
	press = soup.find_all("div", "pressure")
	weather["pressure"] = int(press[0].find("span", "num").text)
	weather["short_summary"] = wth_summary_map[weather["summary"]]
	return weather

def busy():
	logging.debug("busy")
	global is_busy
	if is_busy:
		return True
	else:
		is_busy = True
		return False

def free():
	logging.debug("free")
	global is_busy
	if is_busy:
		is_busy = False
		return False
	else:
		return True
		
def do(func):
	logging.debug("do")
	global last_func
	if busy():
		logging.debug("busy: " + func.__name__)
		return
	logging.debug("free: " + func.__name__)
	blink()
	logging.debug("set pixel on")
	btn.set_pixel(0, 0, 127)
	logging.debug("assign to last func")
	last_func = func
	logging.debug("call funk")
	func()
	logging.debug("set pixel off")
	btn.set_pixel(0, 0, 0)
	logging.debug("set to free")
	free()
	logging.debug("do done")
	
def show():
	ink.set_image(img)
	ink.show()

def clear():
	draw.rectangle([(0, 0), (ink.WIDTH, ink.HEIGHT)], fill=ink.WHITE)

def blank():
	clear()
	show()

def clock():
	logging.debug("clock")
	clear()
	now = localtime()
	text(-1, 0, strftime("%a %b %d %Y", now), font_large)
	text(-1, 23, strftime("%I:%M:%S %p", now), font_large)

	here = geocoder.ip('me')
	text(-1, 23*2, here.city + " " + here.state, font_large)
	
	wth = weather(here.latlng)
	if wth == None:
		text(-1, 23*3, "[Weather Not Available]", font_small)
	else:		
		text(-1, 23*3, str(wth["temperature"]) + "'F " + wth["short_summary"], font_large)
	show()
	logging.debug("clock done")

def info():
	logging.debug("info")
	clear()
	temp = os.popen("vcgencmd measure_temp").read()
	tm = re.search("temp=([\d]*).?([\d]*)'C", temp)
	tc = int(tm.group(1))
	tf = tc * (9 / 5) + 32
	text(0, 0, "temp: " + str(int(tf)) + "'F / " + str(int(tc)) + "'C", font_small)

	volt = os.popen("vcgencmd measure_volts").read()
	vm = re.search("volt=([\d]*).?([\d]*)V", volt)
	v = float(vm.group(1) + "." + vm.group(2))
	text(0, 16, "volt: " + str(v) + "v", font_small)

	stor = os.popen("echo `df -h | grep /dev/root | awk '{ print $4\"/\"$2 }'`").read()
	text(0, 16*2, "disk: " + str(stor), font_small)

	up = os.popen("uptime").read()
	um1 = re.search("[\d:]*\s+up\s+(\d+):(\d+)", up)
	um2 = re.search("[\d:]*\s+up\s+(\d*)\s+(\w*),", up)
	if um2 and um2.group(1) and um2.group(2):
		text(0, 16*3, "  up: " + str(um2.group(1) + " " + um2.group(2)), font_small)
	elif um1 and um1.group(1) and um1.group(2):
		m = um1.group(1)
		h = um1.group(2)
		ms = "min"
		hs = "hr"
		if int(m) > 1:
			ms = "mins"
		if int(h) > 1:
			hs = "hrs"
		text(0, 16*3, "  up: " + str(h) + " " + hs + " " + str(m) + " " + ms, font_small)
	else:
		text(0, 16*3, "  up: (error)", font_small)

	[wfid, wfsig] = winfo()
	myip = os.popen('echo `ifconfig | grep -A1 wlan0` | awk \'{print $6}\'').read()
	text(0, 16*4,  "wifi: " + wfid + " (" + str(wfsig) + "%)", font_small)
	text(0, 16*5, "  ip: " +  myip, font_small)
	show()
	logging.debug("info done")

def image():
	logging.debug("image")
	global zc, zz #, img, draw
	#img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
	#draw = ImageDraw.Draw(img)
	i = random.choice([1, 2, 4, 8, 16, 32, 52])
	t = 212
	r = 104
	for a in range(0, int(t/i)+1):
		x1 = a*i+1
		x2 = x1 + i
		if x2 > t:
			x2 = x1 + t - t/i
		for b in range(0, int(r/i)+1):
			y1 = b*i+1
			y2 = y1 + i
			if y2 > r:
				y2 = y1 + r - r/i
			color = random.choice([ink.WHITE, ink.BLACK, ink.RED])
			draw.rectangle([x1, y1, x2, y2], fill=color, outline=None, width=0)
	show()
	logging.debug("image done")

def mandel():
	logging.debug("mandel")
	global img, draw
	palette = [ink.WHITE, ink.RED, ink.BLACK]
	img = Image.new("P", (ink.WIDTH, ink.HEIGHT))
	draw = ImageDraw.Draw(img)
	h = ink.HEIGHT
	w = ink.WIDTH
	for py in range(h):
		for px in range(w):
			x0 = interp(px, [0, w], [-2.5, 1.0])
			y0 = interp(py, [0, h], [-1.0, 1.0])
			x = 0.0
			y = 0.0
			i = 0
			max = 100
			rs = 0
			iis = 0
			zs = 0
			color = None
			while(rs + iis <= 4 and i < max):
				x = rs - iis + x0
				y = zs - rs - iis + y0
				rs = x*x
				iis = y*y
				zs = (x + y)*(x + y)
				i = i + 1
			if i > max / 2:
				draw.point([px, py], fill=ink.BLACK)			
			else:
				draw.point([px, py], fill=ink.WHITE)
	show()
	logging.debug("mandel done")

@btn.on_hold(btn.BUTTON_E, hold_time=1)
def handler(button):
	do(clock)

@btn.on_hold(btn.BUTTON_D, hold_time=1)
def handler(button):
	do(info)

@btn.on_hold(btn.BUTTON_B, hold_time=1)
def handler(button):
	do(image)

@btn.on_hold(btn.BUTTON_A, hold_time=1)
def handler(button):
	do(mandel)

try:
	logging.debug("try block")
	#do(clock)
	#do(image)
	#do(mandel)
	do(info)
	time.sleep(300)
	logging.debug("while check")
	while True:
		logging.debug("while block")
		do(last_func)
		time.sleep(300)
	#signal.pause()
except:
	exit()

