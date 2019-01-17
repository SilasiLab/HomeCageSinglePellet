from tkinter import *
from time import sleep
import os

class GUI:

	def __init__(self, master, animalProfilePath):


		self.master = master
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
		self.mouse5_button = Button(frame1, text="Select Mouse 5", command=self.select_mouse5_button_onClick, borderwidth = 3, relief = "raised")
		self.mouse1_button.pack(side=LEFT)
		self.mouse2_button.pack(side=LEFT)
		self.mouse3_button.pack(side=LEFT)
		self.mouse4_button.pack(side=LEFT)
		self.mouse5_button.pack(side=LEFT)

		frame1.pack()

		frame2 = Frame(master)

		self.load_animal_profiles()
		dists = [0,0,0,0,0]
		armSettings = ['left','left','left','left']

		for mouse in range(1,6):
			profileIndex = self.find_profile_state_index(mouse)

			if profileIndex == -1:
				print("Mouse " + str(mouse) + " does not exist")
			else:
				dists.insert(mouse - 1,self.profileStates[profileIndex][4])
				armSettings.insert(mouse - 1, self.profileStates[profileIndex][5])



		self.mouse1_label = Label(frame2, text="Dist= " + str(dists[0]))
		self.mouse1_label.pack(padx=38,side=LEFT)
		self.mouse2_label = Label(frame2, text="Dist= "+ str(dists[1]))
		self.mouse2_label.pack(padx=38,side=LEFT)
		self.mouse3_label = Label(frame2, text="Dist= "+ str(dists[2]))
		self.mouse3_label.pack(padx=38,side=LEFT)
		self.mouse4_label = Label(frame2, text="Dist= "+ str(dists[3]))
		self.mouse4_label.pack(padx=38,side=LEFT)
		self.mouse5_label = Label(frame2, text="Dist= "+ str(dists[4]))
		self.mouse5_label.pack(padx=38,side=LEFT)

		frame2.pack()


		frameArmButton = Frame(master)
		self.armButton1 = Button(frameArmButton,text=armSettings[0], command=self.switch_arm_state_1)
		self.armButton1.pack(padx=38,side=LEFT)
		self.armButton2 = Button(frameArmButton,text=armSettings[1], command=self.switch_arm_state_2)
		self.armButton2.pack(padx=38,side=LEFT)
		self.armButton3 = Button(frameArmButton,text=armSettings[2], command=self.switch_arm_state_3)
		self.armButton3.pack(padx=38,side=LEFT)
		self.armButton4 = Button(frameArmButton,text=armSettings[3], command=self.switch_arm_state_4)
		self.armButton4.pack(padx=38,side=LEFT)
		self.armButton5 = Button(frameArmButton,text=armSettings[4], command=self.switch_arm_state_5)
		self.armButton5.pack(padx=38,side=LEFT)

		frameArmButton.pack()


		frame42 = Frame(master)
		self.label = Label(frame42, text="\nPellet Presentation Distance(mm)")
		self.label.pack()
		frame42.pack()

		frame3 = Frame(master)
		self.scale = Scale(frame3, from_=0, to=5, orient=HORIZONTAL)
		self.scale.pack()
		frame3.pack()

		frame4 = Frame(master)
		self.updateButton = Button(frame4, text="Update", fg="green", command=self.update_button_onClick, pady=6)
		self.close_button = Button(frame4, text="Shutdown", command=self.shutdown_onClick, borderwidth = 3, relief = "raised")
		self.update_label = Label(frame4, text="\n", height=3, width= 34)
		self.update_label.config(bd=2, relief="ridge")
		self.updateButton.pack()
		self.update_label.pack(side=BOTTOM)
		frame4.pack()



	def switch_arm_state_1(self):

		self.load_animal_profiles()

		profileIndex = self.find_profile_state_index(1)
		armState = self.profileStates[profileIndex][5]

		if armState == "RIGHT":
			self.profileStates[profileIndex][5] = "LEFT"
			armState = "LEFT"
		elif armState == "LEFT":
			self.profileStates[profileIndex][5] = "RIGHT"
			armState = "RIGHT"


		self.armButton1.config(text=armState)
		self.save_animal_profile(profileIndex)


	def switch_arm_state_2(self):

		self.load_animal_profiles()

		profileIndex = self.find_profile_state_index(2)
		armState = self.profileStates[profileIndex][5]

		if armState == "RIGHT":
			self.profileStates[profileIndex][5] = "LEFT"
			armState = "LEFT"
		elif armState == "LEFT":
			self.profileStates[profileIndex][5] = "RIGHT"
			armState = "RIGHT"


		self.armButton2.config(text=armState)
		self.save_animal_profile(profileIndex)


	def switch_arm_state_3(self):

		self.load_animal_profiles()

		profileIndex = self.find_profile_state_index(3)
		armState = self.profileStates[profileIndex][5]

		if armState == "RIGHT":
			self.profileStates[profileIndex][5] = "LEFT"
			armState = "LEFT"
		elif armState == "LEFT":
			self.profileStates[profileIndex][5] = "RIGHT"
			armState = "RIGHT"


		self.armButton3.config(text=armState)
		self.save_animal_profile(profileIndex)


	def switch_arm_state_4(self):

		self.load_animal_profiles()

		profileIndex = self.find_profile_state_index(4)
		armState = self.profileStates[profileIndex][5]

		if armState == "RIGHT":
			self.profileStates[profileIndex][5] = "LEFT"
			armState = "LEFT"
		elif armState == "LEFT":
			self.profileStates[profileIndex][5] = "RIGHT"
			armState = "RIGHT"


		self.armButton4.config(text=armState)
		self.save_animal_profile(profileIndex)


	def switch_arm_state_5(self):

		self.load_animal_profiles()

		profileIndex = self.find_profile_state_index(5)
		armState = self.profileStates[profileIndex][5]

		if armState == "RIGHT":
			self.profileStates[profileIndex][5] = "LEFT"
			armState = "LEFT"
		elif armState == "LEFT":
			self.profileStates[profileIndex][5] = "RIGHT"
			armState = "RIGHT"


		self.armButton5.config(text=armState)
		self.save_animal_profile(profileIndex)


	def load_animal_profiles(self):

		self.profileNames = []
		self.profileStates = []
		self.profileSaveFilePaths = []

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
		self.mouse5_button.config(relief="raised")
		self.currentMouse = 1

	def select_mouse2_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="sunken")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")
		self.mouse5_button.config(relief="raised")
		self.currentMouse = 2

	def select_mouse3_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="sunken")
		self.mouse4_button.config(relief="raised")
		self.mouse5_button.config(relief="raised")
		self.currentMouse = 3

	def select_mouse4_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="sunken")
		self.mouse5_button.config(relief="raised")
		self.currentMouse = 4

	def select_mouse5_button_onClick(self):

		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")
		self.mouse5_button.config(relief="sunken")
		self.currentMouse = 5

	def update_button_onClick(self):

		self.load_animal_profiles()

		if self.currentMouse > 0 and self.currentMouse <= 5:

			profileIndex = self.find_profile_state_index(self.currentMouse)

			if profileIndex == -1:

				print("Error: Could not find profile for Mouse " + str(self.currentMouse))
				return -1

			else:

				self.profileStates[profileIndex][4] = self.scale.get()
				self.save_animal_profile(profileIndex)
				self.update_label.config(text="Pellet presentation distance \n for Mouse " + str(self.profileStates[profileIndex][2]) + " has been updated to " + str(self.profileStates[profileIndex][4]) + "mm!")
				if self.currentMouse == 1:
					self.mouse1_label.config(text="Dist= " + str(self.profileStates[profileIndex][4]))
				elif self.currentMouse == 2:
					self.mouse2_label.config(text="Dist= " + str(self.profileStates[profileIndex][4]))
				elif self.currentMouse == 3:
					self.mouse3_label.config(text="Dist= " + str(self.profileStates[profileIndex][4]))
				elif self.currentMouse == 4:
					self.mouse4_label.config(text="Dist= " + str(self.profileStates[profileIndex][4]))
				elif self.currentMouse == 5:
					self.mouse5_label.config(text="Dist= " + str(self.profileStates[profileIndex][4]))

	def shutdown_onClick(self):
		self.master.destroy()
		exit()

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
