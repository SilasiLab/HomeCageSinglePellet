import pandas as pd
import numpy as np
import cv2
from functools import reduce
import sys

ANALYSES_DIRECTORY = sys.argv[1]
VIDEO_DIRECTORY = sys.argv[2]
videoName = sys.argv[3]
# Place the name of each model used to analyze the video in this list.
# These will be used to find the .h5 output file of each model.
modelNames = [
    "DeepCut_resnet50_eatingJuly23shuffle1_50000",
    "DeepCut_resnet50_reachingAug1shuffle1_50000"]

# Name of poses that the models were trained to detect.
# Must be in the same order as the corresponding model names
# in <modelNames>.
poseNames = [
    "eating",
    "reaching"]

likelihoodCutoffs = [
    0.9,
    0.9]

minFrameCounts = [
    20,
    10]

maxFrameCounts = [
    10,
    10]


class PoseEvent:

    def __init__(self, startFrame, stopFrame, eventType):

        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType

class BehaviourEvent:

    def __init__(self, startFrame, stopFrame, eventType):
        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType



# Generate the names of each .h5 output file from each model used
# to analyze the current video.
modelH5OutputFilePaths = []
for i in range(0,len(modelNames)):
    modelH5OutputFilePaths.append(ANALYSES_DIRECTORY + videoName[:-4] + modelNames[i] + ".h5")

# Read each .h5 output file into Dataframe
h5Files = []
for path in modelH5OutputFilePaths:
    dataframe = pd.read_hdf(path)
    #dataframe.to_csv(path[:-3] + ".csv")
    h5Files.append(dataframe)


def packageEvent(frameIndexes, poseName):

    tempEvent = PoseEvent(frameIndexes[0], frameIndexes[len(frameIndexes) - 1], poseName)
    return tempEvent

def extractEvents(index, bodyparts):

    dataframe = h5Files[index]
    poseName = poseNames[index]
    modelName = modelNames[index]
    eventStarted = False
    contiguousPositiveCount = 0
    contiguousNegativeCount = 0
    tempEventFrameRange = []
    events = []
    row = 0

    while row < len(dataframe.index):
        confidence = 1
        likelihoodIndex = 2
        for bodypart in bodyparts:
            confidence *= dataframe.iat[row, likelihoodIndex]
            likelihoodIndex += 3

        if(eventStarted):
            if(confidence < likelihoodCutoffs[index]):
                contiguousNegativeCount += 1
            else:
                contiguousNegativeCount = 0

            tempEventFrameRange.append(row)

            if(contiguousNegativeCount >= maxFrameCounts[index]):
                contiguousPositiveCount = 0
                contiguousNegativeCount = 0
                events.append(packageEvent(tempEventFrameRange, poseName))
                tempEventFrameRange = []
                row += 200
                eventStarted = False

            row += 1
            continue

        if(confidence >= likelihoodCutoffs[index]):

            contiguousPositiveCount += 1
            tempEventFrameRange.append(row)
        else:
            contiguousPositiveCount = 0
            tempEventFrameRange = []

        if(contiguousPositiveCount >= minFrameCounts[index]):
            eventStarted = True

        row += 1

    return events



def findBehaviourPattern(video, poseAnalysis):

    successfulReaches = []


    for reach in poseAnalysis[1]:
            for eating in poseAnalysis[0]:
                if eating.startFrame >= reach.startFrame and eating.startFrame <= reach.stopFrame + 150:
                    successfulReaches.append(BehaviourEvent(reach.startFrame, eating.stopFrame, 'Successful Reach'))
                    print("Successful Reach Found")
                    break
                elif eating.startFrame >= reach.stopFrame + 151:
                    break

    return successfulReaches








video = cv2.VideoCapture(VIDEO_DIRECTORY + videoName)
print(VIDEO_DIRECTORY + videoName)
poseAnalysis = []
poseAnalysis.append(extractEvents(0,['bottom','middle','top','nose']))
print('eatPose done')
poseAnalysis.append(extractEvents(1,['wrist', 'pawcenter', 'digit1', 'digit2', 'digit3']))
print('reachPose done')

print('Finding successful reaches...')
successfulReaches = findBehaviourPattern(video,poseAnalysis)
with open(ANALYSES_DIRECTORY + videoName[:-4] +"_reaches.txt", 'w') as f:
    f.write(videoName + "\n")
    f.write(str(len(poseAnalysis[1])) + "\n")
    for reach in successfulReaches:
        f.write(reach.eventType + "\n")
        f.write(str(reach.startFrame) + "\n")
        f.write(str(reach.stopFrame) + "\n")


#Uncomment below to view behavior events
#print(len(successfulReaches))
#for reach in successfulReaches:
#    print("Event: " + reach.eventType)
#    print("Start frame: " + str(reach.startFrame))
#    print("Stop Frame: " + str(reach.stopFrame))
#    video.set(1,reach.startFrame)
#    for frame in range(reach.startFrame, reach.stopFrame):
#        ret, frame = video.read()
#        cv2.imshow(videoName, frame)
#        if cv2.waitKey(0) & 0xFF == ord('q'):
#            break

# Uncomment below to view individual poses
#for pose in poseAnalysis:
#    for event in pose:
#        print("Event: " + event.eventType)
#        print("Start Frame: " + str(event.startFrame))
#        print("Stop Frame:" + str(event.stopFrame))
#        print("\n")
#        video.set(1,event.startFrame)
#        for frame in range(event.startFrame, event.stopFrame):
#            ret, frame = video.read()
#            cv2.imshow(videoName, frame)
#            if cv2.waitKey(0) & 0xFF == ord('q'):
#                break
