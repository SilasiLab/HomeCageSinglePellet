from Tkinter import *
from time import sleep
import os

class GUI:
	
	def __init__(self, master, animalProfilePath):
		
		menubar = Menu(master)
		menubar.config(fg="red",)
		menubar.add_command(label="Quit!", command=master.quit)
		master.config(menu=menubar)	
		
		frame1 = Frame(master)
		self.mouse1_button = Button(frame1, text="Select Mouse 1", command=self.select_mouse1, borderwidth = 3, relief = "raised")
		self.mouse1_button.pack(side=LEFT)
		self.mouse2_button = Button(frame1, text="Select Mouse 2", command=self.select_mouse2, borderwidth = 3, relief = "raised")
		self.mouse2_button.pack(side=LEFT)
		self.mouse3_button = Button(frame1, text="Select Mouse 3", command=self.select_mouse3, borderwidth = 3, relief = "raised")
		self.mouse3_button.pack(side=LEFT)
		self.mouse4_button = Button(frame1, text="Select Mouse 4", command=self.select_mouse4, borderwidth = 3, relief = "raised")
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
		self.updateButton = Button(frame4, text="Update", fg="green", command=self.update, pady=6)
		self.updateButton.pack()	
		self.update_label = Label(frame4, text="\n", height=3, width= 34)
		self.update_label.pack(side=BOTTOM)
		self.update_label.config(bd=2, relief="ridge")			
		frame4.pack()
		
		
		self.animalProfilePath = animalProfilePath
		
		# Get list of profile folders
		profile_names = os.listdir(self.animalProfilePath)
		profile_save_files = []
		profile_states = []
		
		
		for profile in profile_names:

			# Build save file path and save in list
			load_file = animalProfilePath + profile + "/" + profile + "_save.txt"
			profile_save_files.append(load_file)
			
			# Open the save file
			try:
				load = open(load_file, 'r')
			except IOError:
				print "Could not open AnimalProfile save file!"

			# Read all lines from save file and strip them
			with load:
				profile_state = load.readlines()
			profile_states.append([x.strip() for x in profile_state])
			
				
		
		self.current_mouse = 0	
	
	def select_mouse1(self):
		
		self.mouse1_button.config(relief="sunken")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")
		self.current_mouse = 1

	def select_mouse2(self):					
	
		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="sunken")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="raised")	
		self.current_mouse = 2
		
	def select_mouse3(self):
		
		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="sunken")
		self.mouse4_button.config(relief="raised")
		self.current_mouse = 3
		
	def select_mouse4(self):		
		
		self.mouse1_button.config(relief="raised")
		self.mouse2_button.config(relief="raised")
		self.mouse3_button.config(relief="raised")
		self.mouse4_button.config(relief="sunken")
		self.current_mouse = 4
		
	def update(self):
		
		if self.current_mouse != 0:
			
			self.update_label.config(text="Pellet presentation distance \n for Mouse " + str(self.current_mouse) + " has been updated to " + str(self.scale.get()) + "mm!")
			



def start_gui_loop(animalProfilePath):
	
	root = Tk()
	gui = GUI(root, animalProfilePath)
	root.mainloop()
	root.destroy()

