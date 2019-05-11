#include <stdlib.h>
//#include "espressif/esp_common.h"
#include "esp/uart.h"
#include "FreeRTOS.h"
#include "task.h"
#include "esp8266.h"
#include "i2c/i2c.h"
//#include "bmp280/bmp280.h"

#define PCF_ADDRESS	0x38
#define MPU_ADDRESS	0x68
#define BUS_I2C		0
#define SCL 14
#define SDA 12
#define gpio_wemos_led	2

//					mask	returned value
#define button1		0x20	// 0b ??0? ????
#define button2		0x10	// 0b ???0 ????
#define button3		0x80	// 0b 0??? ????
#define button4		0x40	// 0b ?0?? ????
#define clr_btn		0xf0

#define led1		0xfe
#define led12		0xfc
#define led123		0xf8
#define led1234		0xf0

#define PWR_MGMT_1  		0x6B
#define PWR_MGMT_2  		0x6C
#define MPU9250_ACCEL_X		0x3b
#define MPU9250_GYRO_X 		0x43
#define MPU9250_GYRO_CONFIG 0x1B

bool mouseBTN1 = false;
bool mouseBTN2 = false;
bool mouseBTN3 = false;
bool mouseBTN4 = false;
float gx_d = 0;
float gy_d = 0;
int16_t gx_b = 0;
int16_t gy_b = 0;
float scroll_d = 0;

void write_byte(uint8_t address, uint8_t register_address, uint8_t data) {
	i2c_slave_write(BUS_I2C, address, &register_address, &data, 1);
}

uint8_t read_byte(uint8_t address, uint8_t register_address) {
	uint8_t data;
	i2c_slave_read(BUS_I2C, address, &register_address, &data, 1);
	return data;
}

uint8_t read_byte_pcf() {
	uint8_t data;
	i2c_slave_read(BUS_I2C, PCF_ADDRESS, NULL, &data, 1);
	return data;
}

void write_byte_pcf(uint8_t data) {
	i2c_slave_write(BUS_I2C, PCF_ADDRESS, NULL, &data, 1);
}

void MPU9250_start() {
	write_byte(MPU_ADDRESS, PWR_MGMT_1, 0x80);
	vTaskDelay(pdMS_TO_TICKS(100));
	write_byte(MPU_ADDRESS, PWR_MGMT_2, 0);
	vTaskDelay(pdMS_TO_TICKS(100));
	calculateBias();
}

void calculateBias() {
	uint8_t n = 10;
	gx_b = 0;
	gy_b = 0;
	for (uint8_t i; i < n; i++) {
		gx_b += (read_byte(MPU_ADDRESS, MPU9250_GYRO_X)<<8)|(read_byte(MPU_ADDRESS, MPU9250_GYRO_X+1));
		gy_b += (read_byte(MPU_ADDRESS, MPU9250_GYRO_X+2)<<8)|(read_byte(MPU_ADDRESS, MPU9250_GYRO_X+3));
		vTaskDelay(pdMS_TO_TICKS(10));
	}
	gx_b = gx_b /n;
	gy_b = gy_b /n;
}

float getGyroRange() {
	uint8_t data = read_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG);
	data = (data >> 3) & 0b11;
	
	switch(data) {
		case 0:
			return 131;
		case 1:
			return 65.5;
		case 2:
			return 32.8;
		case 3:
			return 16.4;
	}
}

void cycleGyroRange() {
	uint8_t data = read_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG);
	data = (data >> 3) & 0b11;
	data = (data + 1) %4;

	switch(data) {
		case 0:
			write_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG, 0b11100111);
			write_byte_pcf(led1);
			break;
		case 1:
			write_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG, 0b11101111);
			write_byte_pcf(led12);
			break;
		case 2:
			write_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG, 0b11110111);
			write_byte_pcf(led123);
			break;
		case 3:
			write_byte(MPU_ADDRESS, MPU9250_GYRO_CONFIG, 0b11111111);
			write_byte_pcf(led1234);
			break;
	}
	uint8_t pcf_byte = read_byte_pcf();
	while ((pcf_byte & button4) == 0) {
		pcf_byte = read_byte_pcf();
	}
}

void printStatus() {
	printf("__MOUSE_STATUS__\nBTN1: %d\nBTN2: %d\nBTN3: %d\nBTN4: %d\nGX: %f\nGY: %f\nscroll_d: %f\n__EOF__\n", mouseBTN1 , mouseBTN2, mouseBTN3, mouseBTN4, gx_d, gy_d, scroll_d);
}

void mouseTask(void *pvParameters) {
	uint8_t pcf_byte;
	int16_t gx;
	int16_t gy;
	MPU9250_start();

	while (true) {
		// read PCF Byte
		pcf_byte = read_byte_pcf();
		mouseBTN1 = ((pcf_byte & button1) == 0);
		mouseBTN2 = ((pcf_byte & button2) == 0);
		mouseBTN3 = ((pcf_byte & button3) == 0);
		mouseBTN4 = ((pcf_byte & button4) == 0);
		
		// Read Gyro
		gx = (read_byte(MPU_ADDRESS, MPU9250_GYRO_X)<<8)|(read_byte(MPU_ADDRESS, MPU9250_GYRO_X+1));
		gy = (read_byte(MPU_ADDRESS, MPU9250_GYRO_X+2)<<8)|(read_byte(MPU_ADDRESS, MPU9250_GYRO_X+3));
		gx = gx - gx_b;
		gy = gy - gy_b;
		
		gx_d = ((float) gx) / getGyroRange();
		gy_d = ((float) gy) / getGyroRange();
		scroll_d = 0;
		// Scrolling
		if (mouseBTN3) {
			scroll_d = gy_d;
			gx_d = 0;
			gy_d = 0;
		}
		// Change sensitivity
		if (mouseBTN4) {
			//cycleGyroRange();
		}

		printStatus();

		if (false) {
			printf("BIAS: %d - %d\n", gx_b, gy_b );
			printf(" RAW: %d - %d\n", gx, gy);
		}

		mouseBTN1 = false;
		mouseBTN2 = false;
		mouseBTN3 = false;
		mouseBTN4 = false;
		vTaskDelay(pdMS_TO_TICKS(100));
	}
}


void user_init(void)
{
    uart_set_baud(0, 115200);
    // I2C
    i2c_init(BUS_I2C, SCL, SDA, I2C_FREQ_100K);
    // fix i2c driver to work with MPU-9250
    gpio_enable(SCL, GPIO_OUTPUT);

	// turn off Wemos led
	gpio_enable(gpio_wemos_led, GPIO_OUTPUT);
	gpio_write(gpio_wemos_led, 1);
	
	write_byte_pcf(led1);

	xTaskCreate(mouseTask, "mouseTask", 250, NULL, 2, NULL);
	 
}
