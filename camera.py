import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple):
        
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.camera = cv2.VideoCapture(0)
        self.fps = fps
        self.res_tuple = res_tuple


    def captureVideo(self, output_filename):

        camera_output = cv2.VideoWriter(output_filename, self.fourcc, self.fps, self.res_tuple)

        while True:

		ret, frame = self.camera.read()
            	cv2.imshow("live_feed", frame)
            	if cv2.waitKey(1) & 0xFF == ord('q'):
                	break
            	else:
                	camera_output.write(frame)

