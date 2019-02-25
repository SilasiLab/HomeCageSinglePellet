**Overview**:

This system allows the user to host up to 5 mice in their home environment and automatically administer the single pellet reaching test to those animals. The system can run unsupervised and continuously for weeks at a time, allowing all 5 mice to perform an unlimited number of single pellet trials at their leisure. 

The design allows a single mouse at a time to enter the reaching tube. Upon entry, the animal’s RFID tag will be read, and if authenticated, a session will start for that animal. A session is defined as everything that happens from the time an animal enters the reaching tube to when they leave the tube. At the start of a session, the animal’s profile will be read and the task difficulty will be automatically adjusted by moving the pellet presentation arm to the appropriate distance away from the reaching tube. After the difficulty is set, pellets will begin being presented with either the left or right presentation arm, depending on which arm is specified in the mouse’s profile. Pellets will continue to be presented periodically until the mouse leaves the tube, at which point the session will end. Video and other data is recorded for the duration of each session. At session end, all the data for the session is saved in an organized way. 





**Dependencies:**
* Ubuntu v16.04 LTS: Kernel version 4.4.19-35 or later
* Python v3.5.2
	* pySerial	
	* numpy
	* OpenCV v3.4.x
	* tkinter 
	* matplotlib
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

**Installation Steps:**
1. Install Ubuntu 16.04 LTS on your machine.
2. Install Anaconda. (https://www.anaconda.com/distribution/)
3. Install the Flir Spinnaker SDK v1.10.31 (https://www.ptgrey.com/support/downloads)
4. Install Arduino IDE v1.8.5. (https://www.arduino.cc/en/Main/Software)
5. Install OpenCV for C++.
	- `sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev`
	- `sudo apt-get install libjpeg-dev libpng-dev libtiff5-dev libjasper-dev libdc1394-22-dev libeigen3-dev libtheora-dev 			libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libtbb-dev yasm libfaac-dev libopencore-amrnb-dev 			libopencore-amrwb-dev libopenexr-dev libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev 				libavresample-dev`
	- `sudo -s`
	- `cd /opt`
	- Download OpenCV source from https://github.com/opencv/opencv/releases/tag/3.4.4 and unpack it into /opt
	- Download OpenCV_contrib source from https://github.com/opencv/opencv_contrib/releases/3.4.4 and unpack it into /opt
	- `cd opencv`
	- `mkdir release`
	- `cd release`
	- `cmake -D BUILD_TIFF=ON -D WITH_CUDA=OFF -D ENABLE_AVX=OFF -D WITH_OPENGL=OFF -D WITH_OPENCL=OFF -D WITH_IPP=OFF -D 			WITH_TBB=ON -D BUILD_TBB=ON -D WITH_EIGEN=OFF -D WITH_V4L=OFF -D WITH_VTK=OFF -D BUILD_TESTS=OFF -D 				BUILD_PERF_TESTS=OFF -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local -D 						OPENCV_EXTRA_MODULES_PATH=/opt/opencv_contrib/modules /opt/opencv/`
	- `make j4`
	- `make install`
	- `ldconfig`
	- `exit`
	- `cd`
	- `pkg-config --modversion opencv`
	- If everything worked correctly, output should read "3.4.4".
	
5. Create and configure a virtual environment for installing the HomeCageSinglePellet code.
	- `conda create -n <yourenvname> python=3.5.2 anaconda`
	- `conda activate <yourenvname>`
	- `conda install -c conda-forge opencv=3.4.4`
	- `conda install -c anaconda numpy`
	- `conda install -c anaconda pyserial`
	- `conda install -c anaconda tk`
	- `conda install -c conda-forge matplotlib`

6. Download the HCSP source code from https://github.com/SilasiLab/HomeCageSinglePellet and unpack it.
7. Optional (Only if you want to use the analysis features): Install Deeplabcut using the Anaconda based pip installation method. (https://github.com/AlexEMG/DeepLabCut/blob/master/docs/installation.md)
8. Optional (Only if you want to use the anaylsis features): Move the file `HomeCageSinglePellet/src/analysis/HCSP_analyze.py` into `~/.conda/envs/DLC2/lib/python3.6/site-packages/deeplabcut` (Where DLC2 is the name of the anaconda virtual environment where you installed Deeplabcut).
8. Done!
	
	
**Assembly:**

**Attach headers to the PCB**

1. Attach female headers for the Arduino onto the PCB.
![alt text](https://raw.githubusercontent.com/SilasiLab/HomeCageSinglePellet/master/resources/Images/STEP1-2.png)

2. Attach male headers onto the CAMTRIG, MSZ, SERVO1, SERVO2, RFID and IRBREAK holes on the PCB.

3. Solder the stepper driver to the PCB in the orientation shown in the picture. (Note that the holes on 
	the PCB are spaced too far apart for the stepper driver pins, so we've hacked together an adapter.
	(The green PCB in the picture). You'll need to address this until someone gets around to fixing the PCB layout).
	
4. Solder the capacitor across C1 as shown in the picture.

**Install the voltage regulator and power connectors**

5. Attach 6 leads to the voltage regulator.
	- 2 Leads to the positive input pad.
	- 2 leads to the negative input pad.
	- 1 lead to the positive output pad.
	- 1 lead to the negative output pad.
	
6. Short the neutral and ground leads on the circular power connectors by soldering a small wire across them.

7. Line up the voltage regulator in the box and drill holes through the box where you want to mount the regulator.

8. Screw one of the circular power connectors into the bottom hole.

9. Solder one of the negative input leads you attached to the voltage regulator in step 1 onto the negative lead of the 
	power connector you screwed in in step 4.
	
10. Solder one of the positive input leads you attached to the voltage regulator in step 1 onto the positive lead of the
	power connector you screwed in in step 4. 
	
11. Place the PCB into the box and drill holes into the box where the mount holes on the PCB line up. Then mount the 
	PCB with some bolts. Metal bolts are fine, they won't touch anything that will be a problem. Use nylon 
	washers if you're nervous.
	
12. Solder the remaining positive input power lead that you attached to the voltage regulator in step 5 to the positive
	MOTORPWR pad on the PCB.

13. Solder the remaining negative input power lead that you attached to the voltage regulator in step 5 to the negative
	MOTORPWR pad on the PCB.
	
14. Screw in the second circular power connector to the remaining hole in the box.

15. Solder a wire from the negative lead of the second power connector to the negative lead of the first power connctor.

16. Solder a wire from the positive lead of the second power connector to the positive lead of the first power connector.

**Assemble the pellet delivery system**

17. Line the hopper rail piece up on the baseplate and screw in the 4 screws that hold it in place.

18. INSERT STEPPER INSTALLATION STEP HERE

19. INSERT MICROSWITCH INSTALLATION STEP HERE

20. Slide the hopper onto the rails and slot a nut through the stepper coupler attached hole.

21. Thread the stepper coupler bolt through the hopper nut.

21. Attach both front surface mirrors to the mirror mount piece with double sided tape.

22. Slide the front-wall/mirror holder piece over the end of the acrylic tube.

23. Use your favorite adhesive to attach the IR-Breaker to the IR-Breaker holder.

24. Slide the IR-Breaker holder over the tube so that the beam runs across the bottom of the tube 
	(Where the mice feet will be).
	
25. Plug the USB adapter into your RFID sensor and hotglue it to the acrylic tube as shown. (Note:
	Push the IR-Breaker holder up against the RFID module so that it's sandwiched between
	the IR-Breaker holder and the front-wall/mirror holder, and hot glue it all in place).
	
26. Slot the assembled acrylic tube into the square hole on the rail baseplate mount as shown.

27. Line up both servos as shown in the picture.

28. Rotate the servo splines as far as they will go in the directions shown in the picture.

29. Use an allen key to insert the set screws into the tips of the hopper arms.

30. Attach the hopper arms to the servo spline as shown in the picture. (Note: This is why we rotated the servo
	spline as far as possible in step 28, so that you can set the maximum retraction point of the hopper arms 
	by attaching them how you like).
	
31. Line the servos with attached hopper arms up as shown in the picture and use your favourite adhesive to 
	adhere them to the servo mount points on the hopper.
	
 




**Usage**:

1. Enter the virtual environment that the system was installed in by typing `source activate <my_env>` into a terminal.

2. Use `cd` to navigate to HomeCageSinglePellet/src/client/ and then run `python -B genProfiles.py`. The text prompts will walk you through entering your new animals into the system.

3. Open HomeCageSinglePellet/config/config.txt and set the system configuration you want.

4. Enter HomeCageSinglePellet/src/client/ and run `python -B main.py`

5. To test that everything is running correctly, block the IR beam breaker with something
	and scan one of the system’s test tags. If a session starts properly, it’s working.

6. To shut the system down cleanly; 

	- Ensure no sessions are currently running. 
	- Press the quit button on the GUI.
	- Ctrl+c out of the program running in the terminal.



**Analysis**:

A high level analysis script is provided that runs the data for all animals through a long analysis pipeline. The functions performed on each video include;

* Analyze with Deeplabcut2.
* Identify all reaching attempts and record frame indexes where reaches occur.
* Compute 3D trajectory of reaches and estimate magnitude of movement in millimeters.
* Cut videos to remove any footage not within the bounds of a reaching event.
* Neatly package data for each analyzed video in a descriptively named folder within the animals ./Analyses/ directory.

This analysis is started by entering the HomeCageSinglePellet/src/analysis/ directory and running
`bash analyze_videos.sh <CONFIG_PATH> <VIDEO_DIRECTORY> <NETWORK_NAME>`

This script takes the following input;

**CONFIG_PATH** = Full path to config.yaml file in root directory of DLC2 project.
![alt text](https://raw.githubusercontent.com/SilasiLab/HomeCageSinglePellet/master/resources/Images/CONFIG_PATH_ANALYSIS.png)

**VIDEO_DIRECTORY** = Full path to directory containing videos you want to analyze. (e.g <~/HomeCageSinglePellet/AnimalProfiles/MOUSE1/Videos/>)

**NETWORK_NAME** = Full name of DLC2 network you want to use to analyze videos. (e.g <DeepCut_res
net50_HomeCageSinglePelletNov18shuffle1_950000>)


Another script (`HomeCageSinglePellet/src/analysis/scoreTrials.py`) is provided for manually categorizing reaches once they have been identified in the step detailed above. This script opens a GUI that allows the user to select an animal and browse through all the videos that have been analyzed for that animal. (In the video list, blue videos indicate videos where reaches were detected by the analysis software. Beige videos indicate videos where no reaches were detected. Green videos indicate videos that have already been manually scored). When users select a video from the list, the video window will display the first detected reach in a loop. It will also display the "reach count" (e.g 1/16) to indicate how many reaches the video contains and which one is currently being viewed. The user can then use the mouse or a hotkey to place the current reach into a category. The video window will then jump to the next reach. This repeats until all the reaches for a given video are scored, at which point the category information will be saved. 

**Note:** All the analysis functions read and write all their data to/from `HomeCageSinglePellet/AnimalProfiles/<animal_name>/Analyses/`. Information for each video is saved in a unique folder whose name includes video creation date, animal RFID, cage number and session number. (e.g `2019-01-25_14:36:31_002FBE737B99_67465_5233`). Each of these folders will contain the raw video, the deeplabcut output from analyzing the video (.h5 and .csv formats). In addition, if >=1 reaches were found in the video, the folder will contain a file named date_time_rfid_cage_number_session_number_reaches.txt (e.g `2019-01-25_14:36:31_002FBE737B99_67465_5233_reaches.txt`). This file contains the start and stop frame indexes of each reach in the video and (x,y,z) vectors for each reach. In addition, once a video has been scored manually using `scoreTrials.py`, a file named date_time_rfid_cage_number_session_number_reaches_scored.txt (e.g `2019-01-25_14:36:31_002FBE737B99_67465_5233_reaches_scored.txt`) will be added to the video's folder. This file is the same as date_time_rfid_cage_number_session_number_reaches.txt, except that it also contains a category identifier for every reach.


**Troubleshooting**:

* Is everything plugged in?
* Shutting the system down incorrectly will often cause the camera and camera software to enter a bad state.
	* Check if the light on the camera is solid green. If it is, unplug the camera and plug it back in.
	* Check the HomeCageSinglePellet/src/client/ directory for a file named KILL. If this file exists, delete it.
	* Make sure the camera is plugged into a USB 3.0 or greater port and that it is not sharing a USB bridge with too many 			other devices (I.e if you have 43 devices plugged into the back of the computer and none in the front, plug the 		camera into the front).
* Make sure you are in the correct virtual environment.
* Make sure the HomeCageSinglePellet/config/config.txt file contains the correct configuration. (If the file gets deleted it will be replaced by a default version at system start)
* Make sure there are 1 to 5 profiles in the HomeCageSinglePellet/AnimalProfiles/ directory. Ensure these profiles contain all 		the appropriate files and that the save.txt file for each animal contains the correct information. 


