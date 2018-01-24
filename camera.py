import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple):
        
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = fps
	self.camera_index = camera_index
        self.res_tuple = res_tuple


    def captureVideo(self, output_filename, queue):

        camera_output = cv2.VideoWriter(output_filename, self.fourcc, self.fps, self.res_tuple)
	camera = cv2.VideoCapture(self.camera_index)
        while True:
		
		if queue.empty() == False:
			termination_msg = "Camera process termination: " + queue.get() 
			print(termination_msg)
			camera.release()
			camera_output.release()
			cv2.destroyAllWindows()
			return

		ret, frame = camera.read()

            	cv2.imshow("live_feed", frame)
            	if cv2.waitKey(1) & 0xFF == ord('q'):
                	break
            	else:
                	camera_output.write(frame)

