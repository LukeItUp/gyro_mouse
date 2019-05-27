#!/usr/bin/python

import serial
import time
import sys
import platform
import subprocess
from pynput import keyboard, mouse
import matplotlib.pyplot as plt


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
	data["GX"] = -float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["GY"] = -float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["GZ"] = -float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AX"] = float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AY"] = -float(ser.readline().split("\r\n")[0].split(" ")[1])
	data["AZ"] = -float(ser.readline().split("\r\n")[0].split(" ")[1])
	
	return data


# -----------------------------------------------------------------------------------
#			MAIN
# -----------------------------------------------------------------------------------
n = 300
serialPORT = serial.Serial("/dev/ttyUSB0", 115200)
GX = []
GY = []
GZ = []

AX = []
AY = []
AZ = []

time_ms = []

# --------------------------------------
#    GATHERING UNFILTERED DATA
# --------------------------------------
for i in range(n):
	if (i % 10) == 0:
		print(str(i/10) + "sec")
	data = readDataFromSerial(serialPORT)
	time_ms.append(i*10)
	GX.append(data["GX"])
	GY.append(data["GY"])
	GZ.append(data["GZ"])
	AX.append(data["AX"])
	AY.append(data["AY"])
	AZ.append(data["AZ"])


# --------------------------------------
#    FILTERED (LOW-PASS)
# --------------------------------------
alpha = 0.9
GX_fLP = [i for i in GX]
GY_fLP = [i for i in GY]
GZ_fLP = [i for i in GZ]

AX_fLP = [i for i in AX]
AY_fLP = [i for i in AY]
AZ_fLP = [i for i in AZ]


for i in range(1,n):
	#y[i]    := alpha * x[i]        + (1-alpha) * y[i-1]
	GX_fLP[i] = alpha * GX_fLP[i-1] + (1-alpha) * GX[i]
	GY_fLP[i] = alpha * GY_fLP[i-1] + (1-alpha) * GY[i]
	GZ_fLP[i] = alpha * GZ_fLP[i-1] + (1-alpha) * GZ[i]
	
	AX_fLP[i] = alpha * AX_fLP[i-1] + (1-alpha) * AX[i]
	AY_fLP[i] = alpha * AY_fLP[i-1] + (1-alpha) * AY[i]
	AZ_fLP[i] = alpha * AZ_fLP[i-1] + (1-alpha) * AZ[i]
	


# --------------------------------------
#    FILTERED (HIGH-PASS)
# --------------------------------------
alpha = 0.9
GX_fHP = [i for i in GX]
GY_fHP = [i for i in GY]
GZ_fHP = [i for i in GZ]

AX_fHP = [i for i in AX]
AY_fHP = [i for i in AY]
AZ_fHP = [i for i in AZ]

for i in range(1,n):
	#y[i]    := alpha * (y[i-1]      +  x[i] -  x[i-1])
	GX_fHP[i] = alpha * (GX_fHP[i-1] + GX[i] - GX[i-1])
	GY_fHP[i] = alpha * (GY_fHP[i-1] + GY[i] - GY[i-1])
	GZ_fHP[i] = alpha * (GZ_fHP[i-1] + GZ[i] - GZ[i-1])

	AX_fHP[i] = alpha * (AX_fHP[i-1] + AX[i] - AX[i-1])
	AY_fHP[i] = alpha * (AY_fHP[i-1] + AY[i] - AY[i-1])
	AZ_fHP[i] = alpha * (AZ_fHP[i-1] + AZ[i] - AZ[i-1])



# GYRO -----------------------------------------------------------------
plt.suptitle("Gyroscope measures")
plt.subplot(3,3,1)
plt.title("GX_raw")
plt.plot(time_ms, GX, "g" ,label="GX")
bottom, top = plt.ylim() 

plt.subplot(3,3,4)
plt.title("GY_raw")
plt.plot(time_ms, GY, "r" ,label="GY")
#plt.ylim((bottom, top))

plt.subplot(3,3,7)
plt.title("GZ_raw")
plt.plot(time_ms, GZ, "b" ,label="GZ")
#plt.ylim((bottom, top))

# LOW-PASS --------------------------------
plt.subplot(3,3,2)
plt.title("GX_fLP")
plt.plot(time_ms, GX_fLP, "g" ,label="GX_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,3,5)
plt.title("GY_fLP")
plt.plot(time_ms, GY_fLP, "r" ,label="GY_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,3,8)
plt.title("GZ_fLP")
plt.plot(time_ms, GZ_fLP, "b" ,label="GZ_fLP")
#plt.ylim((bottom, top))

# HIGH-PASS --------------------------------
plt.subplot(3,3,3)
plt.title("GX_fHP")
plt.plot(time_ms, GX_fHP, "g" ,label="GX_fHP")
#plt.ylim((bottom, top))

plt.subplot(3,3,6)
plt.title("GY_fHP")
plt.plot(time_ms, GY_fHP, "r" ,label="GY_fHP")
#plt.ylim((bottom, top))

plt.subplot(3,3,9)
plt.title("GZ_fHP")
plt.plot(time_ms, GZ_fHP, "b" ,label="GZ_fHP")
#plt.ylim((bottom, top))

plt.show()


# ACCEL -----------------------------------------------------------------
plt.suptitle("Accelerometer measures")
plt.subplot(3,3,1)
plt.title("AX_raw")
plt.plot(time_ms, AX, "g" ,label="AX")
bottom, top = plt.ylim() 

plt.subplot(3,3,4)
plt.title("AY_raw")
plt.plot(time_ms, AY, "r" ,label="AY")
#plt.ylim((bottom, top))

plt.subplot(3,3,7)
plt.title("AZ_raw")
plt.plot(time_ms, AZ, "b" ,label="AZ")

# LOW-PASS --------------------------------
plt.subplot(3,3,2)
plt.title("AX_fLP")
plt.plot(time_ms, AX_fLP, "g" ,label="AX_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,3,5)
plt.title("AY_fLP")
plt.plot(time_ms, AY_fLP, "r" ,label="AY_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,3,8)
plt.title("AZ_fLP")
plt.plot(time_ms, AZ_fLP, "b" ,label="AZ_fLP")

# HIGH-PASS --------------------------------
plt.subplot(3,3,3)
plt.title("AX_fHP")
plt.plot(time_ms, AX_fHP, "g" ,label="AX_fHP")
#plt.ylim((bottom, top))

plt.subplot(3,3,6)
plt.title("AY_fHP")
plt.plot(time_ms, AY_fHP, "r" ,label="AY_fHP")
#plt.ylim((bottom, top))

plt.subplot(3,3,9)
plt.title("AZ_fHP")
plt.plot(time_ms, AZ_fHP, "b" ,label="AZ_fHP")
#plt.ylim((bottom, top))

plt.show()


# GRAF ZA SEMINARSKO ZIROSKOP --------------------------------
plt.cla()
plt.clf()
plt.suptitle("Vrednosti ziroskopa v mirovanju in vpliv nizko-prepustnega filtra", fontsize=30 )
plt.subplot(3,2,1)
plt.title("GX nefiltrirane vrednosti")
plt.plot(time_ms[1:], GX[1:], "g" ,label="GX")

plt.subplot(3,2,3)
plt.title("GY nefiltrirane vrednosti")
plt.plot(time_ms[1:], GY[1:], "r" ,label="GY")
#plt.ylim((bottom, top))

plt.subplot(3,2,5)
plt.title("GZ nefiltrirane vrednosti")
plt.plot(time_ms[1:], GZ[1:], "b" ,label="GZ")
#plt.ylim((bottom, top))

# LOW-PASS --------------------------------
plt.subplot(3,2,2)
plt.title("GX filtrirane vrednosti")
plt.plot(time_ms[1:], GX_fLP[1:], "g" ,label="GX_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,2,4)
plt.title("GY filtrirane vrednosti")
plt.plot(time_ms[1:], GY_fLP[1:], "r" ,label="GY_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,2,6)
plt.title("GZ filtrirane vrednosti")
plt.plot(time_ms[1:], GZ_fLP[1:], "b" ,label="GZ_fLP")
#plt.ylim((bottom, top))

plt.show()


# GRAF ZA SEMINARSKO POSPESKOMETER --------------------------------
plt.cla()
plt.clf()
plt.suptitle("Vrednosti pospeskometra v mirovanju in vpliv visoko-prepustnega filtra", fontsize=30)
plt.subplot(3,2,1)
plt.title("AX nefiltrirane vrednosti")
plt.plot(time_ms[1:], AX[1:], "g" ,label="GX")

plt.subplot(3,2,3)
plt.title("AY nefiltrirane vrednosti")
plt.plot(time_ms[1:], AY[1:], "r" ,label="GY")
#plt.ylim((bottom, top))

plt.subplot(3,2,5)
plt.title("AZ nefiltrirane vrednosti")
plt.plot(time_ms[1:], AZ[1:], "b" ,label="GZ")
#plt.ylim((bottom, top))

# LOW-PASS --------------------------------
plt.subplot(3,2,2)
plt.title("AX filtrirane vrednosti")
plt.plot(time_ms[1:], AX_fHP[1:], "g" ,label="GX_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,2,4)
plt.title("AY filtrirane vrednosti")
plt.plot(time_ms[1:], AY_fHP[1:], "r" ,label="GY_fLP")
#plt.ylim((bottom, top))

plt.subplot(3,2,6)
plt.title("AZ filtrirane vrednosti")
plt.plot(time_ms[1:], AZ_fHP[1:], "b" ,label="GZ_fLP")
#plt.ylim((bottom, top))

plt.show()
