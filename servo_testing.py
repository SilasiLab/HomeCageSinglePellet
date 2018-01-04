import wiringpi 
from time import sleep

GPIO_pin = 18
delay_period = 0.01
initial_position = 167
current_position = 0

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(GPIO_pin, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)



def initPosition(initial_position):
	
	global current_position
	wiringpi.pwmWrite(GPIO_pin, initial_position)
	current_position = initial_position
	sleep(2)


def setAngle (target_position):
	
	global current_position
	number_of_pulses = abs(target_position - current_position)

	if current_position < target_position:
			for x in range (number_of_pulses):
				wiringpi.pwmWrite(GPIO_pin, current_position)
				current_position += 1
				sleep(delay_period)
	elif current_position > target_position:
			for x in range (number_of_pulses):
				wiringpi.pwmWrite(GPIO_pin, current_position)
				current_position -= 1
				sleep(delay_period)


initPosition(initial_position)
setAngle(80)

