#!/usr/bin/python

import serial
import time
import sys
import platform
import subprocess
from pynput import keyboard, mouse


def getScreenResolution():
	output = subprocess.Popen('xrandr | grep "\*" | cut -d" " -f4',shell=True, stdout=subprocess.PIPE).communicate()[0]
	resolution = output.split()[0].split(b'x')
	return {"x": int(resolution[0]), "y": int(resolution[1])}
	 

def moveMouseTo(mouseCTRL, Newpos):
	x, y = mouseCTRL.position
	dx = Newpos["x"] - x
	dy = Newpos["y"] - y
	mouseCTRL.move(dx, dy)
	return


def readDataFromSerial(ser):
	data = {}
	line = ser.readline()

	while line != "__MOUSE_STATUS__\r\n":
		line = ser.readline()

	# READING DATA
	data["BTN1"] = (ser.readline().split("\r\n")[0].split(" ")[1] == "1")
	data["BTN2"] = (ser.readline().split("\r\n")[0].split(" ")[1] == "1")
	data["BTN3"] = (ser.readline().split("\r\n")[0].split(" ")[1] == "1")
	data["BTN4"] = (ser.readline().split("\r\n")[0].split(" ")[1] == "1")
	data["GX"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["GY"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["GZ"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AX"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AY"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AZ"] = float(ser.readline().split("\r\n")[0].split(" ")[1])

	# TRESHOLD PARAMETERS
	gyro_min = 3
	gyro_max = 30
	accel_min = 0.3
	accel_max = 20

	if abs(data["GX"]) < gyro_min:
		data["GX"] = 0
	if abs(data["GY"]) < gyro_min:
		data["GY"] = 0
	if abs(data["GZ"]) < gyro_min:
		data["GZ"] = 0

	if abs(data["AX"]) < accel_min:
		data["AX"] = 0
	if abs(data["AY"]) < accel_min:
		data["AY"] = 0
	if abs(data["AZ"]) < accel_min:
		data["AZ"] = 0
	return data


# -------------------------------------------------------
# - MAIN -
# -------------------------------------------------------
serialPORT = serial.Serial("/dev/ttyUSB0", 115200)

mouseCTRL = mouse.Controller()
mouseCTRL.release(mouse.Button.left)
mouseCTRL.release(mouse.Button.right)

resolution = getScreenResolution()
mousePosition = {}
mousePosition["x"] = resolution["x"]/2
mousePosition["y"] = resolution["y"]/2

keyboardCTRL = keyboard.Controller()

BUTTONS = { "BTN1": False,
			"BTN2": False,
			"BTN3": False,
			"BTN4": False}
BTN4_counter = 0

while True:
	data = readDataFromSerial(serialPORT)

	# BUTTON 1
	if data["BTN1"] and not BUTTONS["BTN1"]:
		mouseCTRL.press(mouse.Button.right)
		BUTTONS["BTN1"] = True
	elif not data["BTN1"] and BUTTONS["BTN1"]:
		mouseCTRL.release(mouse.Button.right)
		BUTTONS["BTN1"] = False

	# BUTTON 2
	if data["BTN2"] and not BUTTONS["BTN2"]:
		mouseCTRL.press(mouse.Button.left)
		BUTTONS["BTN2"] = True
	elif not data["BTN2"] and BUTTONS["BTN2"]:
		mouseCTRL.release(mouse.Button.left)
		BUTTONS["BTN2"] = False

	# BUTTON 3
	if data["BTN3"] and not BUTTONS["BTN3"]:
		BUTTONS["BTN3"] = True
	elif not data["BTN3"] and BUTTONS["BTN3"]:
		BUTTONS["BTN3"] = False

	# BUTTON 4
	if data["BTN4"] and not BUTTONS["BTN4"]:
		BUTTONS["BTN4"] = True

	elif not data["BTN4"] and BUTTONS["BTN4"]:
		BUTTONS["BTN4"] = False
		BTN4_counter = 0

	# MOVE MOUSE CURSOR
	if not BUTTONS["BTN4"] and not BUTTONS["BTN3"]:
		dx =  2*data["AX"] - data["GZ"] + data["GY"]
		dy = - 3*data["AZ"] - data["GX"]
		if (mousePosition["x"] + dx) >= 0 and (mousePosition["x"] + dx) <= resolution["x"]:
			mousePosition["x"] = mousePosition["x"] + 0.8*dx

		if (mousePosition["y"] + dy) >= 0 and (mousePosition["y"] + dy) <= resolution["y"]:
			mousePosition["y"] = mousePosition["y"] + 0.8*dy
		# --- !!! ---
		moveMouseTo(mouseCTRL, mousePosition)
	
	# SCROLL
	if BUTTONS["BTN3"]:
		mouseCTRL.scroll((- 3*data["AZ"] - data["GX"])/5, (3*data["AZ"] + data["GX"])/5)
	
	# STOP OR RESET MOUSE CURSOR
	if BUTTONS["BTN4"] and BTN4_counter > 50:
		BTN4_counter = 0;
		mousePosition = getScreenResolution()
		mousePosition["x"] = mousePosition["x"]/2
		mousePosition["y"] = mousePosition["y"]/2
	elif BUTTONS["BTN4"]:	
		BTN4_counter += 1


	# PRESSING UP KEY
	if data["AZ"] > 0.5 and data["GX"] < -10 and BUTTONS["BTN4"]:
		keyboardCTRL.press(keyboard.Key.up)
		keyboardCTRL.release(keyboard.Key.up)


	"""
	if data["GZ"] > 20 and BUTTONS["BTN4"]:
		keyboardCTRL.press(keyboard.Key.ctrl)
		keyboardCTRL.press(keyboard.Key.alt)
		keyboardCTRL.press(keyboard.Key.left)
		keyboardCTRL.release(keyboard.Key.ctrl)
		keyboardCTRL.release(keyboard.Key.alt)
		keyboardCTRL.release(keyboard.Key.left)

	if data["GZ"] < -20 and BUTTONS["BTN4"]:
		keyboardCTRL.press(keyboard.Key.ctrl)
		keyboardCTRL.press(keyboard.Key.alt)
		keyboardCTRL.press(keyboard.Key.right)
		keyboardCTRL.release(keyboard.Key.ctrl)
		keyboardCTRL.release(keyboard.Key.alt)
		keyboardCTRL.release(keyboard.Key.right)
	

	print("------------------------------------------------")
	print("GX: " + str(data["GX"]))
	print("GY: " + str(data["GY"]))
	print("GZ: " + str(data["GZ"]))
	print("AX: " + str(data["AX"]*10))
	print("AY: " + str(data["AY"]*10))
	print("AZ: " + str(data["AZ"]*10))
	print(mousePosition)

	"""
