import servo
import camera 
import RFID
import IR 
import time 
from time import sleep 
import multiprocessing
from terminaltables import AsciiTable

class AnimalProfile(object):
   """ 
        A complete profile for a specific animal. Each profile has a unique 
        ID representing a particular animal. Each AnimalProfile has the following
        properties:

        Attributes:
            ID: The ID of the animal who owns the profile. 
            name: The name of the animal. 
            training_stage: An integer representing the current stage of training the animal is at. 
            session_count: An integer representing the numbers of sessions the animal has participated in.
            session_history_directory: A file path pointing to where the profile's session_history file will be saved. 
            video_save_directory: A file path point to where video for the profile will be saved. 
    """

    # Initializes instance variables for a particular AnimalProfile
    def __init__(self, ID, name, training_stage, session_count, session_history_directory, video_save_directory):
        
        self.ID = ID
        self.name = name
        self.training_stage = training_stage  
	self.session_count = session_count
        self.session_history_directory = session_history_directory
        self.video_save_directory = video_save_directory 


    # This function takes all the information required for an animal's session log entry, and then formats it.
    # Once formatted, it writes the log entry to the animal's session_history log file. 
    def insertSessionEntry(self, start_time, end_time, num_pellets_presented):


        #TODO: Is there a better way to create + format strings?
	session_path = self.session_history_directory + str(self.ID) + "_session_history.txt"
	csv_entry = str(start_time) + "," + str(end_time) + "," + str(num_pellets_presented) + "," + self.video_save_directory + "\n"

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
			servo: An object that controls a servo.
			camera: An object that controls a camera.
			RFID_reader: An object that controls an RFID reader.
                        IR_beam_breaker: An object that controls an IR beam breaker.
	"""

	# Initializes instance variables for the SessionController.
	def __init__(self, profile_list, servo, camera, RFID_reader, IR_beam_breaker):

		self.profile_list = profile_list 
		self.servo = servo
		self.camera = camera
		self.RFID_reader = RFID_reader
                self.IR_beam_breaker = IR_beam_breaker



		

	# This function searches the SessionController's profile_list for a profile whose ID 
	# matches the supplied RFID. If a profile is found, it is returned. If no profile is found,
	# -1 is returned.
	def searchForProfile(self, RFID):

		# Search profile_list for AnimalProfile whose ID matches RFID
		for profile in self.profile_list:

		    if profile.ID == RFID:
                        return profile
                
                return -1


        # This function starts an experiment session for the animal identified in the supplied <profile>.
        # A session consists of a video recording spanning the duration of the session, repeated food pellet
        # presentatation every 10s, and various data logging for that session.
        # A session is terminated when the IR beam is no longer broken.
	def startSession(self, profile):


	    session_start_time = time.time()	
	    video_output_path = profile.video_save_directory + str(profile.ID) + "_session#_"  + str(profile.session_count) + ".avi"

            # Fork process and begin recording video in the new process. 
            jobs = []
            p = multiprocessing.Process(target=self.camera.captureVideo, args=(video_output_path,))
            jobs.append(p)
            p.start()
            
            num_pellets_presented = 0
            # While beam is broken, continue presenting pellets every 10s.
            while !self.IR_beam_breaker.getBeamState():

                # Lower pellet arm
	        self.servo.setAngle(10, 173)
                # Raise pellet arm
	        self.servo.setAngle(10, 90)
                # Shut off servo
                self.servo.stopServo()

                num_pellets_presented += 1
                sleep(10)


            
            p.terminate()
            session_end_time = time.time()	
            # Log session info 
	    profile.insertSessionEntry(session_start_time, session_end_time, num_pellets_presented)	








# Servo config
SERVO_PWM_BCM_PIN_NUMBER = 18
# Camera config
FOURCC = "*MJPG"
CAMERA_INDEX = 0
CAMERA_FPS = 20.0
CAMERA_RES = (640,480)
# RFID config
SERIAL_INTERFACE_PATH = "/dev/ttyUSB0"
BAUDRATE = 9600
RFID_PROXIMITY_BCM_PIN_NUMBER = 23
# IR breaker config
PHOTO_DIODE_BCM_PIN_NUMBER = 24
# AnimalProfile config
SESSION_SAVE_PATH = "./AnimalSessions/"
VIDEO_SAVE_PATH = "./AnimalSessions/Videos/"



def main():
   


        # Initializing animal profiles 
	profile0 = AnimalProfile("0782B18622", "Jim Kirk", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile1 = AnimalProfile("0782B182D6", "Yuri Gagarin", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile2 = AnimalProfile("0782B17DE9", "Elon Musk", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile3 = AnimalProfile("0782B18A1E", "Buzz Aldrin", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile4 = AnimalProfile("5643564457", "Captain Picard", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile_list = [profile0, profile1, profile2, profile3, profile4]

        # Initializing system components
	servo_1 = servo.Servo(SERVO_PWM_BCM_PIN_NUMBER)
	camera_1 = camera.Camera(FOURCC, CAMERA_INDEX, CAMERA_FPS, CAMERA_RES)
	RFID_1 = RFID.RFID_Reader(SERIAL_INTERFACE_PATH, BAUDRATE, RFID_PROXIMITY_BCM_PIN_NUMBER) 
        IR_1 = IR.IRBeamBreaker(PHOTO_DIODE_BCM_PIN_NUMBER)
	session_controller = SessionController(profile_list, servo_1, camera_1, RFID_1, IR_1)



	while True:

            # Block until an RFID tag is detected.
	    RFID_code = session_controller.RFID_reader.listenForRFID()

            # Attempt to find a profile matching the detected RFID.
	    profile = session_controller.searchForProfile(RFID_code)

            # If a profile with a matching RFID is found, begin a session for that profile.
            if profile != -1:
	        session_controller.startSession(profile)
		


if __name__ == "__main__":
    main()

