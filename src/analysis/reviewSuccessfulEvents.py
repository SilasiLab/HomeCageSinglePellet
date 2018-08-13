from glob import glob
import os
import cv2
import numpy as np

VIDEO_DIRECTORY="../../AnimalProfiles/"
PROFILE = input("Enter mouse name: ")
VIDEO_NAME = input("Enter video name: ")
profilePaths = []




videoName = ""
lines = []
with open(VIDEO_DIRECTORY + PROFILE + "/Analyses/" + VIDEO_NAME[:-4] + "_reaches.txt") as f:
	videoName = f.readline()
	print("Video Name="+ videoName)
	totalReaches = f.readline()
	print("TotalReaches=" + totalReaches)
	lines = f.readlines()


video = cv2.VideoCapture(VIDEO_DIRECTORY + PROFILE + "/Videos/" + VIDEO_NAME)#str(profile) + "Videos/" + str(videoName))
index = 0
while index < len(lines):

	event = lines[index]
	print("Event: " + event)
	index += 1
	start = int(lines[index])
	print("Start frame: " + str(start))
	index += 1
	stop = int(lines[index])
	print("Stop Frame: " + str(stop))
	index += 1
	video.set(1,start)
	for frameIndex in range(start, stop):
		ret, frame = video.read()
		cv2.imshow(videoName, frame)
		if cv2.waitKey(0) & 0xFF == ord('q'):
			break
