import numpy as np
import cv2




class ObjectDetector(object):

    """ 
        This class contains all relevant data and information for running haar-cascade image detection.
        Each instance of this class is given a cascade.xml file. This file represents a cascade that has 
        been trained to identify a particular object. This file is supplied to the image detection
        algorithm to describe to it what it is looking for. To change what you're trying to detect,
        simply supply a new cascade.xml file. 
    """



    def __init__(self, primary_cascade, x, y, w, h):

        pellet_cascade = cv2.CascadeClassifier(primary_cascade)
        self.roi_x = x
        self.roi_y = y
        self.roi_w = w
        self.roi_h = h


    # This function pre-processes a frame and then runs a haar-cascade using <self.primary_cascade>.
    # If the frame produces a positive detection, a rectangle is drawn around the detection ROI. 
    # The frame is always returned with an integer describing the number of detections in that frame.
    def detectCascade(self, frame):


        # Crop frame to isolate ROI (This saves on CPU cycles and reduces false positives from objects outside ROI)
        cropped = frame[self.roi_y:(self.roi_y + self.roi_h), self.roi_x:(self.roi_x + self.roi_w)]
        # Grayscale to reduce number of channels to save on CPU cycles during frame scan 
        gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
        # Run haar-cascade on cropped/grayscaled image
        pellets = pellet_cascade.detectMultiScale(gray, 1.2, 10)

        # Draw a rectangle around each object identified by haar-cascade
        for (x,y,w,h) in pellets:
       
            cv2.rectangle(cropped,(x,y),(x+w,y+h),(255,255,0),2)
        
        # Stitch ROI with drawn rectangles back into original frame 
        frame[self.roi_y:(self.roi_y + self.roi_h), self.roi_x:(self.roi_x + self.roi_w)] = cropped 

        # Return frame and number of objects detected in ROI
        ret = [frame, len(pellets)]
        return ret 
