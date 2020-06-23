# BSO_Seminar
3D mouse

**Main files:**
- mouseRemote.py
- esp8266/mouse.c

**Tips:**
- Gyro should not move when restarting the device, so Bias is calculated correctly.
- Gyro Bias doesn't calculate correctly when changing gyro range
    `cycleGyroRange() --> calculateBias()`
