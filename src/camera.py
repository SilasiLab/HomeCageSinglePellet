import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple, object_detector):
        
        self.fourcc = cv2.VideoWriter_fourcc(*'MJPG')
        self.fps = fps
	self.camera_index = camera_index
        self.res_tuple = res_tuple
        self.object_detector = object_detector 




    def captureVideo(self, output_filename, queue, servo_queue, main_queue):

		camera_output = cv2.VideoWriter(output_filename, self.fourcc, self.fps, self.res_tuple)
		camera = cv2.VideoCapture(self.camera_index)
		trial_counter = 0
		pellet_not_present_frame_counter = 0

		while True:
		
			if queue.empty():
 
				ret, frame = camera.read()
				# Run object detection on frame and send signal to servo process if pellet needs replacing 
				detection = self.object_detector.detectCascade(frame)

				if detection[1] == 0:

					pellet_not_present_frame_counter += 1
                    
					if pellet_not_present_frame_counter >= 35:
                        
						servo_queue.put("GETPELLET")
						trial_counter += 1
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
					camera.release()
					camera_output.release()
					cv2.destroyAllWindows()
					main_queue.put(trial_counter)
					return 0
           
