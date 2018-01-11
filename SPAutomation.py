import numpy as np
import cv2
import serial
import Servo_Control
import GPIO_Control
from time import sleep


# GPIO Initialization
print("Initializing GPIO pins...")
RFID_proximity_pin = 23
IR_breaker_pin = 24
GPIO_Control.initGPIO()
GPIO_Control.configureGPIOPin(RFID_proximity_pin, 0)
GPIO_Control.configureGPIOPin(IR_breaker_pin, 0)
print("GPIO pins initialized")

# Servo Initialization
print("Initializing servo...")
Servo_PWM_pin = 18
servo_increment_delay_ms = 10
Servo_Control.initServo(servo_PWM_pin, servo_increment_delay_ms)
print("Servo initialized")

# Camera Initialization
print("Opening connection to camera...")
fourcc = cv2.VideoWriter_fourcc(*'MJPG')
camera = cv2.VideoCapture(0)
camera_output = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))
print("Camera connection established")

# RFID Initialization
print ("Opening serial connection to /dev/ttyUSB0...")
serial = serial.Serial("/dev/ttyUSB0", baudrate=9600)
print ("Serial connection established")






class AnimalProfile(object):
    """
        A complete profile for a specific animal. Each profile has a unique 
        ID representing a particular animal. Each AnimalProfile has the following
        properties:


        Attributes:

            ID: The ID of the animal who owns the profile. 
            name: The name of the animal. 
            training_stage: An integer representing the current stage of training the animal is at. 
            session_history_path: A file path to the animal's session history. 
            session_count: An integer representing number of sessions animal has participated in. 
            profile_save_path: A file path to the profile save file.
    """


    # Initializes instance variables for a particular AnimalProfile
    def __init__(self, ID, name, training_stage, session_history_path, profile_save_path):
        
        self.ID = ID
        self.name = name
        self.training_stage = training_stage 
        self.session_history_path = session_history_path
        self.profile_save_path = profile_save_path


    def setTrainingStage(self, training_stage):
        
        self.training_stage = training_stage 


    def insertSessionEntry(self, start_time, end_time, number_of_pellets_displayed):

        session_entry = start_time + "," + end_time + "," + number_of_pellets_displayed

        with open(self.session_history_path, "a") as session_history:
            session_history.write(session_entry)



def main():
    
    session_path = ""

    test_profile = AnimalProfile(1337, "george", 0, session_path, "")
    test_profile.insertSessionEntry("today","later today","10")

if __name__ == "__main__":
    main()

code = ' '


print ("Waiting for RF tag...")
while True:
	data = serial.read()

	if data == '\r':
		#Tag has been detected
		output = "RF tag detected: " + code 
		print(output)
		code = ""


		#Send signal to raise pellet arm
		Servo_Control.setAngle(servo1_BCM_GPIO_pin, servo1_position_increment_delay_ms, 90)
		
		# Capture video
		print("Capturing video")
		for x in range(0,200):
			ret, frame = cap.read()
			cv2.imshow("live_feed", frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			out.write(frame)

		print ("Video saved to ./output.avi")

		# Return pellet arm to rest position
		Servo_Control.setAngle(servo1_BCM_GPIO_pin, servo1_position_increment_delay_ms, 173)

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
