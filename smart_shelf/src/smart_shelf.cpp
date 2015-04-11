/*
 * Author: Brendan Le Foll <brendan.le.foll@intel.com>
 * Copyright (c) 2015 Intel Corporation.
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files (the
 * "Software"), to deal in the Software without restriction, including
 * without limitation the rights to use, copy, modify, merge, publish,
 * distribute, sublicense, and/or sell copies of the Software, and to
 * permit persons to whom the Software is furnished to do so, subject to
 * the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
 * NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
 * LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
 * OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
 * WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */

#include "mraa.hpp"

#include <iostream>
#include <unistd.h>
#include <math.h>
#include <string.h>
#include <stdio.h>
#include <stdlib.h>

/*
 * Analog input example
 *
 * Demonstrate how to read an analog voltage value from an input pin using the
 * MRAA library, any sensor that outputs a variable voltage can be used with
 * this example code.
 * Suitable ones in the Grove Starter Kit are the Rotary Angle Sensor, Light
 * Sensor, Sound Sensor, Temperature Sensor.
 *
 * - analog in: analog sensor connected to pin A0 (Grove Base Shield Port A0)
 *
 * Additional linker flags: none
 */

const char WEIGHT_SWITCH 	= 'w';
const char QUAD_SWITCH		= 'q';
const char FORCE_SWITCH		= 'f';
const char RES_SWITCH		= 'r';
const char AIN_SWITCH		= 'a';
const char LED_SWITCH       = 'l';

float A_const[4] = {1.3785f,	1.3196f, 	1.7905f, 	1.4368f};
float B_const[4] = {-0.75f, 	-0.734f, 	-0.802f, 	-0.741f};
float r_const = 3.23;

// calculates the weight from the vector array
float calculate_weight(float force_values[]){
	return force_values[0] + force_values[1] + force_values[2] + force_values[3];
}

// calculates XY location. X = [0...1], Y = [0..1]
void calculate_XY(float * x, float * y, float force_values[]){
	float weight = calculate_weight(force_values);

	*x = (force_values[2] + force_values[3]) / weight;
	*y = (force_values[1] + force_values[2]) / weight;
}

// converts resistance into force values. R = kOhms. F = lbf
void calculate_forces(float* force_values, float res_values[]){
	for (int i = 0; i < 4; i++){
		*(force_values + i) = A_const[i] * pow(res_values[i], B_const[i]);
	}
}

// calculates the resistance from integer value
float calculate_res(int readerValueInt){
	return r_const * 1024.0f / (float)readerValueInt - r_const;
}

int main(int argc,  char* argv[])
{
	// check that we are running on Galileo or Edison
	mraa_platform_t platform = mraa_get_platform_type();
	if ((platform != MRAA_INTEL_GALILEO_GEN1) &&
			(platform != MRAA_INTEL_GALILEO_GEN2) &&
			(platform != MRAA_INTEL_EDISON_FAB_C)) {
		std::cerr << "Unsupported platform, exiting" << std::endl;
		return MRAA_ERROR_INVALID_PLATFORM;
	}

	// create an analog input object from MRAA using pin A0
	mraa::Aio* a0_pin = new mraa::Aio(0);
	if (a0_pin == NULL) {
		std::cerr << "Can't create mraa::Aio object for analog-in 0, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}	// create an analog input object from MRAA using pin A1
	mraa::Aio* a1_pin = new mraa::Aio(1);
	if (a1_pin == NULL) {
		std::cerr << "Can't create mraa::Aio object for analog-in 1, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}
	// create an analog input object from MRAA using pin A2
	mraa::Aio* a2_pin = new mraa::Aio(2);
	if (a2_pin == NULL) {
		std::cerr << "Can't create mraa::Aio object for analog-in 2, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}
	// create an analog input object from MRAA using pin A3
	mraa::Aio* a3_pin = new mraa::Aio(3);
	if (a3_pin == NULL) {
		std::cerr << "Can't create mraa::Aio object for analog-in 3, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}

	// create a gpio object from MRAA using pin 8
	mraa::Gpio* d_pin = new mraa::Gpio(8);
	if(d_pin == NULL) {
		std::cerr << "Can't create mraa::Gpio object, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}

	// set the pin as output
	if(d_pin->dir(mraa::DIR_OUT) != MRAA_SUCCESS) {
		std::cerr << "Can't set digital pin as output, exiting" << std::endl;
		return MRAA_ERROR_UNSPECIFIED;
	}

	// loop forever toggling the digital output every second
//	for(;;) {
//		d_pin->write(0);
//		sleep(1);
//		d_pin->write(1);
//		sleep(1);
//	}

	if(argc <= 1)
	{
		std::cerr << "Invalid parameters" << std::endl;
		return MRAA_ERROR_INVALID_PARAMETER;
	}

	if(argv[1][0] == WEIGHT_SWITCH)
	{
		float force_values[4];
		for(int i = 0; i < 4; i ++)
		{
			force_values[i] = atof(argv[2 + i]);
		}
		float weight = calculate_weight(force_values);
		//std::cout << "" << weight << std::endl;
		printf("%f\n", weight);
	}
	else if(argv[1][0] == QUAD_SWITCH)
	{
		float force_values[4];
		for(int i = 0; i < 4; i ++)
		{
			force_values[i] = atof(argv[2 + i]);
		}
		float x, y;
		calculate_XY(&x, &y, force_values);
		int q;
		if(x < 0.5 && y < 0.5)
		{
			q = 0;
		}
		else if(x < 0.5 && y >= 0.5)
		{
			q = 1;
		}
		else if(x >= 0.5 && y >= 0.5)
		{
			q = 2;
		}
		else if(x >= 0.5 && y < 0.5)
		{
			q = 3;
		}
		//TODO: change to quadrant below
		//e.g.
		printf("%d\n", q);
//		printf("%f %f\n", x, y);
	}
	else if(argv[1][0] == FORCE_SWITCH)
	{
		float res_values[4];
		for(int i = 0; i < 4; i ++)
		{
			res_values[i] = atof(argv[2 + i]);
		}
		float force_values[4];
		calculate_forces(force_values, res_values);
		printf("%f %f %f %f\n", force_values[0], force_values[1], force_values[2], force_values[3]);
	}
	else if(argv[1][0] == RES_SWITCH)
	{
		int atd_values[4];
		for(int i = 0; i < 4; i ++)
		{
			atd_values[i] = atoi(argv[2 + i]);
		}
		float res_values[4];
		for(int i = 0; i < 4; i ++)
		{
			float res = calculate_res(atd_values[i]);
			res_values[i] = res;
		}
		printf("%f %f %f %f\n", res_values[0], res_values[1], res_values[2], res_values[3]);
	}
	else if(argv[1][0] == AIN_SWITCH)
	{
		int atd_values[4];
		atd_values[0] = (int)a0_pin->read();
		atd_values[1] = (int)a1_pin->read();
		atd_values[2] = (int)a2_pin->read();
		atd_values[3] = (int)a3_pin->read();
		printf("%d %d %d %d\n", atd_values[0], atd_values[1], atd_values[2], atd_values[3]);
	}
	else if(argv[1][0] == LED_SWITCH)
	{
		int led_on = atoi(argv[2]);
		if(led_on)
		{
			d_pin->write(1);
		}
		else
		{
			d_pin->write(0);
		}
	}

	return MRAA_SUCCESS;
}
