import csv
from datetime import datetime
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
profile_names = os.listdir("../AnimalProfiles/")

# Generate paths to each profile's csv log file
log_paths = []
for profile in profile_names:
	path_temp = "../AnimalProfiles/" + str(profile) +"/Logs/" + str(profile) +"_session_history.csv"
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



processed_logs = list()

# Convert the timestamps from each csv log into datetimes
for i in range(len(logs)):

	temp_log = list()

	for row in range (len(logs[i])):

		temp_row = list()

		timestamp1 = float(logs[i][row][4])
		timestamp2 = float(logs[i][row][5])
		datetime_UTC_1 = datetime.utcfromtimestamp(timestamp1)
		datetime_UTC_2 = datetime.utcfromtimestamp(timestamp2)

		temp_row.append(logs[i][row][0])
		temp_row.append(logs[i][row][1])
		temp_row.append(logs[i][row][2])
		temp_row.append(logs[i][row][3])
		temp_row.append(logs[i][row][6])
		temp_row.append(str(datetime_UTC_1.date()))
		temp_row.append(str(datetime_UTC_1.time()))
		temp_row.append(str(datetime_UTC_2.date()))
		temp_row.append(str(datetime_UTC_2.time()))

		temp_log.append(temp_row)


	processed_logs.append(temp_log)



for log in processed_logs:
	print("NEW LOG")
	for row in log:
		print(row)



for profile in profile_names:
	if profile[0:8] == "Test Tag":
		print("Skipping {}".format(profile))
		continue
	else:
		path_temp = "../AnimalProfiles/" + str(profile) +"/Logs/" + str(profile) +"_reformated_session_history.csv"

		with open(path_temp, 'a') as file:
			for log in processed_logs:
				if str(log[0][1]) == str(profile):
					for row in log:
						row_str = row[0] +"," + row[1] +","+row[2]+","+row[3]+","+row[4]+","+row[5] + "," + row[6] + "," + row[7] + "," + row[8] + "\n"
						file.write(row_str)
						print("line written to {}".format(profile))
