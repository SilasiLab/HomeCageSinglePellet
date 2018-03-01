import wiringpi
from time import sleep
import multiprocessing
		

class StepperController(object):

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
	stepper_x_distance_to_origin = 0
	stepper_y_distance_to_origin = 0
	
	def __init__(self):

		wiringpi.wiringPiSetupGpio()


	def init_stepper(self, control_pins):

		for pin in control_pins:
			wiringpi.pinMode(pin, wiringpi.GPIO.OUTPUT)
			wiringpi.digitalWrite(pin,0)
			
		self.stepper_pulse_pins.append(control_pins)
			

	# This function rotates <stepper> <forward> for <steps>.
	def move_stepper(self, stepper, forward, steps):

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
			
			
	# This function is used as an entry point when starting
	# the stepper_controller as a daemon. The daemon will wait in the background
	# and poll it's <queue> for commands related to controlling the stepper motors.
	
	# Note:
	# 	The stepper_controller should be run as a daemon when being used as part of 
	# 	a concurrent application. The reason for this is that stepper motor movement
	# 	is controlled by thousands of precisely timed pulses to the motor's control pins.
	# 	This means whatever process calls move_stepper() will be tied up generating
	# 	pulses for the stepper control pins for the duration of the movement. 
	
	def initDaemon(self, queue):
		
		while True:
			
			if queue.empty():
				sleep(0.2)
				
			else:
				
				msg = queue.get()
				jobs = []
				
				
				if msg == "0POS1":
					stepper_y_process = multiprocessing.Process(target=self.move_stepper, args=(0, True, 1000,))
					jobs.append(stepper_y_process)
					stepper_y_process.start()
					self.stepper_y_distance_to_origin += 1000
					
				elif msg == "0POS2":
					self.move_stepper(0, True, 2000)
					self.stepper_y_distance_to_origin += 2000
					
				elif msg == "0POS3":
					self.move_stepper(0, True, 3000)		
					self.stepper_y_distance_to_origin += 3000
					
				elif msg == "0POS4":
					self.move_stepper(0, True, 4000)
					self.stepper_y_distance_to_origin += 4000
					
				elif msg == "1LEFT":
					self.move_stepper(1, True, 1000)
					self.stepper_x_distance_to_origin += 1000
					
				elif msg == "1RIGHT":
					self.move_stepper(1, False, 1000) 
					self.stepper_x_distance_to_origin -= 1000
					
				elif msg == "TERM":
					
					# Return steppers to origin
					stepper_y_process = multiprocessing.Process(target=self.move_stepper, args=(0, False, self.stepper_y_distance_to_origin,))
					jobs.append(stepper_y_process)
					stepper_y_process.start()
					self.stepper_y_distance_to_origin = 0
					
					if self.stepper_x_distance_to_origin >= 0:
							self.move_stepper(1, False, self.stepper_x_distance_to_origin)
							self.stepper_x_distance_to_origin = 0
							
					elif self.stepper_x_distance_to_origin < 0:
							self.move_stepper(1, True, self.stepper_x_distance_to_origin * -1)
							self.stepper_x_distance_to_origin = 0
							
								
					print("stepper_controller_daemon: TERM sig received")
					return 0
		
