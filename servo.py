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
        wiringpi.pwmWrite(self.PWM_pin, 0)





    # This function increments the servo's position once every <delay_period_ms>
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


    def cycleServo(self, queue, logger):
        
        while True:
            
            if queue.empty():

                sleep(0.3)

	    else:

                msg = queue.get()
                if msg == "GETPELLET":

                    logger.debug("Lowering hopper arm")
                    # Lower hopper arm
                    self.setAngle(10, 173)
                    logger.debug("Raising hopper arm")
                    # Raise hopper arm
                    self.setAngle(10, 90)
                    logger.debug("Killing PWM signal")
                    self.stopServo()
            
                elif msg == "TERM":

		    print("SERVO: TERM RECEIVED")
                    logger.info("TERM signal received. Terminating process")
                    logger.debug("Lowering hopper arm")
                    self.setAngle(10, 173)
                    logger.debug("Killing PWM signal")
                    self.stopServo()
		    return 0
