import servo
import camera
import RFID
import IR
import stepper
import objectDetector
import gui
import time
from time import sleep
from datetime import datetime
import multiprocessing
import logging
import os



logging.basicConfig(filename="../logs/logfile.log", level=logging.DEBUG)
main_logger = logging.getLogger(__name__)



#This function generates a list of AnimalProfiles found inside <profile_save_directory>.
#It then reads the save.txt file for each profile found, and uses the information
#in that file to reconstruct the AnimalProfile object. It returns all the
#reconstructed profiles as a list of AnimalProfiles.
#Note: This function works by assuming the directory structure of each AnimalProfile
#is consistent and the required save.txt files are present, i.e:
#
# <profile_save_directory>
#   -
#   - ProfileName
#       -
#       - Logs
#       - Videos
#       - save.txt

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
		mouseNumber = profile_state[2]
		cageNumber = profile_state[3]
		difficulty_dist_mm = profile_state[4]
		dominant_hand_dist_mm = profile_state[5]
		session_count = profile_state[6]
		animal_profile_directory = profile_state[7]
		temp = AnimalProfile(ID, name, mouseNumber, cageNumber, difficulty_dist_mm, dominant_hand_dist_mm, session_count, animal_profile_directory, False)
		profiles.append(temp)


	return profiles




class AnimalProfile(object):

    #    A profile containing all information related to a particular animal. When a new animal is added to the system,
    #    an AnimalProfile should be created for that animal. This profile will be used by the rest
    #    of the system for any operation pertaining to the animal (data logging, identification, etc). When the application closes,
    #    saveProfile() should be called on each profile in the system. A global loadProfiles() function is used to load/reconstruct
    #    each profile at load time. Each AnimalProfile has the following properties:
	#
    #    Attributes:
    #        ID: A unique identification number for the animal. In our case this number will be the RFID of the RF tag implanted in the animal.
    #        name: The name of the animal
	#		 mouseNumber: The number of the animal in it's cage (0-5).
	#		 cageNumber: The cage number of the animal.
    #        difficulty_dist_mm: An integer representing the distance from the tube to the presented pellet in mm.
    #        dominant_hand_dist_mm: An integer representing how far to either side the pellet will be presented in mm.
    #        session_count: The number of Sessions the animal has participated in. In our system, this is the number of times the animal has
    #                        entered the experiment tube.
    #        animal_profile_directory: A path to the root folder where AnimalProfile's are stored.
    #        video_save_directory: A path to where the videos for this animal are stored. This path will be inside [./<animal_profile_directory>/<animal_name>/]
    #        log_save_directory: A path to where the logs for this animal are stored. This pathh will be inside [./<animal_profile_directory/<animal_name/]




	def __init__(self, ID, name, mouseNumber, cageNumber, difficulty_dist_mm, dominant_hand_dist_mm, session_count, profile_save_directory, is_new):

		self.ID = str(ID)
		self.name = str(name)
		self.mouseNumber = str(mouseNumber)
		self.cageNumber = str(cageNumber)
		self.difficulty_dist_mm = int(difficulty_dist_mm)
		self.dominant_hand_dist_mm = str(dominant_hand_dist_mm)
		self.session_count = int(session_count)


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
			save.write(str(self.mouseNumber) + "\n")
			save.write(str(self.cageNumber) + "\n")
			save.write(str(self.difficulty_dist_mm) + "\n")
			save.write(str(self.dominant_hand_dist_mm) + "\n")
			save.write(str(self.session_count) + "\n")
			save.write(str(self.animal_profile_directory) + "\n")


    # Generates the path where the video for the next session will be stored
	def genVideoPath(self):
		return str(self.video_save_directory) + str(self.name) + "_session#_" + str(self.session_count) + ".avi"


	# This function takes all the information required for an animal's session log entry, and then formats it.
	# Once formatted, it appends the log entry to the animal's session_history.csv file.
	def insertSessionEntry(self, start_timestamp, end_timestamp, trial_count):

		#TODO: Is there a better way to create + format strings?
		session_history = self.log_save_directory + str(self.name) + "_session_history.csv"
		start_date = time.strftime("%d-%b-%Y", time.localtime(start_timestamp))
		start_time = time.strftime("%H:%M:%S", time.localtime(start_timestamp))
		end_date = time.strftime("%d-%b-%Y", time.localtime(end_timestamp))
		end_time = time.strftime("%H:%M:%S", time.localtime(end_timestamp))
		csv_entry = str(self.session_count) + "," + str(self.name) + "," + str(self.ID) + "," + str(trial_count) + "," + str(self.difficulty_dist_mm) + "," + str(self.dominant_hand_dist_mm)  + "," + start_date + "," + start_time + "," + end_date + "," + end_time + "\n"

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
			stepper_controller_x: An object that controls the stepper motor for the x plane.
			stepper_controller_y: An object that controls the stepper motor for the y plane.
			camera: An object that controls a camera.
			RFID_reader: An object that controls an RFID reader.
            IR_beam_breaker: An object that controls an IR beam breaker.
	"""

	def __init__(self, profile_list, servo, stepper_controller_x, stepper_controller_y, camera, RFID_reader, IR_beam_breaker):

		self.profile_list = profile_list
		self.servo = servo
		self.stepper_controller_x = stepper_controller_x
		self.stepper_controller_y = stepper_controller_y
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
			human_readable_start_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(session_start_time))
			print("Start Time: {}".format(human_readable_start_time))



		profile.session_count += 1
		video_output_path = profile.genVideoPath()

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

		# Send msg to StepperController to adjust x position according to profile.training_stage
		x_msg = "POS" + str(profile.dominant_hand_dist_mm)
		self.stepper_controller_x.queue.put(x_msg)
		# Send msg to StepperController to adjust y position according to profile.dominant_hand
		y_msg = "POS" + str(profile.difficulty_dist_mm)
		self.stepper_controller_y.queue.put(y_msg)


		# While beam is still broken, continue session.
		while self.IR_beam_breaker.getBeamState() == 0:

			sleep(0.2)


		# Once beam is reconnected. Send kill/pause sig to all session processes and wait for them to terminate/pause.
		self.stepper_controller_x.queue.put("INTM")
		self.stepper_controller_y.queue.put("INTM")
		camera_process_queue.put("TERM")
		servo_process_queue.put("TERM")
		camera_process.join()
		servo_process.join()


		# Log session information.
		session_end_time = time.time()
		human_readable_end_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime(session_end_time))
		print("End Time: {}".format(human_readable_end_time))
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
PULSE_PINS_X = [7,11,13,15]
PULSE_PINS_Y = [1,16,20,21]
STEPS_MM_RATIO = 450
# Camera config
FOURCC = "*MJPG"
CAMERA_INDEX = 0
CAMERA_FPS = 60.0
CAMERA_RES = (640,480)
# RFID config
SERIAL_INTERFACE_PATH = "/dev/ttyUSB0"
BAUDRATE = 9600
RFID_PROXIMITY_BCM_PIN_NUMBER = 24
# IR breaker config
PHOTO_DIODE_BCM_PIN_NUMBER = 23
# ObjectDetector config
PRIMARY_CASCADE = "../config/hopper_arm_pellet.xml"
with open("../config/config.txt") as config:
	roi_x = int(config.readline())
	roi_y = int(config.readline())
	roi_w = int(config.readline())
	roi_h = int(config.readline())
config.close()
# AnimalProfile config
PROFILE_SAVE_DIRECTORY = "/home/pi/Desktop/AnimalProfiles/"




def main():

# Uncomment these to generate new profiles
#	profile0 = AnimalProfile("0782B190A4", "43036_MOUSE1", 1, 43036, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile1 = AnimalProfile("0782B18BBF", "43036_MOUSE2", 2, 43036, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile2 = AnimalProfile("0782B194F0", "43036_MOUSE3", 3, 43036, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile3 = AnimalProfile("0782B180C4", "43036_MOUSE4", 4, 43036, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile4 = AnimalProfile("0782B18783", "Test Tag0", 0, 43036, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile5 = AnimalProfile("0782B189DD", "Test Tag1", 0, 0, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile6 = AnimalProfile("0782B19226", "Test Tag2", 0, 0, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile7 = AnimalProfile("0782B18783", "Test Tag3", 0, 0, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
#	profile8 = AnimalProfile("0782B1884C", "Test Tag4", 0, 0, 1, 1, 0, PROFILE_SAVE_DIRECTORY, True)
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
	stepper_controller_x = stepper.StepperController(PULSE_PINS_X, STEPS_MM_RATIO)
	stepper_controller_y = stepper.StepperController(PULSE_PINS_Y, STEPS_MM_RATIO)
	obj_detector_1 = objectDetector.ObjectDetector(PRIMARY_CASCADE, roi_x, roi_y, roi_w, roi_h)
	camera_1 = camera.Camera(FOURCC, CAMERA_INDEX, CAMERA_FPS, CAMERA_RES, obj_detector_1)
	RFID_1 = RFID.RFID_Reader(SERIAL_INTERFACE_PATH, BAUDRATE, RFID_PROXIMITY_BCM_PIN_NUMBER)
	IR_1 = IR.IRBeamBreaker(PHOTO_DIODE_BCM_PIN_NUMBER)
	session_controller = SessionController(profile_list, servo_1, stepper_controller_x, stepper_controller_y, camera_1, RFID_1, IR_1)


    # TODO: Servos and cameras should be controlled the same way as steppers are, shown below. Switch them to long lived
    #       processes that are controlled via message passing queues.
    #
    # Start Stepper Motor daemons
	jobs = []
	stepper_x_process = multiprocessing.Process(target=stepper_controller_x.initDaemon, args=())
	stepper_y_process = multiprocessing.Process(target=stepper_controller_y.initDaemon, args=())
	jobs.append(stepper_x_process)
	jobs.append(stepper_y_process)
	stepper_x_process.start()
	stepper_y_process.start()

	# Start GUI
	gui_process = multiprocessing.Process(target=gui.start_gui_loop, args=(PROFILE_SAVE_DIRECTORY,))
	jobs.append(gui_process)
	gui_process.start()

    # Entry point of the system. This block waits for an RFID to enter the <SERIAL_INTERFACE_PATH> buffer.
    # Once it receives an RFID, it parses it and searches for a profile with a matching RFID. If a profile
    # is found, it starts a session for that profile. If no profile is found, it goes back to listening for
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
