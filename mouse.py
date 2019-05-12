#!/usr/bin/python

import serial
import time
import sys
import subprocess
from pynput.mouse import Button, Controller


def getScreenResolution():
    output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
    resolution = output.split()[0].split(b'x')
    resolution = (int(resolution[0]), int(resolution[1]))
    return resolution


def moveMouseTo(mouse, Newpos):
	x, y = mouse.position
	dx = Newpos[0] - x
	dy = Newpos[1] - y
	mouse.move(dx, dy)
	return


# ---------------------------------------------
ser = serial.Serial("/dev/ttyUSB0", 115200)
mouse = Controller()
button = [False, False, None ,False]
counterBTN4 = 0
pos = getScreenResolution()
pos = [ pos[0]/2, pos[1]/2 ]
mouse.release(Button.left)
mouse.release(Button.right)

while True:
	# Reset values
	scroll = 0
	gx = 0
	gy = 0

	# Read new values
	line = ser.readline().split("\r\n")[0]
	if ((line == "BTN1: 1") and (not button[0])):
		mouse.press(Button.right)
		button[0] = True

	elif ((line == "BTN1: 0") and button[0]):
		button[0] = False
		mouse.release(Button.right)

	if ((line == "BTN2: 1") and (not button[1])):
		mouse.press(Button.left)
		button[1] = True

	elif ((line == "BTN2: 0") and button[1]):
		mouse.release(Button.left)
		button[1] = False

	if (line == "BTN4: 1"):
		button[3] = True
		counterBTN4 += 1
		if counterBTN4 > 15:
			pos = getScreenResolution()
			pos = [pos[0]/2, pos[1]/2]
			counterBTN4 = 0
	elif (line == "BTN4: 0"):
		button[3] = False
		counterBTN4 = 0

	if line.split(":")[0] == "GX":
		gx = -float(line.split(" ")[1])
		if abs(gx) < 2:
			gx = 0

	if line.split(":")[0] == "GY":
		gy = -float(line.split(" ")[1])
		if abs(gy) < 2:
			gy = 0

	if line.split(":")[0] == "scroll_d":
		scroll = int(float(line.split(" ")[1]))

	if not button[3] :
		pos[0] = pos[0] + gx
		pos[1] = pos[1] + gy

	moveMouseTo(mouse, pos)
	mouse.scroll(0, scroll/10)
