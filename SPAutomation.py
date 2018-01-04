import time
import numpy as np
import cv2
import serial
import RPi.GPIO as GPIO
from time import sleep



# Camera control setup
cap = cv2.VideoCapture(0)
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))


# RFID control setup
print ("Opening serial connection to /dev/ttyUSB0...")
serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)
print ("Serial connection established...")

def setangle(angle):
	duty = angle / 18 + 2
	GPIO.output(12,True)
	pwm.ChangeDutyCycle(duty)
	sleep(0.5)
	GPIO.output(12, False)
	pwm.ChangeDutyCycle(0)



# Main loop
code = ' '
print ("Waiting for RF tag...")
while True:
	data = serial.read()

	if data == '\r':
		#Tag has been detected
		output = "RF tag detected: " + code 
		print(output)

		#Send signal to raise pellet arm
		print("Initializing GPIO pins")
		GPIO.setmode(GPIO.BOARD)
		GPIO.setup(12,GPIO.OUT)
		pwm = GPIO.PWM(12,50)
		pwm.start(0)
		print("GPIO pins initialized")
		print("Raising pellet arm")
		setangle(0)
		print("Pellet arm raised")
		
		# Capture video
		print("Capturing video")
		for x in range(0,200):
			ret, frame = cap.read()
			out.write(frame)
			cv2.imshow('frame',frame)
		print ("Video saved to ./output.avi")

		# Return pellet arm to rest position
		print("Lowering pellet arm")
		setangle(100)
		print("Cutting power to servo")		
		pwm.stop()
		GPIO.cleanup()
		code = ' '
		print("Ready for next cycle")
		print("Waiting for RF tag...")
	else:
		code = code + data




cap.release()
out.release()
cv2.destroyAllWindows()
