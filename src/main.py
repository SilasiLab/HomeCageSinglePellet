import servo
import camera
import RFID
import IR
import stepper
import objectDetector
import time
from time import sleep
import multiprocessing
import logging
import os



logging.basicConfig(filename="../logs/logfile.log", level=logging.DEBUG)
main_logger = logging.getLogger(__name__)


"""
This function generates a list of AnimalProfiles found inside <profile_save_directory>.
It then reads the save.txt file for each profile found, and uses the information
in that file to reconstruct the AnimalProfile object. It returns all the
reconstructed profiles as a list of AnimalProfiles.
Note: This function works by assuming the directory structure of each AnimalProfile
is consistent and the required save.txt files are present, i.e:

<profile_save_directory
   -
   - ProfileName
       -
       - Logs
       - Videos
       - save.txt
"""
def loadAnimalProfiles(profile_save_directory):

    # Get list of profile folders
	profile_names = os.listdir(profile_save_directory)
	profiles = []

	for profile in profile_names:

		# Build save file path
		load_file = profile_save_directory + profile + "/" + profile + "_save.txt"
		profile_state = []

		# Open the save file
		try:
			load = open(load_file, 'r')
		except IOError:
			print "Could not open AnimalProfile save file!"

		# Read all lines from save file and strip them
		with load:
			profile_state = load.readlines()
		profile_state = [x.strip() for x in profile_state]

		# Create AnimalProfile object using loaded data and put it in profile list
		ID = profile_state[0]
		name = profile_state[1]
		training_stage = profile_state[2]
		dominant_hand = profile_state[3]
		session_count = profile_state[4]
		animal_profile_directory = profile_state[5]
		temp = AnimalProfile(ID, name, training_stage, dominant_hand, session_count, animal_profile_directory, False)
		profiles.append(temp)


	return profiles




class AnimalProfile(object):
    """
        A profile containing all information related to a particular animal. When a new animal is added to the system,
        an AnimalProfile should be created for that animal. This profile will be used by the rest
        of the system for any operation pertaining to the animal (data logging, identification, etc). When the application closes,
        saveProfile() should be called on each profile in the system. A global loadProfiles() function is used to load/reconstruct
        each profile at load time. Each AnimalProfile has the following properties:

        Attributes:
            ID: A unique identification number for the animal. In our case this number will be the RFID of the RF tag implanted in the animal.
            name: The name of the animal
            training_stage: An integer representing which stage of training the animal is at.
            dominant_hand: String representing the dominant hand of the animal.
            session_count: The number of Sessions the animal has participated in. In our system, this is the number of times the animal has
                            entered the experiment tube.
            animal_profile_directory: A path to the root folder where AnimalProfile's are stored.
            video_save_directory: A path to where the videos for this animal are stored. This path will be inside [./<animal_profile_directory>/<animal_name>/]
            log_save_directory: A path to where the logs for this animal are stored. This pathh will be inside [./<animal_profile_directory/<animal_name/]
    """



	def __init__(self, ID, name, training_stage, dominant_hand, session_count, profile_save_directory, is_new):

		self.ID = str(ID)
		self.name = str(name)
		self.training_stage = int(training_stage)
		self.dominant_hand = str(dominant_hand)
		self.session_count = int(session_count)

        # Everything that's in this function and below this comment is Dependency Hell.
        # The save/load system is poorly designed and changing anything in the block below will
        # probably break it. Good luck.
		if is_new:
			self.animal_profile_directory = profile_save_directory + name + "/"
		else:
			self.animal_profile_directory = profile_save_directory

		self.video_save_directory = self.animal_profile_directory + "Videos/"
		self.log_save_directory = self.animal_profile_directory + "Logs/"

		if is_new:

			if not os.path.isdir(self.animal_profile_directory):
				os.makedirs(self.animal_profile_directory)

			if not os.path.isdir(self.video_save_directory):
				os.makedirs(self.video_save_directory)

			if not os.path.isdir(self.log_save_directory):
				os.makedirs(self.log_save_directory)


    # This function writes the state of the AnimalProfile object to the
    # AnimalProfile's save file.
	def saveProfile(self):

		save_file_path = self.animal_profile_directory + str(self.name) + "_save.txt"

		with open(save_file_path, 'w') as save:

			save.write(str(self.ID) + "\n")
			save.write(str(self.name) + "\n")
			save.write(str(self.training_stage) + "\n")
			save.write(str(self.dominant_hand) + "\n")
			save.write(str(self.session_count) + "\n")
			save.write(str(self.animal_profile_directory) + "\n")


	# This function takes all the information required for an animal's session log entry, and then formats it.
	# Once formatted, it appens the log entry to the animal's session_history.csv file.
	def insertSessionEntry(self, start_time, end_time, trial_count):

		#TODO: Is there a better way to create + format strings?
		session_history = self.log_save_directory + str(self.name) + "_session_history.csv"
		csv_entry = str(self.session_count) + "," + str(self.name) + "," + str(self.ID) + "," + str(trial_count) + "," + str(start_time) + "," + str(end_time) + "," + str(self.training_stage) + "," + str(self.dominant_hand)  + "\n"

		with open(session_history, "a") as log:
			log.write(csv_entry)




class SessionController(object):
	"""
		A controller for all sessions that occur within the system. A "session" is defined as everything that happens while an animal is in the
                experiment tube. A session is started when an animal first breaks the IR beam AND then triggers the RFID reader (Note: Triggering
                the RFID reader alone will not start a session. The IR beam must be broken first. This is intentional as the IR beam is for pressence
                detection while the RFID reader is only for identification). The session will continue until the IR beam is reconnected.
                A SessionController has the following properties:

		Attributes:
			profile_list: A list containing all animal profiles.
			servo: An object that controls a servo.
			stepper_controller: An object that controls stepper motors.
			camera: An object that controls a camera.
			RFID_reader: An object that controls an RFID reader.
            IR_beam_breaker: An object that controls an IR beam breaker.
	"""

	def __init__(self, profile_list, servo, stepper_controller, camera, RFID_reader, IR_beam_breaker):

		self.profile_list = profile_list
		self.servo = servo
		self.stepper_controller = stepper_controller
		self.camera = camera
		self.RFID_reader = RFID_reader
		self.IR_beam_breaker = IR_beam_breaker





	# This function searches the SessionController's profile_list for a profile whose ID
	# matches the supplied RFID. If a profile is found, it is returned. If no profile is found,
	# -1 is returned.
	def searchForProfile(self, RFID):

		for profile in self.profile_list:

		    if profile.ID == RFID:
                        return profile

                return -1


    # This function starts an experiment session for the animal identified in the supplied <profile>.
    # A session is only started if the IR beam is broken and only continues while this remains true.
    # Each session forks a process that records video for the duration of the session and forks
    # another process which controls the servo for the duration of the session. Each session
    # will also log data about itself. As soon as the session detects the IR beam reconnect,
    # a destruct signal will be sent to all forked processes and this function will wait to join
    # with those processes before concluding the session.
    #TODO: This function is really bloated. Should be broken into 4-5 smaller functions.
	def startSession(self, profile):

		if self.IR_beam_breaker.getBeamState() != 0:

			console_err_msg1 = profile.ID + " recognized but IR beam NOT broken.\nAborting session.\n\n"
			print(console_err_msg1)
			return
		else:

			session_start_msg = "-------------------------------------------\n" + "Starting session for " + profile.name
			print(session_start_msg)
			session_start_time = time.time()



		#TODO video_output_path should be constructed by a member method of AnimalProfile.
		profile.session_count += 1
		video_output_path = profile.video_save_directory + str(profile.name) + "_session#_"  + str(profile.session_count) + ".avi"

		# Fork processes for camera recording and for servo cycling.
		jobs = []
		servo_process_queue = multiprocessing.Queue()
		camera_process_queue = multiprocessing.Queue()
		main_process_queue = multiprocessing.Queue()

		camera_process = multiprocessing.Process(target=self.camera.captureVideo, args=(video_output_path, camera_process_queue, servo_process_queue, main_process_queue,))
		jobs.append(camera_process)

		servo_process = multiprocessing.Process(target=self.servo.cycleServo, args=(servo_process_queue,))
		jobs.append(servo_process)

		camera_process.start()
		servo_process.start()


		# Adjust bed position based on mouse profile information
		if profile.training_stage == 1:
			self.stepper_controller.queue.put("0POS1")

		elif profile.training_stage == 2:
			self.stepper_controller.queue.put("0POS2")

		elif profile.training_stage == 3:
			self.stepper_controller.queue.put("0POS3")

		elif profile.training_stage == 4:
			self.stepper_controller.queue.put("0POS4")


		#if profile.dominant_hand == "LEFT":
		#	stepper_process_queue.put("1LEFT")

		#elif profile.dominant_hand == "RIGHT":
		#	stepper_process_queue.put("1RIGHT")



		# While beam is still broken, continue session.
		while self.IR_beam_breaker.getBeamState() == 0:

			sleep(0.2)



		# Once beam is reconnected. Send kill sig to all session processes and wait for them to terminate.
		camera_process_queue.put("TERM")
		servo_process_queue.put("TERM")
		camera_process.join()
		servo_process.join()


		# Log session information.
		session_end_time = time.time()
		trial_count = int(main_process_queue.get())
		profile.insertSessionEntry(session_start_time, session_end_time, trial_count)
		profile.saveProfile()

		# Flush serial buffer incase RFID tag was read multiple times during this session.
		self.RFID_reader.flushRFIDBuffer()
		session_end_msg = profile.name + "'s session has completed\n-------------------------------------------\n"
		print(session_end_msg)
		return 0




# Servo config
SERVO_PWM_BCM_PIN_NUMBER = 18
# Stepper config
pulse_pins_x = [7,11,13,15]
pulse_pins_y = [7,11,13,15]
# Camera config
FOURCC = "*MJPG"
CAMERA_INDEX = 0
CAMERA_FPS = 60.0
CAMERA_RES = (640,480)
# RFID config
SERIAL_INTERFACE_PATH = "/dev/ttyUSB0"
BAUDRATE = 9600
RFID_PROXIMITY_BCM_PIN_NUMBER = 23
# IR breaker config
PHOTO_DIODE_BCM_PIN_NUMBER = 24
# ObjectDetector config
PRIMARY_CASCADE = "../config/hopper_arm_pellet.xml"
with open("../config/config.txt") as config:
	roi_x = int(config.readline())
	roi_y = int(config.readline())
	roi_w = int(config.readline())
	roi_h = int(config.readline())
config.close()
# AnimalProfile config
PROFILE_SAVE_DIRECTORY = "../AnimalProfiles/"




def main():

# Uncomment these to generate new profiles
#	profile0 = AnimalProfile("0782B18367", "Jim Kirk", 1, "LEFT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile1 = AnimalProfile("0782B1797D", "Yuri Gagarin", 1, "LEFT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile2 = AnimalProfile("0782B191B5", "Elon Musk", 1, "RIGHT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile3 = AnimalProfile("0782B19BCF", "Buzz Aldrin", 1, "RIGHT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile4 = AnimalProfile("0782B18A1E", "Test Tag0", 1, "RIGHT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile5 = AnimalProfile("0782B189DD", "Test Tag1", 1, "LEFT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile6 = AnimalProfile("0782B19226", "Test Tag2", 2, "RIGHT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile7 = AnimalProfile("0782B18783", "Test Tag3", 3, "RIGHT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile8 = AnimalProfile("0782B1884C", "Test Tag4", 4, "LEFT", 0, PROFILE_SAVE_DIRECTORY, True)
#	profile0.saveProfile()
#	profile1.saveProfile()
#	profile2.saveProfile()
#	profile3.saveProfile()
#	profile4.saveProfile()
#	profile5.saveProfile()
#	profile6.saveProfile()
#	profile7.saveProfile()
#	profile8.saveProfile()
#	exit()


    # Initialize every system component
	profile_list = loadAnimalProfiles(PROFILE_SAVE_DIRECTORY)
	servo_1 = servo.Servo(SERVO_PWM_BCM_PIN_NUMBER)
	stepper_controller = stepper.StepperController()
	stepper_controller.initStepper(pulse_pins_x)
	stepper_controller.initStepper(pulse_pins_y)
	obj_detector_1 = objectDetector.ObjectDetector(PRIMARY_CASCADE, roi_x, roi_y, roi_w, roi_h)
	camera_1 = camera.Camera(FOURCC, CAMERA_INDEX, CAMERA_FPS, CAMERA_RES, obj_detector_1)
	RFID_1 = RFID.RFID_Reader(SERIAL_INTERFACE_PATH, BAUDRATE, RFID_PROXIMITY_BCM_PIN_NUMBER)
	IR_1 = IR.IRBeamBreaker(PHOTO_DIODE_BCM_PIN_NUMBER)
	session_controller = SessionController(profile_list, servo_1, stepper_controller, camera_1, RFID_1, IR_1)



    # TODO: Servos and cameras should be controlled the same way as steppers are, shown below. Switch them to long lived
    #       processes that are controlled via message passing queues.
    #
    # Start Stepper Motor daemon
	jobs = []
	stepper_process = multiprocessing.Process(target=stepper_controller.initDaemon, args=())
	jobs.append(stepper_process)
	stepper_process.start()

    # Entry point of the system. This block waits for an RFID to enter the <SERIAL_INTERFACE_PATH> buffer.
    # Once it receives an RFID, it parses it and searches for a profile with a matching RFID. If a profile
    # is found, it starts a session for that profile. If not profile is found, it goes back to listening for
    # an RFID.
	while True:

		print("Waiting for RF tag...")
		RFID_code = session_controller.RFID_reader.listenForRFID()
		profile = session_controller.searchForProfile(RFID_code)

		if profile != -1:
			session_controller.startSession(profile)

		else:
			unrecognized_id_msg = RFID_code + " not recognized. Aborting session.\n\n"
			print(unrecognized_id_msg)


# Python convention for launching main() function.
if __name__ == "__main__":
    main()
