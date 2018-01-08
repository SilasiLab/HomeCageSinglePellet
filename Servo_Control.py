import wiringpi 
from time import sleep

initial_position = 167
current_position = 167


# This function initializes the GPIO pin at <BCM_pin_number> to 
# PWM mode for servo control and sets initial servo position.
def initServo(BCM_pin_number):
	
    global current_position
    global initial_position 

    wiringpi.pinMode(BCM_pin_number, wiringpi.GPIO.PWM_OUTPUT)
    wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
    wiringpi.pwmSetClock(192)
    wiringpi.pwmSetRange(2000)

    wiringpi.pwmWrite(BCM_pin_number, initial_position)
    current_position = initial_position 
    sleep(1)


# This function slowly changes the angle of the servo controlled by the
# GPIO pin at <BCM_pin_number>.
#
# Note: This function increments the servo's position and then sleeps
# for <delay_period>. Decrease/Increase to speed/slow the servo's movement.
def setAngle (BCM_pin_number, delay_period_ms, target_position):
	
	global current_position
	number_of_pulses = abs(target_position - current_position)


	if current_position < target_position:
	    for x in range (number_of_pulses):
		wiringpi.pwmWrite(BCM_pin_number, current_position)
		current_position += 1
		sleep(float(delay_period_ms)/1000.0)
	elif current_position > target_position:

	    for x in range (number_of_pulses):
		wiringpi.pwmWrite(BCM_pin_number, current_position)
		current_position -= 1
		sleep(float(delay_period_ms)/1000.0)



