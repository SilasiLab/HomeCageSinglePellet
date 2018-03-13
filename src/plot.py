import csv
import datetime
import time
import numpy as np
import matplotlib
import matplotlib.dates as mdates
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
import os
import sys


"""
	BEWARE: This script was written quickly with little thought. Dependency hell below. Changing 1 thing may break something
	else that is seemingly unrelated. Editing not reccomended.
"""

#------------------------Load Profile csv logs and preprocess them------------------------------------
# Get profile names
profile_names = os.listdir("/media/pi/GS 2TB/AnimalProfiles/")

# Generate paths to each profile's csv log file
log_paths = []
for profile in profile_names:
	path_temp = "/media/pi/GS 2TB/AnimalProfiles/" + str(profile) +"/Logs/" + str(profile) +"_session_history.csv"
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


	# Filter out test tag log files
	if result[0][1][0:8] == "Test Tag":
		continue
	else:
		logs.append(result)





# Initialize matrices for storing datetime values for each profile
profile_datetimes = list()
for log in logs:

	datetimes_temp = np.zeros(shape=(len(log), 2), dtype='datetime64[s]')
	profile_datetimes.append(datetimes_temp)

current_time = time.time()

time_thing = 0
other_time_thing = 0

while True:

	print("[1] Graph n Days")
	print("[2] Graph n Hours")
	menu = int(input("Input: "))


	if menu == 1:

		other_time_thing = int(input("How many days would you like to graph?: "))
		day_s = 86400
		time_thing = day_s
		break

	elif menu == 2:

		other_time_thing = int(input("How many hours would you like to graph?: "))
		hour_s = 3600
		time_thing = hour_s
		break

	else:
		print("Invalid menu choice, please try again.")


indexes = []

# Convert the timestamps from each csv log into datetimes
for i in range(len(logs)):

	log_indexes = []

	for row in range (len(profile_datetimes[i])):



		timestamp1 = float(logs[i][row][4])
		timestamp2 = float(logs[i][row][5])

		if timestamp1 < (current_time - time_thing*other_time_thing):
			continue
		else:
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

		y_temp.append(int(logs[i][x][3]))
		x_temp.append(profile_datetimes[i][x][0])

	profile_y_vals.append(y_temp)
	profile_x_vals.append(x_temp)
	y_temp = []
	x_temp = []

# Load session durations into y axis and session start time stamps into x axis
# y = profile_session_durations
# x = profile_x_vals



# Assign line styles and legend information to each profile
color_codes = ['b','g','r','c','m','k']
line_styles = ['bo','go','ro','co','mo','ko']
legend_patches = []
for i in range(len(logs)):

	color_code_temp = color_codes[i]
	legend_patch_temp = mpatches.Patch(color=color_code_temp, label=str(logs[i][0][1]))
	legend_patches.append(legend_patch_temp)






# Configure plot
plt.ion()
plt.style.use('ggplot')

# First graph (trial count vs session start time)
fig, ax = plt.subplots(figsize=(50,100))
fig.autofmt_xdate(rotation=45, ha='center')
ax.xaxis.set_major_locator(mdates.HourLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
ax.set_ylabel('Trials', labelpad=30, fontsize=24)
ax.set_xlabel('Session Start Time', labelpad=30, fontsize=24)
ax.set_title('Mouse Sessions', fontsize=24)
plt.legend(handles=legend_patches)
# Second graph (session duration vs session start time)
fig2, ax2 = plt.subplots(figsize=(50,100))
fig2.autofmt_xdate(rotation=45, ha='center')
ax2.xaxis.set_major_locator(mdates.HourLocator())
ax2.xaxis.set_major_formatter(mdates.DateFormatter('%b-%d %H:%M'))
ax2.set_ylabel('Session Duration (s)', labelpad=30, fontsize=24)
ax2.set_xlabel('Session Start Time', labelpad=30, fontsize=24)
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

plt.pause(10000)
