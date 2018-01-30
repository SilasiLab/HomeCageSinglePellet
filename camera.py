import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple):
        
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = fps
	self.camera_index = camera_index
        self.res_tuple = res_tuple


    def captureVideo(self, output_filename, queue, logger):

        logger.info("Initializing cv2.VideoWriter")
        camera_output = cv2.VideoWriter(output_filename, self.fourcc, self.fps, self.res_tuple)
        logger.info("Opening camera for cv2.VideoCapture")
	camera = cv2.VideoCapture(self.camera_index)

        while True:
		
	    if not queue.empty():

		msg = queue.get()
                if msg == "TERM":
                    logger.info("TERM message received. Cleaning up and then terminating process")
		    camera.release()
		    camera_output.release()
		    cv2.destroyAllWindows()
		    return 0
            else:

		ret, frame = camera.read()
            	cv2.imshow("live_feed", frame)
            	if cv2.waitKey(1) & 0xFF == ord('q'):
                    break 
            	else:
                    camera_output.write(frame)
