import numpy as np
import cv2
import serial
import time
from time import sleep
import Servo_Control
import GPIO_Control



class RFIDReader(object):
	
	def __init__(self, serial_interface_path, baudrate, proximity_BCM_pin):

		print ("Opening serial connection to /dev/ttyUSB0...")
		self.RFID = serial.Serial(serial_interface_path, baudrate)
		self.proximity_pin = proximity_BCM_pin
		GPIO_Control.initGPIO()
		GPIO_Control.configureGPIOPin(proximity_BCM_pin, 1)
		print ("Serial connection established")


	def proximityIsHigh(self):
		return GPIO_Control.getPinState(self.proximity_pin)

class Camera(object):
	
	def __init__(self, fourcc, camera_index):
	
		print("Opening connection to camera...")
		self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
		self.camera = cv2.VideoCapture(0)
		print("Camera connection established")


	def captureVideo(self, output_filename, fps, res_tuple, number_of_frames):
	
		camera_output = cv2.VideoWriter(output_filename, self.fourcc, fps, res_tuple)

		for x in range(0, number_of_frames):
			ret, frame = self.camera.read()
			cv2.imshow("live_feed", frame)
			if cv2.waitKey(1) & 0xFF == ord('q'):
				break
			else:
				camera_output.write(frame)


#TODO: merge this class with Servo_Control.py
class Servo(object):
	
	def __init__(self, PWM_pin, position_increment_ms):
	
		self.PWM_pin = PWM_pin
		self. position_increment_ms = position_increment_ms
		Servo_Control.initServo(PWM_pin)

	def setAngle(self, angle):
		Servo_Control.setAngle(self.PWM_pin, self.position_increment_ms, angle)


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
	csv_entry = str(start_time) + "," + str(end_time) + "," + str(number_of_pellets_displayed) + "," + video_recording_path + "\n"

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
			serial_port: A serial_port object that has already been initialized to the desired serial interface.
			servo: An object that controls a servo.
			camera: An object that controls a camera.
			RFID_reader: An object that controls an RFID reader.
	"""

	# Initializes instance variables for the SessionController.
	def __init__(self, profile_list, serial_port, servo, camera, RFID_reader):

		self.profile_list = profile_list
		self.serial_port = serial_port
		self.servo = servo
		self.camera = camera
		self.RFID_reader = RFID_reader


	# This function listens to the SessionController's serial_port and appends 
	# each byte it receives to <RFID_code>. Once the "\r" terminating character 
	# is received, RFID_code is returned.
	def listenForRFID(self):

		RFID_code = ""
		print "Waiting for RF tag..."

		while True:
		
			data = self.RFID_reader.RFID.read()

			# RFID end character detected. Parse and return RFID.
			if data == '\r':
				RFID_code = RFID_code[2:len(RFID_code) - 1] #TODO: Parse RFID_code properly.
				tag_detected_message = "RF tag detected: " + RFID_code
				print(tag_detected_message)
				print("Flushing serial buffer...")
				self.RFID_reader.RFID.reset_input_buffer()
				sleep(1)
				print("Serial buffer flush completed")
				return RFID_code

			# RFID end character not detected. Continue listening.
			else:
				RFID_code = RFID_code + data

	# This function searches the SessionController's profile_list for a profile whose ID 
	# matches the supplied RFID. If a profile is found, it is returned. If no profile is found,
	# an error message is printed to stdout and -1 is returned.
	def searchForProfile(self, RFID):

		# Search profile_list for AnimalProfile whose ID matches RFID
		for profile in self.profile_list:
			if profile.ID == RFID:
				return profile
			elif profile == self.profile_list[len(self.profile_list) - 1]:
				print("\n-------------------------------------")
				print("Id not recognized. Aborting session.")
				print("-------------------------------------")
				return -1


	def startSession(self, profile):

		session_start_time = time.time()	
		while_counter = 0
		print(self.RFID_reader.proximityIsHigh())
		while self.RFID_reader.proximityIsHigh():
			self.servo.setAngle(90)
			video_output_path = profile.session_history_directory + str(profile.ID) + "_session" + str(profile.session_count) + ".avi"
			self.camera.captureVideo(video_output_path, 20.0, (640, 480), 200)
			self.servo.setAngle(173)
			while_counter += 1
		
		session_end_time = time.time()	
		profile.insertSessionEntry(session_start_time, session_end_time, while_counter)


def main():
    
	# Testing AnimalProfile functions
	session_save_path = "./"
	profile0 = AnimalProfile("0782B18622", "Jim Kirk", 0, 0, session_save_path)
	profile1 = AnimalProfile("0782B182D6", "Yuri Gagarin", 0, 0, session_save_path)
	profile2 = AnimalProfile("0782B17DE9", "Elon Musk", 0, 0, session_save_path)
	profile3 = AnimalProfile("0782B18A1E", "Buzz Aldrin", 0, 0, session_save_path)
	profile4 = AnimalProfile("5643564457", "Captain Picard", 0, 0, session_save_path)

	profile_list = [profile0, profile1, profile2, profile3, profile4]
	servo_1 = Servo(18, 10)
	camera_1 = Camera('*MJPG', 0)
	RFID_1 = RFIDReader("/dev/ttyUSB0", 9600, 23)
	session_controller = SessionController(profile_list, serial, servo_1, camera_1, RFID_1)

	RFID_code = session_controller.listenForRFID()
	profile = session_controller.searchForProfile(RFID_code)
	session_controller.startSession(profile)
		

if __name__ == "__main__":
    main()

