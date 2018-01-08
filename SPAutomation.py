import numpy as np
import cv2
import serial
import Servo_Control
import GPIO_Control
from time import sleep


servo1_BCM_GPIO_pin = 18
servo1_position_increment_delay_ms = 50


# Camera control setup
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

# RFID control setup
print ("Opening serial connection to /dev/ttyUSB0...")
serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)
print ("Serial connection established...")



# Main loop

code = ' '

print "Initialising servo..."
GPIO_Control.initGPIOPin(servo1_BCM_GPIO_pin, 0)
Servo_Control.initPWMPin(servo1_BCM_GPIO_pin)
Servo_Control.initServo(servo1_BCM_GPIO_pin)

print ("Waiting for RF tag...")
while True:
	data = serial.read()

	if data == '\r':
		#Tag has been detected
		output = "RF tag detected: " + code 
		print(output)
		code = ""


		#Send signal to raise pellet arm
		Servo_Control.setAngle(servo1_BCM_GPIO_pin, servo1_position_increment_delay_ms, 75)
		
		# Capture video
		print("Capturing video")
		for x in range(0,200):
			ret, frame = cap.read()
			out.write(frame)
			cv2.imshow('frame',frame)
		print ("Video saved to ./output.avi")

		# Return pellet arm to rest position
		Servo_Control.setAngle(servo1_BCM_GPIO_pin, servo1_position_increment_delay_ms, 167)

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
