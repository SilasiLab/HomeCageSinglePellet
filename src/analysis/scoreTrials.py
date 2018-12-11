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

    def __init___(self, start, stop, trajectoryCoords):

        self.start = start
        self.stop = stop
        self.trajectoryCoords = trajectoryCoords




class Application(Frame):


    currentProfile = None
    currentVideoList = ['No videos']
    currentVideo = None

    def __init__(self, master=None):

        Frame.__init__(self, master)

        self.cap = cv2.VideoCapture('4.avi')
        self.defaultImg = cv2.imread('../../resources/default.png')
        self.lmain = None

        self.profileNames = get_profile_list()
        self.profiles = gen_profiles(self.profileNames)

        self.animalDropdownVar = StringVar(self)
        self.animalDropdownVar.set("Select Animal")
        self.animalDropdownVar.trace('w',self.change_animal_dropdown)
        self.videoSelectionChanged = False
        self.createWidgets()



    def TEMP(self):
        print("TEMP")

    def play_video(self):
        ret, frame = self.cap.read()
        if ret == False:
            return 0
        img = PIL.Image.fromarray(frame)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)
        self.lmain.after(1, self.play_video)

    def show_frame(self):
        img = PIL.Image.fromarray(self.defaultImg)
        imgtk = PIL.ImageTk.PhotoImage(image=img)
        self.lmain.imgtk = imgtk
        self.lmain.configure(image=imgtk)

    def change_animal_dropdown(self, *args):
        self.currentProfile = self.find_animal_profile(self.animalDropdownVar.get())
        self.videoListBox.delete(0, END)
        for video in self.currentProfile.videoList[1]:
            self.videoListBox.insert(END, video)


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



        self.videoPath = '../../AnimalProfiles/' + str(self.currentProfile.profileName) + "/Analyses/" + self.currentVideo + "/" + self.currentVideo + ".avi"
        print(self.videoPath)
        self.cap = cv2.VideoCapture(self.videoPath)
        self.loadVideoReachData()
        self.play_video()



    def loadVideoReachData(self):
        file = open("../../AnimalProfiles/" + str(self.currentProfile.profileName) + "/Analyses/" + self.currentVideo + "/" + self.currentVideo + "_reaches.txt")
        lines = file.readlines()
        currentVideoReaches = []
       # for line in lines:
        #    start = int(line)
         #   stop = int(line)


    def createWidgets(self):

        topFrame = Frame(self.master,width=500,height=500)
        imageFrame = Frame(self.master, width=600, height=500)
        leftFrame = Frame(self.master)
        buttonFrame = Frame(self.master)



        self.quitButton = Button(topFrame, text='quit', command=self.quit)
        self.quitButton.pack(side=TOP)
        animalSelectionDropDownMenu = OptionMenu(topFrame, self.animalDropdownVar, *self.profileNames)
        animalSelectionDropDownMenu.pack()
        self.videoListBox = Listbox(topFrame)
        self.videoListBox.pack()
        self.selectAnimalButton = Button(topFrame, text='Select Video', command=self.loadVideo)
        self.selectAnimalButton.pack()


        self.lmain = Label(imageFrame)
        self.show_frame()


        self.successButton = Button(buttonFrame, text='Successful Trial (W)',
            command=self.TEMP)
        self.successButton.pack(side=LEFT)
        self.failButton = Button(buttonFrame, text='Failed Trial (A)',
            command=self.TEMP)
        self.failButton.pack(side=LEFT)
        self.invalidButton = Button(buttonFrame, text='Invalid Trial (S)',
            command=self.TEMP)
        self.invalidButton.pack(side=LEFT)
        self.flagButton = Button(buttonFrame, text='Flag Trial (D)',
            command=self.TEMP)
        self.flagButton.pack(side=LEFT)





        topFrame.pack(side=LEFT)
        imageFrame.pack()
        self.lmain.pack()
        leftFrame.pack(side=LEFT)
        buttonFrame.pack()
        self.pack()







app = Application()
app.master.title('HCSP Scoring Interface')
app.mainloop()