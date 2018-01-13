import servo
import camera 
import RFID
import time 
from time import sleep 



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
    def insertSessionEntry(self, start_time, end_time, number_of_pellets_displayed):


        #TODO: Is there a better way to create + format strings?
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
		subsession_counter = 0

		while True:

                        # If RFID proximity pin returns high, then RFID tag is still present. Continue session. Else, stop session.
			if self.RFID_reader.readProximityState()

                            # Raise pellet arm
			    self.servo.setAngle(10, 90)

                            #TODO: <video_output_path> should not be constructed by startSession(). This path should be supplied by <AnimalProfile.profile>.
			    video_output_path = profile.session_history_directory +"/Videos/" + str(profile.ID) + "_session#_"  + str(profile.session_count) + "." + str(while_counter) + ".avi"

                            # Begin recording video
			    self.camera.captureVideo(video_output_path, 200)

                            # Lower pellet arm
			    self.servo.setAngle(10, 173)
			    subsession_counter += 1
                    
                            # Sleep to allow the PWM signal caused by servo.setAngle() to turn off.
                            # For some reason the RFID proximity pin signal will be interrupted if the servo's
                            # PWM signal is on. If we don't sleep here, the "if self.RFID_reader.readProximityState()"
                            # line may return a false negative. 
                            sleep(1)

                        # Session has completed
			else:
                	    session_end_time = time.time()	
			    break

                # Log session info 
		profile.insertSessionEntry(session_start_time, session_end_time, subsession_counter)	








# Servo config
servo_PWM_BCM_pin_number = 18

# Camera config
fourcc = "*MJPG"
camera_index = 0
camera_fps = 20.0
camera_res = (640,480)

# RFID config
serial_inerface_path = "/dev/ttyUSB0"
baudrate = 9600
RFID_proximity_BCM_pin_number = 23

# AnimalSession config
session_save_path = "./AnimalSessions/"






def main():
    
	# Test animal profiles.
	profile0 = AnimalProfile("0782B18622", "Jim Kirk", 0, 0, session_save_path)
	profile1 = AnimalProfile("0782B182D6", "Yuri Gagarin", 0, 0, session_save_path)
	profile2 = AnimalProfile("0782B17DE9", "Elon Musk", 0, 0, session_save_path)
	profile3 = AnimalProfile("0782B18A1E", "Buzz Aldrin", 0, 0, session_save_path)
	profile4 = AnimalProfile("5643564457", "Captain Picard", 0, 0, session_save_path)
	profile_list = [profile0, profile1, profile2, profile3, profile4]

        
        # Initializing servo, camera and RFID reader and session controller.
	servo_1 = servo.Servo(servo_PWM_BCM_pin_number)
	camera_1 = camera.Camera(fourcc, camera_index, camera_fps, camera_res)
	RFID_1 = RFID_Reader(serial_interface_path, baudrate, RFID_proximity_BCM_pin_number) 
	session_controller = SessionController(profile_list, serial, servo_1, camera_1, RFID_1)



        # Main loop until I implement a GUI or something 
	while True:
		RFID_code = session_controller.RFID_reader.listenForRFID()
		profile = session_controller.searchForProfile(RFID_code)
		session_controller.startSession(profile)
		


if __name__ == "__main__":
    main()

