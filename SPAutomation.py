import numpy as np
import cv2
import serial
import time
from time import sleep
import Servo_Control
import GPIO_Control



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
servo_PWM_pin = 18
servo_increment_delay_ms = 10
Servo_Control.initServo(servo_PWM_pin)
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
            session_history_directory: A file path to the directory containing all session_histories 
            session_count: An integer representing number of sessions animal has participated in. 
    """

    # Initializes instance variables for a particular AnimalProfile
    def __init__(self, ID, name, training_stage, session_count, session_history_directory):
        
        self.ID = ID
        self.name = name
        self.training_stage = training_stage 
	self.session_count = session_count
        self.session_history_directory = session_history_directory


    def insertSessionEntry(self, start_time, end_time, number_of_pellets_displayed):

	session_path = self.session_history_directory + str(self.ID) + "_session_history.txt"
	video_recording_path = self.session_history_directory + str(self.ID) + "_session" + str(self.session_count)
	csv_entry = start_time + "," + end_time + "," + str(number_of_pellets_displayed) + "," + video_recording_path + "\n"

	with open(session_path, "a") as session_history:
		session_history.write(csv_entry)
		self.session_count += 1


class SessionController(object):
	"""
		A  controller for all sessions that occur within the system. A "session" is defined as everything that happens when an animal
		is in proximity to the RFID reader. A session is started when an animal comes into proximity of the RFID reader and is
		ended when the animal leaves proximity of the RFID reader. A SessionController has the following properties:
	
		Attributes:
			profile_list: A list containing all animal profiles.
	"""

	# Initializes instance variables for the SessionController.
	def __init__(self, profile_list):
		self.profile_list = profile_list
		print "SessionController initialized"

	def listenForRFID(self):

		RFID_code = ""
		print "Waiting for RF tag..."

		while True:
		
			data = serial.read()

			# RFID end character detected. Session will be started.
			if data == '\r':
				RFID_code = RFID_code[2:len(RFID_code) - 1]
				tag_detected_message = "RF tag detected: " + RFID_code
				print(tag_detected_message)
				self.startSession(RFID_code)
				RFID_code = ""
				print("Flushing serial buffer...")
				serial.reset_input_buffer()
				sleep(1)
				print("Serial buffer flush completed")
				print("Ready for next session")
				print("Waiting for RF tag...")
			# RFID end character not detected. Continue listening.
			else:
				RFID_code = RFID_code + data

	def startSession(self, ID):
		
		session_start_time = time.time()	

		# Get profile of animal who started session
		session_profile = " "
		for profile in self.profile_list:
			if profile.ID == ID:
				session_profile = profile
				print("\n-------------------------------------")
				start_session_message = "Starting session for: " + profile.name
				print(start_session_message)
				break
			elif profile == self.profile_list[len(self.profile_list) - 1]:
				print("\n-------------------------------------")
				print("Id not recognized. Aborting session")
				print("-------------------------------------")
				return 


		
		session_end_time = time.time()
		end_session_message = profile.name + "'s session has completed"
		print(end_session_message)
		print("-------------------------------------")

def main():
    
	# Testing AnimalProfile functions
	session_save_path = "./"
	profile0 = AnimalProfile("0782B18622", "Jim Kirk", 0, 0, session_save_path)
	profile1 = AnimalProfile("0782B182D6", "Yuri Gagarin", 0, 0, session_save_path)
	profile2 = AnimalProfile("0782B17DE9", "Elon Musk", 0, 0, session_save_path)
	profile3 = AnimalProfile("0782B18A1E", "Buzz Aldrin", 0, 0, session_save_path)
	profile4 = AnimalProfile("5643564457", "Captain Picard", 0, 0, session_save_path)
	profile_list = [profile0, profile1, profile2, profile3, profile4]
	session_controller = SessionController(profile_list)
	session_controller.listenForRFID()

		

if __name__ == "__main__":
    main()

