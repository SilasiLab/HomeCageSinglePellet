import servo
import camera 
import RFID
import IR 
import objectDetector
import time 
from time import sleep 
import multiprocessing
import logging

logging.basicConfig(filename="logfile.log", level=logging.DEBUG)
main_logger = logging.getLogger(__name__)
servo_logger = logging.getLogger("servo.py")
camera_logger = logging.getLogger("camera.py")



class AnimalProfile(object):

	def __init__(self, ID, name, training_stage, session_count, session_history_directory, video_save_directory):

		self.ID = ID
		self.name = name
		self.training_stage = training_stage  
		self.session_count = session_count
		self.session_history_directory = session_history_directory
		self.video_save_directory = video_save_directory 


	# This function takes all the information required for an animal's session log entry, and then formats it.
	# Once formatted, it writes the log entry to the animal's session_history log file. 
	def insertSessionEntry(self, start_time, end_time):

		#TODO: Is there a better way to create + format strings?
		session_path = self.session_history_directory + str(self.ID) + "_session_history.txt"
		csv_entry = str(start_time) + "," + str(end_time) + "," + self.video_save_directory + "\n"

		with open(session_path, "a") as session_history:
			session_history.write(csv_entry)
			self.session_count += 1





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
			camera: An object that controls a camera.
			RFID_reader: An object that controls an RFID reader.
                        IR_beam_breaker: An object that controls an IR beam breaker.
	"""

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
        #TODO: This function seems really bloated. Try to break it down into smaller pieces.
	def startSession(self, profile):


            main_logger.info("Checking IR beam state")
	    if self.IR_beam_breaker.getBeamState() != 0:

                main_logger.info("IR beam not broken. Aborting session")
            	console_err_msg1 = profile.ID + " recognized but IR beam NOT broken.\nAborting session.\n\n"
		print(console_err_msg1)
		return 
            else:
                main_logger.info("IR beam broken. Continuing session")
                session_start_msg = "-------------------------------------------\n" + "Starting session for " + profile.name
	        print(session_start_msg)
            

	    session_start_time = time.time()
            
            #TODO video_output_path should be constructed by a member method of AnimalProfile.
	    video_output_path = profile.video_save_directory + str(profile.ID) + "_session#_"  + str(profile.session_count) + ".avi"

            # Fork processes for camera recording and for servo cycling.
            jobs = []
            servo_process_queue = multiprocessing.Queue()
	    camera_process_queue = multiprocessing.Queue()

            main_logger.info("Initializing camera process")
            camera_process = multiprocessing.Process(target=self.camera.captureVideo, args=(video_output_path, camera_process_queue, servo_process_queue, camera_logger,))
            jobs.append(camera_process)
            
            main.logger.info("Initializing servo process")
            servo_process = multiprocessing.Process(target=self.servo.cycleServo, args=(servo_process_queue, servo_logger,))
            jobs.append(servo_process)
            
            main_logger.info("Launching camera process")
	    camera_process.start()
            main_logger.info("Launching servo process")
            servo_process.start()

            main_logger.info("Beginning IR beam state monitoring")
            # While beam is still broken, continue session.
            while self.IR_beam_breaker.getBeamState() == 0:
                    
                    sleep(0.3)


            # Once beam is reconnected. Send kill sig to all session processes and wait for them to terminate.
            main_logger.info("Sending TERM signal to camera process")
	    camera_process_queue.put("TERM")
            main_logger.info("Sending TERM signal to servo process")
            servo_process_queue.put("TERM")

            main_logger.info("Calling camera_process.join()")
            camera_process.join()
            main_logger.info("Calling servo_process.join()")
            servo_process.join()


            main_logger.info("Logging experiment data")
            # Log session information.
            session_end_time = time.time()	
	    profile.insertSessionEntry(session_start_time, session_end_time)	

            main_logger.info("Flushing serial buffer")
	    # Flush serial buffer incase RFID tag was read multiple times during this session.
	    self.RFID_reader.flushRFIDBuffer()

            session_end_msg = profile.name + "'s session has completed\n-------------------------------------------\n" 
            print(session_end_msg)
	    return 0




# Servo config
SERVO_PWM_BCM_PIN_NUMBER = 18
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
PRIMARY_CASCADE = "./hopper_arm_pellet.xml"
roi_x = 0
roi_y = 0
roi_w = 0
roi_h = 0
# AnimalProfile config
SESSION_SAVE_PATH = "./AnimalSessions/"
VIDEO_SAVE_PATH = "./AnimalSessions/Videos/"



def main():
   

        main_logger.info("Creating AnimalProfiles...")
	profile0 = AnimalProfile("0782B18367", "Jim Kirk", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile1 = AnimalProfile("0782B1797D", "Yuri Gagarin", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile2 = AnimalProfile("0782B191B5", "Elon Musk", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile3 = AnimalProfile("0782B19BCF", "Buzz Aldrin", 0, 0, SESSION_SAVE_PATH, VIDEO_SAVE_PATH)
	profile_list = [profile0, profile1, profile2, profile3]

        main_logger.info("Initializing servo")
	servo_1 = servo.Servo(SERVO_PWM_BCM_PIN_NUMBER)

        main_logger.info("Initializing ObjectDetector")
        obj_detector_1 = objectDetector.ObjectDetector(PRIMARY_CASCADE, roi_x, roi_y, roi_w, roi_h)
        main_logger.info("Initializing camera")
	camera_1 = camera.Camera(FOURCC, CAMERA_INDEX, CAMERA_FPS, CAMERA_RES, obj_detector_1)

        main_logger.info("Initializing RFID reader")
	RFID_1 = RFID.RFID_Reader(SERIAL_INTERFACE_PATH, BAUDRATE, RFID_PROXIMITY_BCM_PIN_NUMBER) 
        main_logger.info("Initializing IR beam breaker")
        IR_1 = IR.IRBeamBreaker(PHOTO_DIODE_BCM_PIN_NUMBER)
        main_logger.info("Initializing SessionController")
	session_controller = SessionController(profile_list, servo_1, camera_1, RFID_1, IR_1)


	while True:

            main_logger.info("Waiting for RF tag")
	    print("Waiting for RF tag...")
	    RFID_code = session_controller.RFID_reader.listenForRFID()

            main_logger.info("Searching for AnimalProfile with matching RFID")
            # Attempt to find a profile matching the detected RFID.
	    profile = session_controller.searchForProfile(RFID_code)

            # If a profile with a matching RFID is found, begin a session for that profile.
            if profile != -1:
                main_logger.info("Starting session")
	        session_controller.startSession(profile)
	    else:
                main_logger.info("No AnimalProfile found with matching RFID. Aborting session")
		unrecognized_id_msg = RFID_code + " not recognized. Aborting session.\n\n"
		print(unrecognized_id_msg)



if __name__ == "__main__":
    main()
