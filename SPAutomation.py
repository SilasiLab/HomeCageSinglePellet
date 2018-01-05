import numpy as np
import cv2
import serial
import wiringpi
from time import sleep



# Camera control setup
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

# RFID control setup
print ("Opening serial connection to /dev/ttyUSB0...")
serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)
print ("Serial connection established...")

# Servo control setup
GPIO_pin = 18
delay_period = 0.01
initial_position = 167
current_position = 0
wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(GPIO_pin, wiringpi.GPIO.PWM_OUTPUT)
wiringpi.pwmSetMode(wiringpi.GPIO.PWM_MODE_MS)
wiringpi.pwmSetClock(192)
wiringpi.pwmSetRange(2000)

# Initialise servo position
def initPosition(initial_position):
	
	global current_position
	wiringpi.pwmWrite(GPIO_pin, initial_position)
	current_position = initial_position
	sleep(2)

# Set servo position (Do not set value outside 50-167 or servo will try to turn too far and break something)
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



# Main loop
code = ' '
print "Initialising servo..."
initPosition(167)
print ("Waiting for RF tag...")
while True:
	data = serial.read()

	if data == '\r':
		#Tag has been detected
		output = "RF tag detected: " + code 
		print(output)
		code = ""


		#Send signal to raise pellet arm
		setAngle(75)
		
		# Capture video
		print("Capturing video")
		for x in range(0,200):
			ret, frame = cap.read()
			out.write(frame)
			cv2.imshow('frame',frame)
		print ("Video saved to ./output.avi")

		# Return pellet arm to rest position
		setAngle(167)

		# Cycle Complete
		print("Ready for next cycle")
		print("Waiting for RF tag...")
		serial.reset_input_buffer()
		sleep(2)
	else:
		code = code + data




cap.release()
out.release()
cv2.destroyAllWindows()
