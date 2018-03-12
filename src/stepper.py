import wiringpi
from time import sleep
import multiprocessing

class StepperController(object):

	# Each inner list contains the output values for the 4 signal
	# pins of a stepper for taking 1 step.
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
	# This is a list of lists. The outer list represents a particular stepper motor
	# and the inner list represents the control pins for that particular stepper motor.
	stepper_pulse_pins = []
	stepper_distances_to_origin = []
	stepper_target_distances_to_origin = []


	def __init__(self):

		wiringpi.wiringPiSetupGpio()
		self.queue = multiprocessing.Queue()

	# Stepper initialization consists of setting the stepper's signal <control_pins> to output mode
	# and placing <control_pins> into a list. The stepper's <current_position> and <target_position>
	# are also both set to 0. This means that when a stepper is initialized, it's current position in real
	# space will be considered the origin.
	def initStepper(self, control_pins):

		for pin in control_pins:
			wiringpi.pinMode(pin, wiringpi.GPIO.OUTPUT)
			wiringpi.digitalWrite(pin,0)

		self.stepper_pulse_pins.append(control_pins)
		self.stepper_distances_to_origin.append(0)
		self.stepper_target_distances_to_origin.append(0)


	# This function rotates <stepper> <forward> for <steps>.
	# The stepper's signal pins will be turned off when the movement
	# is complete.
	def moveStepper(self, stepper, forward, steps):

		if forward:
			pulses = self.halfstep_forward
		elif not forward:
			pulses = self.halfstep_backward

		for i in range(steps):
			for halfstep in range(8):
				for pin in range(4):
					wiringpi.digitalWrite(self.stepper_pulse_pins[stepper][pin], pulses[halfstep][pin])
				sleep(0.001)

		for pin in self.stepper_pulse_pins[stepper]:
			wiringpi.digitalWrite(pin,0)

		return 0

	# This function calculates the number of steps required to move
	# a stepper motor from it's current position to it's target position.
	def calcPosUpdtDist(self, stepper):

		dist = self.stepper_target_distances_to_origin[stepper] - self.stepper_distances_to_origin[stepper]
		return dist

	# This function moves a particular <stepper> to a <target> position.
	# It does this by calculating the distance from <current_position>
	# to <target_position> to determine the number and direction of steps
	# required to bridge that distance. It then feeds that information to moveStepper().
	def updateStepperPos(self, stepper, target):

		self.stepper_target_distances_to_origin[stepper] = target
		travel_distance = self.calcPosUpdtDist(stepper)

		if travel_distance >= 0:
			self.moveStepper(stepper, True, travel_distance)
		else:
			self.moveStepper(stepper, False, travel_distance *-1)

		self.stepper_distances_to_origin[stepper] = target

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

				# TODO: Temp random y-distance changing for testing xy-bed. Remove after testing.
				# Note: Make sure you change the updateStepperPos() parameters below back to real values
				# after removing <random_y_dist>
				random_y_dist = random.randint(0,4000)

				if msg == "0POS1":
					print("Updating pellet presentation y-distance to position 1")
					self.updateStepperPos(0, random_y_dist)

				elif msg == "0POS2":
					print("Updating pellet presentation y-distance to position 2")
					self.updateStepperPos(0, random_y_dist)

				elif msg == "0POS3":
					print("Updating pellet presentation y-distance to position 3")
					self.updateStepperPos(0, random_y_dist)

				elif msg == "0POS4":
					print("Updating pellet presentation y-distance to position 4")
					self.updateStepperPos(0, random_y_dist)

				elif msg == "1LEFT":
					self.updateStepperPos(1, 1000)

				elif msg == "1RIGHT":
					self.updateStepperPos(1, 2000)

				elif msg == "TERM":

					print("stepper_controller_daemon: TERM sig received")
					return 0
