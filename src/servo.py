import wiringpi
from time import sleep



class Servo(object):

    def __init__(self,PWM_BCM_pin):

        self.PWM_pin = PWM_BCM_pin
        self.initial_position = 157
        self.current_position = 157

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


    # Turns off PWM signal to servo.
    def stopServo(self):
        wiringpi.pwmWrite(self.PWM_pin, 0)


    # This function is currently being used as the entry point for the servo sub-process that is
    # forked from main. This is a bad design and a proper initDaemon() function should be
    # created as an entry point for a long-lived servo control process that polls a message queue
    # for instructions. 
    def cycleServo(self, queue):

		self.setAngle(5,75)
		self.stopServo()
		while True:

			if queue.empty():

				sleep(0.2)

			else:

				msg = queue.get()
				if msg == "GETPELLET":

					# Lower hopper arm
					self.setAngle(2, 157)
					# Raise hopper arm
					self.setAngle(5, 75)
					self.stopServo()

				elif msg == "TERM":
					self.setAngle(2, 127)
					self.stopServo()
					return 0
