**Overview**:

This system allows the user to host up to 5 mice in their home environment and automatically administer the single pellet reaching test to those animals. The system can run unsupervised and continuously for weeks at a time, allowing all 5 mice to perform an unlimited number of single pellet trials at their leisure. 

The design allows a single mouse at a time to enter the reaching tube. Upon entry, the animal’s RFID tag will be read, and if authenticated, a session will start for that animal. A session is defined as everything that happens from the time an animal enters the reaching tube, to when they leave the tube. At the start of a session, the animal’s profile will be read and the task difficulty will be automatically adjusted by moving the pellet presentation arm to the appropriate distance from the reaching tube. After the difficulty is set, pellets will begin being presented with either the left or right presentation arm, depending on which arm is specified in the mouse’s profile. Pellets will continue to be presented periodically until the mouse leaves the tube, at which point the session will end. Video and other data is recorded for the duration of each session. At session end, all the data for the session is saved in an organized way. 

**Installation**:
Dependencies:
* Ubuntu v16.04 LTS: Kernel version 4.4.19-35 or later
* Python v3.5.2
	* pySerial	
	* numpy
	* OpenCV v3.4.x
	* tkinter 	
* Flir Spinnaker SDK v1.10.31
	* libavcodec-ffmpeg56
	* libavformat-ffmpeg56
	* libswscale-ffmpeg3
	* libswresample-ffmpeg1
	* libavutil-ffmpeg54
	* libgtkmm-2.4-dev
	* libusb-1.0-0

	Note: The Spinnaker dependencies are installed via official Spinnaker SDK install script.
* Arduino IDE v1.8.5

**Assembly:**
Assembly is complex and is therefore detailed in HomeCageSinglePellet/Assembly.txt
	
**Usage**:

1. Implant RFID tags in a group of <=5 animals. Record the RFID number of each.

2. Enter your virtual environment the HomeCage system was installed in.

3. Enter HomeCageSinglePellet/src/client/ and run `python -B genProfiles.py`. The command prompt
	will walk you through the entering your new animals into the system.

4. Open HomeCageSinglePellet/config/config.txt and set the system configuration you want.

5. Enter HomeCageSinglePellet/src/client/ and run `python -B main.py`

6. To test that everything is running correctly, block the IR beam breaker with something
	and scan one of the system’s test tags. If a session starts properly, it’s working.

7. To shut the system down cleanly; Ensure no sessions are currently running. Press the quit
	button on the GUI and then ctrl+c out of the program running in the terminal.



**Analysis**:

A high level analysis script is provided that runs the data for all animals through a long analysis pipeline. The functions performed on each video include;

Analyze with Deeplabcut2.
Identify all reaching attempts and record frame indexes where reaches occur.
Compute 3D trajectory of reaches and estimate magnitude of movement in millimeters.
Cut videos to remove any footage not within the bounds of a reaching event.
Neatly package data for each analyzed video in a descriptively named folder within the animals ./Analyses/ directory.

This analysis is start by entering the HomeCageSinglePellet/src/analysis/ directory and running
`bash analyze_videos.sh`. This script takes the following input;

**CONFIG_PATH**=Full path to config.yaml file in root directory of DLC2 project.
**VIDEO_DIRECTORY**=Full path to directory containing videos you want to analyze.
**NETWORK_NAME**=Full name of DLC2 network you want to use to analyze videos.


**Troubleshooting**:

* Is everything plugged in?
* Shutting the system down incorrectly will often cause the camera and camera software to enter a bad state.
* Check if the light on the camera is solid green. If it is, power cycle the camera to reset it.
* Check the HomeCageSinglePellet/src/client/ directory for a file named <KILL>. If this file exists, delete it.
* Make sure the camera is plugged into a USB 3.0 or greater port and that it is not sharing a USB bridge with too many other 		devices (I.e if you have 43 devices plugged into the back of the computer and none in the front, plug the camera into the front).
* Make sure you are in the correct virtual environment.
* Make sure the HomeCageSinglePellet/config/config.txt file contains the correct configuration.
* Make sure there are 1 to 5 profiles in the HomeCageSinglePellet/AnimalProfiles/ directory. Ensure these profiles contain all 		the appropriate files and that the save.txt file for each animal contains the correct information. 


