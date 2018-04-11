import wiringpi
from time import sleep
import multiprocessing

class StepperController(object):

	# Each inner list contains the output values for the 4 signal
	# pins of a stepper for taking 1 halfstep.
	halfstep_forward = [
			[1,0,0,0],
			[1,1,0,0],
			[0,1,0,0],
			[0,1,1,0],
			[0,0,1,0],
			[0,0,1,1],
			[0,0,0,1],
			[1,0,0,1]
						]

	halfstep_backward = [
			[1,0,0,1],
			[0,0,0,1],
			[0,0,1,1],
			[0,0,1,0],
			[0,1,1,0],
			[0,1,0,0],
			[1,1,0,0],
			[1,0,0,0]
						]



	# Stepper initialization consists of setting the stepper's signal <control_pins> to output mode
	# and placing <control_pins> into a list. The stepper's <current_position> and <target_position>
	# are also both set to 0. This means that when a stepper is initialized, it's current position in real
	# space will be considered the origin.

	def __init__(self, control_pins, steps_mm_ratio):

		wiringpi.wiringPiSetupGpio()
		self.queue = multiprocessing.Queue()

		for pin in control_pins:
			wiringpi.pinMode(pin, wiringpi.GPIO.OUTPUT)
			wiringpi.digitalWrite(pin,0)

		self.steps_mm_ratio = steps_mm_ratio
		self.stepper_pulse_pins = control_pins
		self.stepper_distance_to_origin = 0
		self.stepper_target_distance_to_origin = 0



	# This function rotates the stepper <forward> for <steps>.
	# The stepper's signal pins will be turned off when the movement
	# is complete. This function also polls the StepperController's queue
	# for interrupt messages. If it receives one, it immediately turns
	# off the control pins and returns the number of steps already taken.
	def moveStepper(self, forward, steps):

		if forward:
			pulses = self.halfstep_forward
		elif not forward:
			pulses = self.halfstep_backward

		steps_taken = 0

		for i in range(steps):
			for halfstep in range(8):
				for pin in range(4):
					wiringpi.digitalWrite(self.stepper_pulse_pins[pin], pulses[halfstep][pin])
				sleep(0.0007)
			steps_taken += 1

			# Poll queue after every 8 halfsteps for interrupt msg.
			if not self.queue.empty():
				msg = self.queue.get()
				if msg == "INTM":
					for pin in self.stepper_pulse_pins:
						wiringpi.digitalWrite(pin,0)
					return steps_taken

		for pin in self.stepper_pulse_pins:
			wiringpi.digitalWrite(pin,0)

		return 0

	# This function calculates the number of steps required to move
	# a stepper motor from it's current position to it's target position.
	def calcPosUpdtDist(self):

		dist = self.stepper_target_distance_to_origin - self.stepper_distance_to_origin
		return dist

	# This function moves a particular <stepper> to a <target> position.
	# It does this by calculating the distance from <current_position>
	# to <target_position> to determine the number and direction of steps
	# required to bridge that distance. It then feeds that information to moveStepper().
	def updateStepperPos(self, target):

		self.stepper_target_distance_to_origin = target
		travel_distance = self.calcPosUpdtDist()

		if travel_distance >= 0:
			steps_taken = self.moveStepper(True, travel_distance)
			self.stepper_distance_to_origin += steps_taken
		else:
			steps_taken = self.moveStepper(False, travel_distance *-1)
			self.stepper_distance_to_origin -= steps_taken


	# This function is used as an entry point when starting
	# the stepper_controller as a daemon. The daemon will wait in the background
	# and poll it's <queue> for commands related to controlling the stepper motors.

	# Note:
	# 	The stepper_controller should be run as a daemon when being used as part of
	# 	a concurrent application. The reason for this is that stepper motor movement
	# 	is controlled by thousands of precisely timed pulses to the motor's control pins.
	# 	This means whatever process calls move_stepper() will be tied up generating
	# 	pulses for the stepper control pins for the duration of the movement.

	def initDaemon(self):

		while True:

			if self.queue.empty():
				sleep(0.2)

			else:

				msg = self.queue.get()

				# The "POS" message expects a number immediately after POS representing the
				# target distance (in mm) from the origin. E.G: POS3 would be 3mm from the origin.
				if msg[0:3] == "POS":
					target_s = len(msg)
					target = int(msg[3:target_s])
					target = target * self.steps_mm_ratio
					self.updateStepperPos(target)


				elif msg == "TERM":
					print("stepper_controller_daemon: TERM sig received")
					return 0
