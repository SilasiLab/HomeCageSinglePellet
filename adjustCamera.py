import cv2
import numpy as np

camera = cv2.VideoCapture(0)


while True:
	ret,frame = camera.read()
	cv2.imshow("feed", frame)
	if cv2.waitKey(1) & 0xFF == ord('q'):
        	break 
	elif cv2.waitKey(1) & 0xFF == ord('s'):

		r = cv2.selectROI(frame)
		print(r[0])
		print(r[1])
		print(r[2])
		print(r[3])