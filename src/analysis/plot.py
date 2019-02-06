"""
    Author: Julian Pitney
    Email: JulianPitney@gmail.com
    Organization: University of Ottawa (Silasi Lab)
"""



import csv
import datetime
import time
import numpy as np
import matplotlib as mpl
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import sys




if sys.version_info[0] < 3:
    import Tkinter as tk
else:
    import tkinter as tk
import matplotlib.backends.tkagg as tkagg
from matplotlib.backends.backend_agg import FigureCanvasAgg


def draw_figure(canvas, figure, loc=(0, 0)):
    """ Draw a matplotlib figure onto a Tk canvas

    loc: location of top-left corner of figure on canvas in pixels.
    Inspired by matplotlib source: lib/matplotlib/backends/backend_tkagg.py
    """
    figure_canvas_agg = FigureCanvasAgg(figure)
    figure_canvas_agg.draw()
    figure_x, figure_y, figure_w, figure_h = figure.bbox.bounds
    figure_w, figure_h = int(figure_w), int(figure_h)
    photo = tk.PhotoImage(master=canvas, width=figure_w, height=figure_h)

    # Position: convert from top-left anchor to center anchor
    canvas.create_image(loc[0] + figure_w/2, loc[1] + figure_h/2, image=photo)

    # Unfortunately, there's no accessor for the pointer to the native renderer
    tkagg.blit(photo, figure_canvas_agg.get_renderer()._renderer, colormode=2)

    # Return a handle which contains a reference to the photo object
    # which must be kept live or else the picture disappears
    return photo





#------------------------Load Profile csv logs and preprocess them------------------------------------
# Get profile names
ANIMAL_PROFILE_DIRECTORY = "../../AnimalProfiles/"
profile_names = os.listdir(ANIMAL_PROFILE_DIRECTORY)


# Generate paths to each profile's csv log file
log_paths = []
for profile in profile_names:
	path_temp = ANIMAL_PROFILE_DIRECTORY + str(profile) +"/Logs/" + str(profile) +"_session_history.csv"
	log_paths.append(path_temp)


# Load each csv log file into matrix
logs = list()
for path in log_paths:

	try:
		reader = csv.reader(open(path, "r"), delimiter=",")
	except IOError:
		# No csv log found for current profile
		continue

	x = list(reader)
	result = np.array(x).astype("str")
	logs.append(result)


# Initialize matrices for storing datetime values for each profile
profile_datetimes = list()
for log in logs:

	datetimes_temp = np.zeros(shape=(len(log), 2), dtype='datetime64[s]')
	profile_datetimes.append(datetimes_temp)


# Convert the timestamps from each csv log into datetimes
indexes = []
for i in range(len(logs)):

	log_indexes = []

	for row in range (len(profile_datetimes[i])):



		timestamp1 = time.mktime(datetime.datetime.strptime(logs[i][row][6]+"-" + logs[i][row][7], "%d-%b-%Y-%H:%M:%S").timetuple())
		timestamp2 = time.mktime(datetime.datetime.strptime(logs[i][row][8]+"-" + logs[i][row][9], "%d-%b-%Y-%H:%M:%S").timetuple())


		timestamp1 = datetime.datetime.fromtimestamp(timestamp1)
		timestamp2 = datetime.datetime.fromtimestamp(timestamp2)
		profile_datetimes[i][row][0] = timestamp1
		profile_datetimes[i][row][1] = timestamp2
		log_indexes.append(row)

	indexes.append(log_indexes)
	log_indexes = []


# Get duration of each session
profile_session_durations = []
for profile in profile_datetimes:

	temp_timedeltas = []

	for row in profile:
		temp_timedeltas.append(row[1] - row[0])

	profile_session_durations.append(temp_timedeltas)
	temp_timedeltas = []



#------------------------------------------------------------------------------------------------------




# Load trial numbers into y axis and session start time stamps into x axis
profile_y_vals = []
profile_x_vals = []
for i in range(len(logs)):

	y_temp = []
	x_temp = []

	for x in range(len(logs[i])):
		
		# Temp block for filtering out bad data from when serial wasn't working properly.
		# Remove this if/else once we stop using old corrupted log files for graph testing
		if(logs[i][x][3] == 'GETPEL'):
			y_temp.append(0)
		else:
			y_temp.append(int(logs[i][x][3]))

		x_temp.append(profile_datetimes[i][x][0])

	profile_y_vals.append(y_temp)
	profile_x_vals.append(x_temp)
	y_temp = []
	x_temp = []

# Load session durations into y axis and session start time stamps into x axis
profile_session_durations = profile_session_durations
profile_x_vals = profile_x_vals



# Assign line styles and legend information to each profile
color_codes = ['b','g','r','c','m','k']
line_styles = ['bo','go','ro','co','mo','ko']
legend_patches = []
for i in range(len(logs)):

	color_code_temp = color_codes[i]
	legend_patch_temp = mpatches.Patch(color=color_code_temp, label=str(logs[i][0][1]))
	legend_patches.append(legend_patch_temp)






# Configure plot
plt.style.use('ggplot')

# First graph (trial count vs session start time)
fig, ax = plt.subplots(figsize=(20,10))
fig.autofmt_xdate(rotation=45, ha='center')
ax.xaxis.set_major_locator(mdates.HourLocator(interval=12))
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %Hh'))
ax.set_ylabel('Trials', labelpad=10, fontsize=24)
ax.set_xlabel('Session Start Time', labelpad=10, fontsize=24)
ax.set_title('Mouse Sessions', fontsize=24)
plt.legend(handles=legend_patches)
# Second graph (session duration vs session start time)
fig2, ax2 = plt.subplots(figsize=(50,100))
fig2.autofmt_xdate(rotation=45, ha='center')
ax2.xaxis.set_major_locator(mdates.HourLocator(interval=12))
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %Hh'))
ax2.set_ylabel('Session Duration (s)', labelpad=10, fontsize=24)
ax2.set_xlabel('Session Start Time', labelpad=10, fontsize=24)
ax2.set_title('Mouse Sessions', fontsize=24)
plt.legend(handles=legend_patches)



# Plot information for first 6 profiles
# This is necessary since 1. We'll run out of color codes for lines after 6 and fine
# because we won't have more than 6 animals in a cage.

for i in range(len(logs)):

	current_x = []
	current_y = []

	for x in range(len(indexes[i])):

		current_x.append(profile_x_vals[i][indexes[i][x]])
		current_y.append(profile_y_vals[i][indexes[i][x]])
	ax.plot(current_x,current_y, line_styles[i])
	current_x = []
	current_y = []



for i in range(len(logs)):

	current_x = []
	current_y = []

	for x in range(len(indexes[i])):

		current_x.append(profile_x_vals[i][indexes[i][x]])
		current_y.append(profile_session_durations[i][indexes[i][x]])
			
	ax2.plot(current_x,current_y, line_styles[i])
	current_x = []
	current_y = []


plt.pause(100000000)


#TODO: Tk embedding stuff...maybe implement later on if we want a full dashboard
# Create a canvas
#w, h = 1920, 1080
#window = tk.Tk()
#window.title("A figure in a canvas")
#canvas = tk.Canvas(window, width=w, height=h)
#canvas.pack()

# Keep this handle alive, or else...
#fig_x, fig_y = 0, 0
#fig_photo = draw_figure(canvas, fig, loc=(fig_x, fig_y))

# Let Tk take over
#tk.mainloop()

