import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple, object_detector):
        
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = fps
	self.camera_index = camera_index
        self.res_tuple = res_tuple
        self.object_detector = object_detector 

    def captureVideo(self, output_filename, queue, servo_queue, logger):

        logger.info("Initializing cv2.VideoWriter")
        camera_output = cv2.VideoWriter(output_filename, self.fourcc, self.fps, self.res_tuple)
        logger.info("Opening camera for cv2.VideoCapture")
	camera = cv2.VideoCapture(self.camera_index)

        pellet_not_present_frame_counter = 0

        while True:
		
	    if queue.empty():
 
		ret, frame = camera.read()
                # Run object detection on frame and send signal to servo process if pellet needs replacing 
                detection = self.object_detector.detectCascade(frame)

                if detection[1] == 0:

                    pellet_not_present_frame_counter += 1
                    
                    if pellet_not_present_frame_counter >= 60:
                        
                        servo_queue.put("GETPELLET")
                        pellet_not_present_frame_counter = 0

                elif detection[1] >= 1:
                    
                    pellet_not_present_frame_counter = 0



            	cv2.imshow("live_feed", detection[0])
            	if cv2.waitKey(1) & 0xFF == ord('q'):
                    break 
            	else:
                    camera_output.write(frame)
            else:

	        msg = queue.get()
                if msg == "TERM":

                    logger.info("TERM message received. Cleaning up and then terminating process")
		    camera.release()
		    camera_output.release()
		    cv2.destroyAllWindows()
		    return 0
           
