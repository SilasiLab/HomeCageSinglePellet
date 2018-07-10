import numpy as np
import cv2


class Camera(object):

    def __init__(self, fourcc, camera_index, fps, res_tuple, object_detector):

        self.fourcc = cv2.VideoWriter_fourcc('X','V','I','D')
        self.fps = fps
        self.camera_index = camera_index
        self.res_tuple = res_tuple
        self.object_detector = object_detector



    # This function is being used as the entry point for a process that is forked by
    # main. It does like 5 things. This needs a rewrite, badly.
    def captureVideo(self, output_filename, queue, mainQueue):

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

                    # TODO change the 200 back to 35 after testing
                    if pellet_not_present_frame_counter >= 200:

                        mainQueue.put("GETPEL")
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
                    mainQueue.put(str(trial_counter))
                    return 0
