from tkinter import *
import PIL
from PIL import ImageTk
import cv2
import os, sys


def get_profile_list():
    return next(os.walk('../../AnimalProfiles'))[1]


def gen_profiles(profileNames):
    profiles = []
    for profileName in profileNames:
        profiles.append(AnimalProfile(profileName))

    return profiles


class AnimalProfile(object):

    def __init__(self, profileName):
        self.profileName = profileName
        self.videoList = self.get_video_list(profileName)

    def get_video_list(self, profileName):
        return next(os.walk('../../AnimalProfiles/' + profileName + "/Analyses"))


class Reach(object):

    def __init__(self, start, stop, trajectoryCoords,category):
        self.start = start
        self.stop = stop
        self.trajectoryCoords = trajectoryCoords
        self.category = category

class Application(Frame):
    currentProfile = None
    currentVideo = None
    currentReaches = []
    currentReachIndex = None
    currentFrame = None
    currentStartFrame = None
    currentStopFrame = None
    font = cv2.FONT_HERSHEY_SIMPLEX


    def __init__(self, master=None):

        Frame.__init__(self, master)

        self.cap = None
        self.defaultImg = cv2.imread('../../resources/default.png')
        self.lmain = None

        self.profileNames = get_profile_list()
        self.profiles = gen_profiles(self.profileNames)

        self.animalDropdownVar = StringVar(self)
        self.animalDropdownVar.set("Select Animal")
        self.animalDropdownVar.trace('w', self.change_animal_dropdown)
        self.videoSelectionChanged = False
        self.createWidgets()


    def saveScoring(self):
        reaches = self.currentReaches
        self.currentReaches = []

        print("saving scoring...")
        savePath = "../../AnimalProfiles/" + self.currentProfile.profileName + "/Analyses/" + self.currentVideo +"/"
        newName = self.currentVideo
        newName += "_reaches_scored.txt"
        savePath += newName


        exists = os.path.isfile(savePath)
        if exists:

            print("This video has already been scored. Not overwriting existing data.\n")

        else:

            with open(savePath, 'a') as f:

                for reach in reaches:
                    f.write(str(reach.start) + "\n")
                    f.write(str(reach.stop) + "\n")
                    f.write(str(reach.category) + "\n")
                    for line in reach.trajectoryCoords:
                        f.write(line)
                    f.write("\n\n")

            print("Scoring saved!")
        self.change_animal_dropdown()

    def s1_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_1_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_1_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_1_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def s2_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_2_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_2_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_2_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def s3_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_3_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_3_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_3_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a1_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_1_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_1_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_1_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a2_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_2_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_2_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_2_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a3_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_3_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_3_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_3_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def drop_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "DROP_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as DROP_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as DROP_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def knock_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "KNOCK_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as KNOCK_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as KNOCK_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def s_lick_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESSFUL_LICK_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESSFUL_LICK_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESSFUL_LICK_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def f_lick_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "FAILED_LICK_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as FAILED_LICK_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as FAILED_LICK_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def invalid_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "INVALID_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as INVALID_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as INVALID_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def machine_fail_left(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "MACHINE_FAIL_LEFT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as MACHINE_FAIL_LEFT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as MACHINE_FAIL_LEFT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def s1_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_1_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_1_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_1_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def s2_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_2_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_2_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_2_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def s3_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESS_3_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESS_3_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESS_3_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a1_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_1_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_1_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_1_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a2_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_2_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_2_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_2_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def a3_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "ATTEMPT_3_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as ATTEMPT_3_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as ATTEMPT_3_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def drop_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "DROP_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as DROP_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as DROP_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def knock_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "KNOCK_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as KNOCK_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as KNOCK_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def s_lick_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "SUCCESSFUL_LICK_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as SUCCESSFUL_LICK_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as SUCCESSFUL_LICK_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def f_lick_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "FAILED_LICK_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as FAILED_LICK_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as FAILED_LICK_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def invalid_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "INVALID_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as INVALID_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as INVALID_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def machine_fail_right(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "MACHINE_FAIL_RIGHT"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as MACHINE_FAIL_RIGHT")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as MACHINE_FAIL_RIGHT")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf1(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_1"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_1")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_1")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf2(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_2"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_2")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_2")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf3(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_3"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_3")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_3")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf4(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_4"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_4")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_4")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf5(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_5"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_5")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_5")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None

    def udf6(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_6"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_6")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_6")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def udf7(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_7"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_7")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_7")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def udf8(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_8"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_8")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_8")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None


    def udf9(self, event=None):

        if self.currentReachIndex == None:
            return 0

        self.currentReaches[self.currentReachIndex].category = "USER_DEFINED_9"
        if(self.currentReachIndex < len(self.currentReaches) - 1):
            self.currentReachIndex += 1
            self.currentFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStartFrame = self.currentReaches[self.currentReachIndex].start
            self.currentStopFrame = self.currentReaches[self.currentReachIndex].stop
            print("Trial marked as USER_DEFINED_9")
        elif(self.currentReachIndex >= len(self.currentReaches) - 1):
            print("Trial marked as USER_DEFINED_9")
            self.saveScoring()
            self.currentReachIndex = None
            self.currentVideo = None
            self.cap = None
            self.currentFrame = None
            self.currentStartFrame = None
            self.currentStopFrame = None




    def play_video(self, event=None):

        if self.cap == None or self.currentReachIndex == None:
            self.show_frame()
            return 0



        if self.currentFrame > self.currentStopFrame + 20 or self.currentFrame < self.currentStartFrame:
            self.currentFrame = self.currentStartFrame



        self.cap.set(cv2.CAP_PROP_POS_FRAMES, self.currentFrame)
        ret, frame = self.cap.read()
        if ret == False:
            return 0

        cv2.putText(frame, "Reach:" + str(self.currentReachIndex + 1) + "/" + str(len(self.currentReaches)), (950, 40), self.font, 1, (255, 255, 255), 1, cv2.LINE_AA)

        img = PIL.Image.fromarray(frame)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.currentFrame += 1
        self.lmain.after(1, self.play_video)

    def show_frame(self):
        img = PIL.Image.fromarray(self.defaultImg)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)


    def change_animal_dropdown(self, *args):
        self.currentProfile = self.find_animal_profile(self.animalDropdownVar.get())
        self.videoListBox.delete(0, END)

        index = 0
        for video in self.currentProfile.videoList[1]:
            self.videoListBox.insert(END, video)


            # Check if file exists indicating video has already been scored. If it has, make it green in the list.
            testPath = "../../AnimalProfiles/" + self.currentProfile.profileName + "/Analyses/" + video + "/" + video + "_reaches_scored.txt"
            exists = os.path.isfile(testPath)


            if exists:
                self.videoListBox.itemconfig(index, {'bg': 'dark sea green'})
                index += 1
                continue

            # Check if reaches.txt exists for current video. If it does not, make it PeachPuff2 in the list.
            testPath = "../../AnimalProfiles/" + self.currentProfile.profileName + "/Analyses/" + video + "/" + video + "_reaches.txt"
            exists = os.path.isfile(testPath)
            if not exists:
                self.videoListBox.itemconfig(index, {'bg': 'PeachPuff2'})
            # If it does exist, make it dark sea green.
            else:
                self.videoListBox.itemconfig(index, {'bg': 'steel blue'})

            index += 1


    def find_animal_profile(self, profileName):
        for profile in self.profiles:
            if profileName == profile.profileName:
                return profile
        return -1

    def loadVideo(self):
        selections = map(int, self.videoListBox.curselection())
        items = [self.currentProfile.videoList[1][int(item)] for item in selections]
        if (len(items) > 1 or len(items) <= 0):
            print("Warning: video drop down has <=0 or >1 selection")
            return 0
        else:
            self.currentVideo = items[0]

        self.videoPath = '../../AnimalProfiles/' + str(
            self.currentProfile.profileName) + "/Analyses/" + self.currentVideo + "/" + self.currentVideo + ".avi"
        self.cap = cv2.VideoCapture(self.videoPath)
        self.loadVideoReachData()
        self.play_video()

    def loadVideoReachData(self):

        try:
            file = open("../../AnimalProfiles/" + str(
                self.currentProfile.profileName) + "/Analyses/" + self.currentVideo + "/" + self.currentVideo + "_reaches.txt")
            # Store configuration file values
        except FileNotFoundError:
            print("No reaching data found for selected video!")
            return -1

        lines = file.readlines()
        reachesText = []
        temp = []
        lastLine = ""

        for line in lines:

            if line + lastLine == "\n\n":
                reachesText.append(temp)
                temp = []
            else:
                temp.append(line)

            lastLine = line

        reaches = []
        for text in reachesText:
            start = int(text[0])
            stop = int(text[1])
            category = str(text[2])
            trajectoryCoords = []
            for i in range(3, len(text) - 1):
                trajectoryCoords.append(text[i])

            reaches.append(Reach(start, stop, trajectoryCoords,category))

        self.currentReaches = reaches
        if(len(self.currentReaches) > 0):
            self.currentFrame = self.currentReaches[0].start
            self.currentStartFrame = self.currentReaches[0].start
            self.currentStopFrame = self.currentReaches[0].stop
            self.currentReachIndex = 0



    def createWidgets(self):

        topFrame = Frame(self.master, width=500, height=500)
        imageFrame = Frame(self.master, width=600, height=500)
        leftFrame = Frame(self.master)
        buttonFrame1 = Frame(self.master)
        buttonFrame2 = Frame(self.master)
        buttonFrame3 = Frame(self.master)

        self.quitButton = Button(topFrame, text='quit', command=self.quit)
        self.quitButton.pack(side=TOP)
        animalSelectionDropDownMenu = OptionMenu(topFrame, self.animalDropdownVar, *self.profileNames)
        animalSelectionDropDownMenu.pack()
        self.videoListBox = Listbox(topFrame,width=45,height=30)
        self.videoListBox.pack()
        self.selectAnimalButton = Button(topFrame, text='Select Video', command=self.loadVideo)
        self.selectAnimalButton.pack()

        self.lmain = Label(imageFrame)
        self.show_frame()

        self.S1_LEFT = Button(buttonFrame1, text='S_1_L (q)',command=self.s1_left)
        self.S1_LEFT.pack(side=LEFT)
        self.S2_LEFT = Button(buttonFrame1, text='S_2_L (w)',command=self.s2_left)
        self.S2_LEFT.pack(side=LEFT)
        self.S3_LEFT = Button(buttonFrame1, text='S_3_L (e)',command=self.s3_left)
        self.S3_LEFT.pack(side=LEFT)
        self.A1_LEFT = Button(buttonFrame1, text='A_1_L (r)',command=self.a1_left)
        self.A1_LEFT.pack(side=LEFT)
        self.A2_LEFT = Button(buttonFrame1, text='A_2_L (t)',command=self.a2_left)
        self.A2_LEFT.pack(side=LEFT)
        self.A3_LEFT = Button(buttonFrame1, text='A_3_L (y)',command=self.a3_left)
        self.A3_LEFT.pack(side=LEFT)
        self.DROP_LEFT = Button(buttonFrame1, text='DROP_L (u)',command=self.drop_left)
        self.DROP_LEFT.pack(side=LEFT)
        self.KNOCK_LEFT = Button(buttonFrame1, text='KNOCK_L (i)',command=self.knock_left)
        self.KNOCK_LEFT.pack(side=LEFT)
        self.S_LICK_LEFT = Button(buttonFrame1, text='S_LICK_L (o)',command=self.s_lick_left)
        self.S_LICK_LEFT.pack(side=LEFT)
        self.F_LICK_LEFT = Button(buttonFrame1, text='F_LICK_L (p)',command=self.f_lick_left)
        self.F_LICK_LEFT.pack(side=LEFT)
        self.INVALID_LEFT = Button(buttonFrame1, text='INVALID_L (a)',command=self.invalid_left)
        self.INVALID_LEFT.pack(side=LEFT)
        self.MACHINE_FAIL_LEFT = Button(buttonFrame1, text='MACHINE_FAIL_L (s)',command=self.machine_fail_left)
        self.MACHINE_FAIL_LEFT.pack(side=LEFT)


        self.S1_RIGHT = Button(buttonFrame2, text='S_1_R (d)',command=self.s1_right)
        self.S1_RIGHT.pack(side=LEFT)
        self.S2_RIGHT = Button(buttonFrame2, text='S_2_R (f)',command=self.s2_right)
        self.S2_RIGHT.pack(side=LEFT)
        self.S3_RIGHT = Button(buttonFrame2, text='S_3_R (g)',command=self.s3_right)
        self.S3_RIGHT.pack(side=LEFT)
        self.A1_RIGHT = Button(buttonFrame2, text='A_1_R (h)',command=self.a1_right)
        self.A1_RIGHT.pack(side=LEFT)
        self.A2_RIGHT = Button(buttonFrame2, text='A_2_R (j)',command=self.a2_right)
        self.A2_RIGHT.pack(side=LEFT)
        self.A3_RIGHT = Button(buttonFrame2, text='A_3_R (k)',command=self.a3_right)
        self.A3_RIGHT.pack(side=LEFT)
        self.DROP_RIGHT = Button(buttonFrame2, text='DROP_R (l)',command=self.drop_right)
        self.DROP_RIGHT.pack(side=LEFT)
        self.KNOCK_RIGHT = Button(buttonFrame2, text='KNOCK_R (z)',command=self.knock_right)
        self.KNOCK_RIGHT.pack(side=LEFT)
        self.S_LICK_RIGHT = Button(buttonFrame2, text='S_LICK_R (x)',command=self.s_lick_right)
        self.S_LICK_RIGHT.pack(side=LEFT)
        self.F_LICK_RIGHT = Button(buttonFrame2, text='F_LICK_R (c)',command=self.f_lick_right)
        self.F_LICK_RIGHT.pack(side=LEFT)
        self.INVALID_RIGHT = Button(buttonFrame2, text='INVALID_R (v)',command=self.invalid_right)
        self.INVALID_RIGHT.pack(side=LEFT)
        self.MACHINE_FAIL_RIGHT = Button(buttonFrame2, text='MACHINE_FAIL_R (b)',command=self.machine_fail_right)
        self.MACHINE_FAIL_RIGHT.pack(side=LEFT)


        self.UDF1 = Button(buttonFrame3, text="USER_DEF_1 (1)",command=self.udf1)
        self.UDF1.pack(side=LEFT)
        self.UDF2 = Button(buttonFrame3, text="USER_DEF_2 (2)",command=self.udf2)
        self.UDF2.pack(side=LEFT)
        self.UDF3 = Button(buttonFrame3, text="USER_DEF_3 (3)",command=self.udf3)
        self.UDF3.pack(side=LEFT)
        self.UDF4 = Button(buttonFrame3, text="USER_DEF_4 (4)",command=self.udf4)
        self.UDF4.pack(side=LEFT)
        self.UDF5 = Button(buttonFrame3, text="USER_DEF_5 (5)",command=self.udf5)
        self.UDF5.pack(side=LEFT)
        self.UDF6 = Button(buttonFrame3, text="USER_DEF_6 (6)",command=self.udf6)
        self.UDF6.pack(side=LEFT)
        self.UDF7 = Button(buttonFrame3, text="USER_DEF_7 (7)",command=self.udf7)
        self.UDF7.pack(side=LEFT)
        self.UDF8 = Button(buttonFrame3, text="USER_DEF_8 (8)",command=self.udf8)
        self.UDF8.pack(side=LEFT)
        self.UDF9 = Button(buttonFrame3, text="USER_DEF_9 (9)",command=self.udf9)
        self.UDF9.pack(side=LEFT)



        topFrame.pack(side=LEFT)
        imageFrame.pack()
        self.lmain.pack()
        leftFrame.pack(side=LEFT)
        buttonFrame1.pack()
        buttonFrame2.pack()
        buttonFrame3.pack()
        self.pack()






app = Application()
app.master.title('HCSP Scoring Interface')
app.master.bind('q',app.s1_left)
app.master.bind('w',app.s2_left)
app.master.bind('e',app.s3_left)
app.master.bind('r',app.a1_left)
app.master.bind('t',app.a2_left)
app.master.bind('y',app.a3_left)
app.master.bind('u',app.drop_left)
app.master.bind('i',app.knock_left)
app.master.bind('o',app.s_lick_left)
app.master.bind('p',app.f_lick_left)
app.master.bind('a',app.invalid_left)
app.master.bind('s',app.machine_fail_left)

app.master.bind('d',app.s1_right)
app.master.bind('f',app.s2_right)
app.master.bind('g',app.s3_right)
app.master.bind('h',app.a1_right)
app.master.bind('j',app.a2_right)
app.master.bind('k',app.a3_right)
app.master.bind('l',app.drop_right)
app.master.bind('z',app.knock_right)
app.master.bind('x',app.s_lick_right)
app.master.bind('c',app.f_lick_right)
app.master.bind('v',app.invalid_right)
app.master.bind('b',app.machine_fail_right)

app.master.bind('1',app.udf1)
app.master.bind('2',app.udf2)
app.master.bind('3',app.udf3)
app.master.bind('4',app.udf4)
app.master.bind('5',app.udf5)
app.master.bind('6',app.udf6)
app.master.bind('7',app.udf7)
app.master.bind('8',app.udf8)
app.master.bind('9',app.udf9)

app.mainloop()
