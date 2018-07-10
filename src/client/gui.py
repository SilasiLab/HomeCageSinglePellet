from tkinter import *
from time import sleep
import os

class GUI:

	def __init__(self, master, animalProfilePath):


		self.animalProfilePath = animalProfilePath
		self.profileNames = []
		self.profileSaveFilePaths = []
		self.profileStates = []
		self.currentMouse = -1


		menubar = Menu(master)
		menubar.config(fg="red",)
		menubar.add_command(label="Quit!", command=master.quit)
		master.config(menu=menubar)

		frame1 = Frame(master)
		self.mouse1_button = Button(frame1, text="Select Mouse 1", command=self.select_mouse1_button_onClick, borderwidth = 3, relief = "raised")
		self.mouse2_button = Button(frame1, text="Select Mouse 2", command=self.select_mouse2_button_onClick, borderwidth = 3, relief = "raised")
		self.mouse3_button = Button(frame1, text="Select Mouse 3", command=self.select_mouse3_button_onClick, borderwidth = 3, relief = "raised")
		self.mouse4_button = Button(frame1, text="Select Mouse 4", command=self.select_mouse4_button_onClick, borderwidth = 3, relief = "raised")
		self.mouse1_button.pack(side=LEFT)
		self.mouse2_button.pack(side=LEFT)
		self.mouse3_button.pack(side=LEFT)
		self.mouse4_button.pack(side=LEFT)
		frame1.pack()

		frame2 = Frame(master)
		self.label = Label(frame2, text="\nPellet Presentation Distance(mm)")
		self.label.pack()
		frame2.pack()

		frame3 = Frame(master)
		self.scale = Scale(frame3, from_=0, to=10, orient=HORIZONTAL)
		self.scale.pack()
		frame3.pack()

		frame4 = Frame(master)
		self.updateButton = Button(frame4, text="Update", fg="green", command=self.update_button_onClick, pady=6)
		self.update_label = Label(frame4, text="\n", height=3, width= 34)
		self.update_label.config(bd=2, relief="ridge")
		self.updateButton.pack()
		self.update_label.pack(side=BOTTOM)
		frame4.pack()


	def load_animal_profiles(self):

		# Get list of profile folders
		self.profileNames = os.listdir(self.animalProfilePath)


		for profile in self.profileNames:

			# Build save file path and save in list
			loadFile = self.animalProfilePath + profile + "/" + profile + "_save.txt"
			self.profileSaveFilePaths.append(loadFile)

			# Open the save file
			try:
				load = open(loadFile, 'r')
			except IOError:
				print ("Could not open AnimalProfile save file!")

			# Read all lines from save file and strip them
			with load:
				profileState = load.readlines()
			self.profileStates.append([x.strip() for x in profileState])


	def save_animal_profile(self, profileIndex):

		with open(self.profileSaveFilePaths[profileIndex], 'w') as save:

			save.write(str(self.profileStates[profileIndex][0]) + "\n")
			save.write(str(self.profileStates[profileIndex][1]) + "\n")
			save.write(str(self.profileStates[profileIndex][2]) + "\n")
			save.write(str(self.profileStates[profileIndex][3]) + "\n")
			save.write(str(self.profileStates[profileIndex][4]) + "\n")
			save.write(str(self.profileStates[profileIndex][5]) + "\n")
			save.write(str(self.profileStates[profileIndex][6]) + "\n")
			save.write(str(self.profileStates[profileIndex][7]) + "\n")


	# Search for correct profileState by <mouseNumber>
	def find_profile_state_index(self, mouseNumber):

		for x in range(0,len(self.profileStates)):

			if mouseNumber == int(self.profileStates[x][2]):

				return x

		return -1


	def select_mouse1_button_onClick(self):

		self.mouse1_button.config(relief="sunken")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")
		self.currentMouse = 1

	def select_mouse2_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="sunken")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")
		self.currentMouse = 2

	def select_mouse3_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="sunken")
		self.mouse4_button.config(relief="raised")
		self.currentMouse = 3

	def select_mouse4_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="sunken")
		self.currentMouse = 4


	def update_button_onClick(self):

		if self.currentMouse > 0 and self.currentMouse <= 4:

			profileIndex = self.find_profile_state_index(self.currentMouse)

			if profileIndex == -1:

				print("Error: Could not find profile for Mouse " + str(self.currentMouse))
				return -1

			else:

				self.profileStates[profileIndex][4] = self.scale.get()
				self.save_animal_profile(profileIndex)
				self.update_label.config(text="Pellet presentation distance \n for Mouse " + str(self.profileStates[profileIndex][2]) + " has been updated to " + str(self.profileStates[profileIndex][4]) + "mm!")


# Entry point of GUI initialization. This function is outside of the GUI class
# so that it can be called by multiprocessing without having to construct a GUI
# object in the parent process first. Constructing a GUI object is expensive and
# we don't want it tying up the parent process. This is bad practice but it's easy
# so I'm leaving it for now.
def start_gui_loop(animalProfilePath):

	root = Tk()
	gui = GUI(root, animalProfilePath)
	gui.load_animal_profiles()
	root.mainloop()
	root.destroy()
