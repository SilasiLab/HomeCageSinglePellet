import pandas as pd
import numpy as np

class PoseEvent:

    def __init__(self, startFrame, stopFrame, eventType, data ):

        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType
        self.data = data




# Name of the video being analyzed. Hard-coded for now
# but later on this will be supplied by a queue
# that's fed with video names as videos come in.
videoName = "624-0000.avi"
# Truncate extension
videoName = videoName[:-4]
# Place the name of each model used to analyze the video in this list.
# These will be used to find the .h5 output file of each model.
modelNames = [
    "DeepCut_resnet50_eatingJuly23shuffle1_50000",
    "DeepCut_resnet50_lickingPoseJuly26shuffle1_50000",
    "DeepCut_resnet50_pelletJuly23shuffle1_50000",
    "DeepCut_resnet50_reachingJuly24shuffle1_50000"]

# Name of poses that the models were trained to detect.
# Must be in the same order as the corresponding model names
# in <modelNames>.
poseNames = [
    "eating",
    "lickingPose",
    "pellet",
    "reaching"]

likelihoodCutoffs = [
    0.99,
    0.99,
    0.99,
    0.99]

# Generate the names of each .h5 output file from each model used
# to analyze the current video.
modelH5OutputFilePaths = []
for i in range(0,len(modelNames)):
    modelH5OutputFilePaths.append("./" + poseNames[i] + "/" + videoName + modelNames[i] + ".h5")

# Read each .h5 output file into Dataframe
h5Files = []
for path in modelH5OutputFilePaths:
    h5Files.append(pd.read_hdf(path))



    #            if Dataframe[scorer][bp]['likelihood'].values[index] > pcutoff:
    #                xc = int(Dataframe[scorer][bp]['x'].values[index])
    #                yc = int(Dataframe[scorer][bp]['y'].values[index])


def extractEatingEvents(dataframe):

    contiguous = False
    contiguousCount = 0

    for row in range(0,len(dataframe.index)):
        bl = dataframe[modelNames[0]]['bottom']['likelihood'].values[row]
        ml = dataframe[modelNames[0]]['middle']['likelihood'].values[row]
        tl = dataframe[modelNames[0]]['top']['likelihood'].values[row]
        nl = dataframe[modelNames[0]]['nose']['likelihood'].values[row]

        if(bl*ml*tl*nl > likelihoodCutoffs[0]):

            print("frame#=" + str(row))
            print(str(bl) + "|" + str(ml) + "|" + str(tl) + "|" + str(nl))

def extractLickingPoseEvents(dataframe):
    return 0
def extractPelletEvents(dataframe):
    return 0
def extractReachingEvents(dataframe):
    return 0



extractEatingEvents(h5Files[0])
