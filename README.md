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
2. Install Anaconda.
3. Install the Flir Spinnaker SDK v1.10.31.
4. Install Arduino IDE v1.8.5.
5. Install OpenCV for C++.
	- `sudo apt-get install build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev`
	- `sudo apt-get install libjpeg-dev libpng-dev libtiff5-dev libjasper-dev libdc1394-22-dev libeigen3-dev libtheora-dev 			libvorbis-dev libxvidcore-dev libx264-dev sphinx-common libtbb-dev yasm libfaac-dev libopencore-amrnb-dev 			libopencore-amrwb-dev libopenexr-dev libgstreamer-plugins-base1.0-dev libavutil-dev libavfilter-dev 				libavresample-dev`
	- `suso -s`
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
	
	
**Assembly:**

Assembly is complex and is therefore detailed in HomeCageSinglePellet/Assembly.txt



**Usage**:

1. Enter the virtual environment that the system was installed in (e.g `source activate <my_env>`).

2. Enter HomeCageSinglePellet/src/client/ and run `python -B genProfiles.py`. The terminal 
	will walk you through entering your new animals into the system.

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

**VIDEO_DIRECTORY** = Full path to directory containing videos you want to analyze.

**NETWORK_NAME** = Full name of DLC2 network you want to use to analyze videos.




**Troubleshooting**:

* Is everything plugged in?
* Shutting the system down incorrectly will often cause the camera and camera software to enter a bad state.
	* Check if the light on the camera is solid green. If it is, unplug the camera and plug it back in.
	* Check the HomeCageSinglePellet/src/client/ directory for a file named KILL. If this file exists, delete it.
	* Make sure the camera is plugged into a USB 3.0 or greater port and that it is not sharing a USB bridge with too many 			other devices (I.e if you have 43 devices plugged into the back of the computer and none in the front, plug the 		camera into the front).
* Make sure you are in the correct virtual environment.
* Make sure the HomeCageSinglePellet/config/config.txt file contains the correct configuration. (If the file gets deleted it will be replaced by a default version at system start)
* Make sure there are 1 to 5 profiles in the HomeCageSinglePellet/AnimalProfiles/ directory. Ensure these profiles contain all 		the appropriate files and that the save.txt file for each animal contains the correct information. 


