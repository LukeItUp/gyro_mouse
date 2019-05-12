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


ser = serial.Serial("/dev/ttyUSB0", 115200)
mouse = Controller()

pos = getScreenResolution()
pos = [ pos[0]/2, pos[1]/2 ]

while True:
	# Reset values
	scroll = 0
	gx = 0
	gy = 0

	# Read new values
	line = ser.readline().split("\r\n")[0]
	if (line == "BTN1: 1"):
		mouse.press(Button.right)
		print("Pressed Right Mouse Button")
	else:
		mouse.release(Button.right)

	if (line == "BTN2: 1"):
		mouse.press(Button.left)
                print("Pressed Left Mouse Button")
	else:
		mouse.release(Button.left)

	if line.split(":")[0] == "GX":
		gx = -int(float(line.split(" ")[1]))

	if line.split(":")[0] == "GY":
		gy = int(float(line.split(" ")[1]))

	if line.split(":")[0] == "scroll_d":
		scroll = int(float(line.split(" ")[1]))


	pos[0] = pos[0] + gx
	pos[1] = pos[1] + gy
	moveMouseTo(mouse, pos)
	mouse.scroll(0, scroll/10)
