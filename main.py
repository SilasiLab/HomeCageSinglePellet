import servo
import camera 
import RFID
import IR 
import time 
from time import sleep 
import multiprocessing


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


    # This function takes all the information required for an animal's session log entry, and then formats it.
    # Once formatted, it writes the log entry to the animal's session_history log file. 
    def insertSessionEntry(self, start_time, end_time):


        #TODO: Is there a better way to create + format strings?
	session_path = self.session_history_directory + str(self.ID) + "_session_history.txt"
	video_recording_path = self.session_history_directory + str(self.ID) + "_session" + str(self.session_count)
	csv_entry = str(start_time) + "," + str(end_time) + "," + video_recording_path + "\n"

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
			elif profile == self.profile_list[len(self.profile_list) - 1]:
				return -1


        # This function starts an experiment session for the animal identified in the supplied <profile>. 
        # 
        # Note: (TODO) Since the "RFID-proximity-pin polling" and camera recording functions are on the same thread,
        # we currently have to interrupt the camera recording in order to poll the proximity pin to check if the
        # session should be terminated. Obviously, that sucks. The RFID proximity polling needs to be on it's own thread,
        # so that when it detects the RFID tag leaving, it can pass a message to the experiment session thread to interrupt it
        # and terminate the session. This function will need to be redesigned to facilitate this.
	def startSession(self, profile):


	    session_start_time = time.time()	
	    print("starting session")

            # If IR beam is broken, assume animal is present and begin session. 
	    if self.IR_beam_breaker.isBeamBroken() == 1:

                #TODO: <video_output_path> should not be constructed by startSession(). This path should be supplied by <AnimalProfile.profile>.
	        video_output_path = profile.session_history_directory +"/Videos/" + str(profile.ID) + "_session#_"  + str(profile.session_count) + ".avi"

                # Begin recording video
	       # self.camera.captureVideo(video_output_path, 200)
                jobs = []
                p = multiprocessing.Process(target=self.camera.captureVideo, args=(video_output_path,))
                jobs.append(p)
		print("starting process")
                p.start()
		sleep(60)










            if self.IR_beam_breaker.isBeamBroken() == 1:


                # Raise pellet arm
	        self.servo.setAngle(10, 90)


                # Lower pellet arm
	        self.servo.setAngle(10, 173)
                    
                # Sleep to allow the PWM signal caused by servo.setAngle() to turn off.
                # For some reason the RFID proximity pin signal will be interrupted if the servo's
                # PWM signal is on. If we don't sleep here, the "if self.RFID_reader.readProximityState()"
                # line may return a false negative. 
                sleep(1)

                session_end_time = time.time()	

                # Log session info 
	        profile.insertSessionEntry(session_start_time, session_end_time)	








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
# AnimalSession config
SESSION_SAVE_PATH = "./AnimalSessions/"




def main():
    
	# Test animal profiles.
	profile0 = AnimalProfile("0782B18622", "Jim Kirk", 0, 0, SESSION_SAVE_PATH)
	profile1 = AnimalProfile("0782B182D6", "Yuri Gagarin", 0, 0, SESSION_SAVE_PATH)
	profile2 = AnimalProfile("0782B17DE9", "Elon Musk", 0, 0, SESSION_SAVE_PATH)
	profile3 = AnimalProfile("0782B18A1E", "Buzz Aldrin", 0, 0, SESSION_SAVE_PATH)
	profile4 = AnimalProfile("5643564457", "Captain Picard", 0, 0, SESSION_SAVE_PATH)
	profile_list = [profile0, profile1, profile2, profile3, profile4]

        
        # Initializing servo, camera and RFID reader and session controller.
	servo_1 = servo.Servo(SERVO_PWM_BCM_PIN_NUMBER)
	camera_1 = camera.Camera(FOURCC, CAMERA_INDEX, CAMERA_FPS, CAMERA_RES)
	RFID_1 = RFID.RFID_Reader(SERIAL_INTERFACE_PATH, BAUDRATE, RFID_PROXIMITY_BCM_PIN_NUMBER) 
        IR_1 = IR.IRBeamBreaker(PHOTO_DIODE_BCM_PIN_NUMBER)
	session_controller = SessionController(profile_list, servo_1, camera_1, RFID_1, IR_1)



        # Main loop until I implement a GUI or something 
	while True:
		RFID_code = session_controller.RFID_reader.listenForRFID()
		print(RFID_code)
		profile = session_controller.searchForProfile(RFID_code)
		session_controller.startSession(profile)
		


if __name__ == "__main__":
    main()

