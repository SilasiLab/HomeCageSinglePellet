import pandas as pd
import numpy as np
import cv2
from functools import reduce

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

# Name of the video being analyzed. Hard-coded for now
# but later on this will be supplied by a queue
# that's fed with video names as videos come in.
videoName = "3998-0000.avi"
# Place the name of each model used to analyze the video in this list.
# These will be used to find the .h5 output file of each model.
modelNames = [
    "DeepCut_resnet50_eatingJuly23shuffle1_50000",
    "DeepCut_resnet50_pelletJuly23shuffle1_50000",
    "DeepCut_resnet50_reachingAug1shuffle1_50000"]

# Name of poses that the models were trained to detect.
# Must be in the same order as the corresponding model names
# in <modelNames>.
poseNames = [
    "eating",
    "pellet",
    "reaching"]

likelihoodCutoffs = [
    0.99,
    0.99,
    0.99]

minFrameCounts = [
    5,
    5,
    5]

maxFrameCounts = [
    5,
    5,
    5]

# Generate the names of each .h5 output file from each model used
# to analyze the current video.
modelH5OutputFilePaths = []
for i in range(0,len(modelNames)):
    modelH5OutputFilePaths.append("./" + poseNames[i] + "/" + videoName[:-4] + modelNames[i] + ".h5")

# Read each .h5 output file into Dataframe
h5Files = []
for path in modelH5OutputFilePaths:
    dataframe = pd.read_hdf(path)
    dataframe.to_csv(path[:-3] + ".csv")
    h5Files.append(dataframe)

    #            if Dataframe[scorer][bp]['likelihood'].values[index] > pcutoff:
    #                xc = int(Dataframe[scorer][bp]['x'].values[index])
    #                yc = int(Dataframe[scorer][bp]['y'].values[index])

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


    for row in range(0,len(dataframe.index)):
        print(row)
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

            if(contiguousNegativeCount >= 5):
                contiguousPositiveCount = 0
                contiguousNegativeCount = 0
                events.append(packageEvent(tempEventFrameRange, poseName))
                tempEventFrameRange = []
                eventStarted = False

            continue

        if(confidence >= likelihoodCutoffs[0]):

            contiguousPositiveCount += 1
            tempEventFrameRange.append(row)
        else:
            contiguousPositiveCount = 0
            tempEventFrameRange = []

        if(contiguousPositiveCount >= 5):
            eventStarted = True

    return events



def findBehaviourPattern(video, poseAnalysis):

    successfulReaches = []

    for pellet in poseAnalysis[1]:
        # Check for licking events within range of pellet event
        for reach in poseAnalysis[2]:
            # Beginning of lick detected within range of pellet event
            if reach.startFrame >= pellet.startFrame and reach.startFrame <= pellet.stopFrame + 200:
                for eating in poseAnalysis[0]:
                    if eating.startFrame >= reach.startFrame and eating.startFrame <= reach.stopFrame + 200:
                        successfulReaches.append(BehaviourEvent(pellet.startFrame, eating.stopFrame, 'Successful Reach'))
                        print("Successful Reach Found")
                    elif eating.startFrame >= reach.stopFrame + 201:
                        break
            # Lick is too far past pellet
            elif reach.startFrame >= pellet.stopFrame + 201:
                break


    return successfulReaches








video = cv2.VideoCapture(videoName)
poseAnalysis = []
poseAnalysis.append(extractEvents(0,['bottom','middle','top','nose']))
print('eatPose done')
#poseAnalysis.append(extractEvents(1,['tongue', 'leftcheek', 'rightcheek', 'forehead', 'nose']))
#print('lickPose done')
poseAnalysis.append(extractEvents(1,['left', 'right']))
print('pelletPose done')
poseAnalysis.append(extractEvents(2,['nose', 'leftcheek', 'rightcheek', 'shoulder', 'wrist', 'pawcenter', 'digit1', 'digit2', 'digit3']))
print('reachPose done')

print('Finding successful reaches...')
successfulReaches = findBehaviourPattern(video,poseAnalysis)
for reach in successfulReaches:
    print("Event: " + reach.eventType)
    print("Start frame: " + str(reach.startFrame))
    print("Stop Frame: " + str(reach.stopFrame))
    video.set(1,reach.startFrame)
    for frame in range(reach.startFrame, reach.stopFrame):
        ret, frame = video.read()
        cv2.imshow(videoName, frame)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break



for pose in poseAnalysis:
    for event in pose:
        print("Event: " + event.eventType)
        print("Start Frame: " + str(event.startFrame))
        print("Stop Frame:" + str(event.stopFrame))
        print("\n")
        video.set(1,event.startFrame)
        for frame in range(event.startFrame, event.stopFrame):
            ret, frame = video.read()
            cv2.imshow(videoName, frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break
