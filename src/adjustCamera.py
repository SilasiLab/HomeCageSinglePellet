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
		with open("../config/config.txt", 'w') as file:
			file.write(str(r[0]) + "\n")
			file.write(str(r[1]) + "\n")
			file.write(str(r[2]) + "\n")
			file.write(str(r[3]) + "\n")
			print("ROI configuration has been updated")
