from glob import glob
import os
from time import sleep
import subprocess
from queue import Queue


KEEP_DAEMON_ALIVE=True
# List of DLC networks that should be used to analyze each video
ANALYSIS_NETWORKS = [
	'DeepCut_resnet50_eatingUpdatedAug30shuffle1_100000',
	'DeepCut_resnet50_leftReachingAug29shuffle1_100000']
ANALYSIS_POSES = [
	'eatingUpdated',
	'leftReaching']
ANALYSIS_DATES = [
	'Aug30',
	'Aug29']

VIDEO_DIRECTORY="/home/sliasi/HomeCageSinglePellet/AnimalProfiles/"
profilePaths = []


# Get path of all animal profiles and filter out test tags
for dir in glob(VIDEO_DIRECTORY+"*/"):
	if "Test" not in dir:
		profilePaths.append(dir)

# Ensure integrity of each AnimalProfile directory
for dir in profilePaths:
	if(os.path.isdir(dir+"/Analyses/")):
		print("HomeCageAnalysisDaemon: Profile="+dir+" Analyses=Found")
	else:
		print("HomeCageAnalysisDaemon: Profile="+dir+" Analyses=Not Found")
		print("HomeCageAnalysisDaemon: Creating Analyses directory...")
		try:
			os.makedirs(dir+"Analyses/")
		except OSError as e:
			if e.errno != errno.EEXIST:
				raise
		print("HomeCageAnalysisDaemon: Analyses directory created for Profile="+dir)



def refresh_analysis_queue(profilePaths):

	videos = []
	analyses = []

	for profile in profilePaths:
		tempVidList = os.listdir(profile+"Videos/")
		tempAnalysesList = os.listdir(profile+"Analyses/")
		videos.append(tempVidList)
		analyses.append(tempAnalysesList)

	return videos, analyses



while(KEEP_DAEMON_ALIVE):

	# Refresh list of videos at start of every run through list
	videos, analyses = refresh_analysis_queue(profilePaths)

	for index in range(0,len(profilePaths)):
		print("Finding video for="+profilePaths[index])
		for video in videos[index]:

			print("Checking video state for=" + video)
			# If video less than 10MB, skip analysis.
			if os.stat(profilePaths[index]+"Videos/"+video).st_size < 1048576:
				print("Video less than 10MB, skipping...")
				continue
			else:
				print("Video greater than 10MB, analyzing...")

			videoAnalyzed = False
			for networkIndex in range(0,len(ANALYSIS_NETWORKS)):
					if video[:-4]+ANALYSIS_NETWORKS[networkIndex]+".h5" in analyses[index]:
						print("Analysis found for "+video)
					else:
						# RUN ANALYSIS ON <video> using <network>
						print("running analysis on " + video)
						try:
							os.rename(profilePaths[index]+"Videos/"+video, profilePaths[index]+"temp/"+video)
						except OSError as e:
							if e.errno != errno.EEXIST:
								raise

						lines = []
						with open("myconfig_analysis.py") as f:
							lines = f.readlines()
							print(len(lines))
							lines[12] = 'videofolder = \''+profilePaths[index]+"temp/\'\n"
							lines[34] = 'Task = \''+ANALYSIS_POSES[networkIndex]+"\'\n"
							lines[35] = 'date = \''+ANALYSIS_DATES[networkIndex]+"\'\n"

						with open("myconfig_analysis.py",'w') as f:
							print(lines[12])
							print(lines[34])
							print(lines[35])
							f.writelines(lines)

						print("Starting DLC...")
						os.chdir("./Analysis-tools/")
						DLC_P = subprocess.Popen('CUDA_VISIBLE_DEVICES=0 python3 AnalyzeVideos.py', shell=True)
						print("Waiting for DLC...")
						DLC_P.wait()
						print("DLC DONE")
						sleep(3)
						os.chdir("..")
						os.remove(profilePaths[index]+"temp/"+video[:-4]+ANALYSIS_NETWORKS[networkIndex]+"includingmetadata.pickle")
						os.rename(profilePaths[index]+"temp/"+video, profilePaths[index]+"Videos/"+video)
						os.rename(profilePaths[index]+"temp/"+video[:-4]+ANALYSIS_NETWORKS[networkIndex]+".h5", profilePaths[index]+"Analyses/"+video[:-4]+ANALYSIS_NETWORKS[networkIndex]+".h5")
						videoAnalyzed = True
			if (videoAnalyzed):
				print("Starting behavior analysis...")
				behaviorAnalysisP = subprocess.Popen('python3 -B processh5.py ' + profilePaths[index] + "Analyses/ " + profilePaths[index] + "Videos/ " + video, shell=True)
				print("Waiting for behavior analysis...")
				behaviorAnalysisP.wait()
				print("Behavior analysis complete!")
				break
			print("Starting behavior analysis...")
			behaviorAnalysisP = subprocess.Popen('python3 -B processh5.py ' + profilePaths[index] + "Analyses/ " + profilePaths[index] + "Videos/ " + video, shell=True)
			print("Waiting for behavior analysis...")
			behaviorAnalysisP.wait()
print("Behavior analysis complete!")
