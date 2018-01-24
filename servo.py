import wiringpi 
from time import sleep



class Servo(object):
    
    def __init__(self,PWM_BCM_pin):
            
        self.PWM_pin = PWM_BCM_pin
        self.initial_position = 173
        self.current_position = 173
        
        wiringpi.wiringPiSetupGpio()
        wiringpi.pinMode(PWM_BCM_pin, wiringpi.GPIO.PWM_OUTPUT)
        wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
        wiringpi.pwmSetClock(192)
        wiringpi.pwmSetRange(2000)

        wiringpi.pwmWrite(PWM_BCM_pin, self.initial_position)
        sleep(1)






    # This function increments the servo's position once ever <delay_period_ms>
    # until it reaches <target_position>.
    def setAngle (self, delay_period_ms, target_position):
	
	number_of_pulses = abs(target_position - self.current_position)


	if self.current_position < target_position:
	    for x in range (number_of_pulses):
		wiringpi.pwmWrite(self.PWM_pin, self.current_position)
		self.current_position += 1
		sleep(float(delay_period_ms)/1000.0)
	elif self.current_position > target_position:

	    for x in range (number_of_pulses):
		wiringpi.pwmWrite(self.PWM_pin, self.current_position)
		self.current_position -= 1
		sleep(float(delay_period_ms)/1000.0)


    def stopServo(self):
        wiringpi.pwmWrite(self.PWM_pin, 0)


    def cycleServo(self, sleep_duration, queue):
        
        while True:

            if queue.empty():
                self.setAngle(10, 173)
                self.setAngle(10, 90)
                self.stopServo()
                sleep(sleep_duration)
            else:
                signal = queue.get()
                print(signal)
                return 

