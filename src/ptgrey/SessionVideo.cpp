/*
    Author: Julian Pitney
    Email: JulianPitney@gmail.com
    Organization: University of Ottawa (Silasi Lab)
*/



#include "Spinnaker.h"
#include "SpinGenApi/SpinnakerGenApi.h"
#include "AVIRecorder.h"
#include <iostream>
#include <unistd.h>
#include <sstream>
#include <sys/stat.h>
#include <string>
#include <pthread.h>
#include <iostream>
#include <fstream>
#include <opencv2/highgui.hpp>
#include <opencv2/core.hpp>
#include <opencv2/imgcodecs.hpp>
#include <stdlib.h>
#include <chrono>

using namespace Spinnaker;
using namespace Spinnaker::GenApi;
using namespace Spinnaker::GenICam;
using namespace std;
using namespace std::chrono;
using namespace cv;


/*

This program captures video from a Flir Blackfly S camera (It may work with other cameras
that use the Spinnaker API).
Note: Most of this code is chopped up bits from the official Spinnaker SDK examples.
	Read those examples for the best available documentation.


Input Args:

	WIDTH = width of frames that will be captured
	HEIGHT = height of frmaes that will be captured
	OFFSET_X = x_offset of frame from top left corner of camera sensor
	OFFSET_Y = y_offset of frame from top left corner of camera sensor
	FPS = Acquisition FPS camera will be set to (careful: If your machine can't keep up with this fps you won't get an error, your videos will just look sped up)
	EXPOSURE = integer representing exposure time in microseconds
	BITRATE = integer representing bitrate
	PREVIEW_WINDOW = integer flag for turning preview window on or off (Note the preview window will significantly lower your max fps)

Note: In the HomeCage system, these args are supplied by the python client when it spawns this process for recording.


Compiling:

	Compile the same way the Spinnaker SDK examples are compiled.

	1. Run Spinnaker SDK installer for version specified in HomeCageSinglePellet/INSTALL.txt
	2. Install OpenCV 3.4.x for C++
	3. Modify the Makefile supplied with this cpp file to point to wherever you installed OpenCV
	4. Move this source file and the Makefile to /usr/src/spinnaker/src/SessionVideo/ (Create SessionVideo yourself)
	5. run make


Note: This program will print the actual recording time and the expected recording time.
	Expected recording time is based on requested fps and number of frames captured.
	(100 frames at 10 fps expects to take 10 seconds to capture). Actual recording time is
	measured using std::chrono. If actual and expected times differ, you're not getting the
	fps you requested.

Note: The AcquireImages() function captures until it detects the existence of a file called KILL in the working
	directory that this program is running from. In the HomeCage system this file is created and deleted by the python client.
	Obviously, this is terrible way to handle IPC. Socket communication was in the works but never got finished.

Note: The block in AcquireImages that displays spinnaker frames to an OpenCV window is explained in detail
	on github under SilasiLab/Spinnaker-Utilities/ in the file displaySpinnakerFramesOpenCV.cpp

*/





const int ns_per_second = 1000000000;
int WIDTH = 1220;
int HEIGHT = 500;
int OFFSET_X = 128;
int OFFSET_Y = 520;
int FPS = 160;
int EXPOSURE = 200;
int BITRATE = 8000000;
bool PREVIEW_WINDOW = false;

int FRAMES_RECORDED = 0;
int TARGET_ACQUISITION_DURATION = 0;
int ACTUAL_ACQUISITION_DURATION = 0;

int pelletClassifierFrameInterval = 100;



enum aviType
{
	UNCOMPRESSED,
	MJPG,
	H264
};

const aviType chosenAviType = H264;


enum triggerType
{
	SOFTWARE,
	HARDWARE
};

const triggerType chosenTrigger = HARDWARE;




int initCameras(CameraList camList) {

	CameraPtr pCam = NULL;

	for (int i = 0; i < camList.GetSize(); i++)
	{
		// Select camera
		pCam = camList.GetByIndex(i);
		cout << "Initializing camera" + i << endl;
		// Initialize camera
		pCam->Init();
	}

}

int deinitCameras(CameraList camList) {

	CameraPtr pCam = NULL;

	for (int i = 0; i < camList.GetSize(); i++)
	{
		// Select camera
		pCam = camList.GetByIndex(i);
		cout << "Deinitializing camera" + i << endl;
		// Deinitialize camera
		pCam->DeInit();
	}
}

inline bool file_exists (const std::string& name) {
  struct stat buffer;
  return (stat (name.c_str(), &buffer) == 0);
}


// This function configures the camera to use a trigger. First, trigger mode is
// set to off in order to select the trigger source. Once the trigger source
// has been selected, trigger mode is then enabled, which has the camera
// capture only a single image upon the execution of the chosen trigger.
int ConfigureTrigger(INodeMap & nodeMap) {

	int result = 0;

	cout << endl << endl << "*** CONFIGURING TRIGGER ***" << endl << endl;

	if (chosenTrigger == SOFTWARE)
	{
		cout << "Software trigger chosen..." << endl;
	}
	else if (chosenTrigger == HARDWARE)
	{
		cout << "Hardware trigger chosen..." << endl;
	}

	try
	{
		//
		// Ensure trigger mode off
		//
		// *** NOTES ***
		// The trigger must be disabled in order to configure whether the source
		// is software or hardware.
		//
		CEnumerationPtr ptrTriggerMode = nodeMap.GetNode("TriggerMode");
		if (!IsAvailable(ptrTriggerMode) || !IsReadable(ptrTriggerMode))
		{
			cout << "Unable to disable trigger mode (node retrieval). Aborting..." << endl;
			return -1;
		}

		CEnumEntryPtr ptrTriggerModeOff = ptrTriggerMode->GetEntryByName("Off");
		if (!IsAvailable(ptrTriggerModeOff) || !IsReadable(ptrTriggerModeOff))
		{
			cout << "Unable to disable trigger mode (enum entry retrieval). Aborting..." << endl;
			return -1;
		}

		ptrTriggerMode->SetIntValue(ptrTriggerModeOff->GetValue());

		CEnumerationPtr triggerSelector = nodeMap.GetNode("TriggerSelector");
		triggerSelector->SetIntValue(triggerSelector->GetEntryByName("AcquisitionStart")->GetValue());

		cout << "Trigger mode disabled..." << endl;

		//
		// Select trigger source
		//
		// *** NOTES ***
		// The trigger source must be set to hardware or software while trigger
		// mode is off.
		//
		CEnumerationPtr ptrTriggerSource = nodeMap.GetNode("TriggerSource");
		if (!IsAvailable(ptrTriggerSource) || !IsWritable(ptrTriggerSource))
		{
			cout << "Unable to set trigger mode (node retrieval). Aborting..." << endl;
			return -1;
		}

		if (chosenTrigger == SOFTWARE)
		{
			// Set trigger mode to software
			CEnumEntryPtr ptrTriggerSourceSoftware = ptrTriggerSource->GetEntryByName("Software");
			if (!IsAvailable(ptrTriggerSourceSoftware) || !IsReadable(ptrTriggerSourceSoftware))
			{
				cout << "Unable to set trigger mode (enum entry retrieval). Aborting..." << endl;
				return -1;
			}

			ptrTriggerSource->SetIntValue(ptrTriggerSourceSoftware->GetValue());

			cout << "Trigger source set to software..." << endl;
		}
		else if (chosenTrigger == HARDWARE)
		{
			// Set trigger mode to hardware ('Line0')
			CEnumEntryPtr ptrTriggerSourceHardware = ptrTriggerSource->GetEntryByName("Line0");
			if (!IsAvailable(ptrTriggerSourceHardware) || !IsReadable(ptrTriggerSourceHardware))
			{
				cout << "Unable to set trigger mode (enum entry retrieval). Aborting..." << endl;
				return -1;
			}

			ptrTriggerSource->SetIntValue(ptrTriggerSourceHardware->GetValue());

			cout << "Trigger source set to hardware..." << endl;
		}

		//
		// Turn trigger mode on
		//
		// *** LATER ***
		// Once the appropriate trigger source has been set, turn trigger mode
		// on in order to retrieve images using the trigger.
		//

		CEnumEntryPtr ptrTriggerModeOn = ptrTriggerMode->GetEntryByName("On");
		if (!IsAvailable(ptrTriggerModeOn) || !IsReadable(ptrTriggerModeOn))
		{
			cout << "Unable to enable trigger mode (enum entry retrieval). Aborting..." << endl;
			return -1;
		}

		ptrTriggerMode->SetIntValue(ptrTriggerModeOn->GetValue());
		// TODO: Blackfly and Flea3 GEV cameras need 1 second delay after trigger mode is turned on
		//unsigned int microseconds = 2000000;
		//usleep(microseconds);

		CEnumerationPtr triggerActivation = nodeMap.GetNode("TriggerActivation");
		triggerActivation->SetIntValue(triggerActivation->GetEntryByName("LevelHigh")->GetValue());


		cout << "Trigger mode turned back on..." << endl << endl;
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
		result = -1;
	}

	return result;



}


// This function returns the camera to a normal state by turning off trigger
// mode.
int ResetTrigger(INodeMap & nodeMap)
{
	int result = 0;

	try
	{
		//
		// Turn trigger mode back off
		//
		// *** NOTES ***
		// Once all images have been captured, turn trigger mode back off to
		// restore the camera to a clean state.
		//
		CEnumerationPtr ptrTriggerMode = nodeMap.GetNode("TriggerMode");
		if (!IsAvailable(ptrTriggerMode) || !IsReadable(ptrTriggerMode))
		{
			cout << "Unable to disable trigger mode (node retrieval). Non-fatal error..." << endl;
			return -1;
		}

		CEnumEntryPtr ptrTriggerModeOff = ptrTriggerMode->GetEntryByName("Off");
		if (!IsAvailable(ptrTriggerModeOff) || !IsReadable(ptrTriggerModeOff))
		{
			cout << "Unable to disable trigger mode (enum entry retrieval). Non-fatal error..." << endl;
			return -1;
		}

		ptrTriggerMode->SetIntValue(ptrTriggerModeOff->GetValue());

		cout << "Trigger mode disabled..." << endl << endl;
	}
	catch (Spinnaker::Exception &e)
	{
		cout << "Error: " << e.what() << endl;
		result = -1;
	}

	return result;
}


int AcquireImages(CameraPtr pCam, INodeMap &nodeMap, INodeMap &nodeMapTLDevice, char *vidPath) {

int result = 0;

cout << endl << "*** IMAGE ACQUISITION ***" << endl << endl;

pCam->Height.SetValue(HEIGHT);
pCam->Width.SetValue(WIDTH);
pCam->OffsetX.SetValue(OFFSET_X);
pCam->OffsetY.SetValue(OFFSET_Y);

CEnumerationPtr exposureAuto = nodeMap.GetNode("ExposureAuto");
exposureAuto->SetIntValue(exposureAuto->GetEntryByName("Off")->GetValue());
CEnumerationPtr exposureMode = nodeMap.GetNode("ExposureMode");
exposureMode->SetIntValue(exposureMode->GetEntryByName("Timed")->GetValue());
CFloatPtr exposureTime = nodeMap.GetNode("ExposureTime");
exposureTime->SetValue(EXPOSURE);
pCam->AcquisitionFrameRateEnable.SetValue(true);
pCam->AcquisitionFrameRate.SetValue(float(FPS));



// Retrieve device serial number for filename
		string deviceSerialNumber = "";

		CStringPtr ptrStringSerial = nodeMapTLDevice.GetNode("DeviceSerialNumber");
		if (IsAvailable(ptrStringSerial) && IsReadable(ptrStringSerial))
		{
			deviceSerialNumber = ptrStringSerial->GetValue();

			cout << "Device serial number retrieved as " << deviceSerialNumber << "..." << endl;
		}

		//
		// Get the current frame rate; acquisition frame rate recorded in hertz
		//
		// *** NOTES ***
		// The video frame rate can be set to anything; however, in order to
		// have videos play in real-time, the acquisition frame rate can be
		// retrieved from the camera.
		//
		CFloatPtr ptrAcquisitionFrameRate = nodeMap.GetNode("AcquisitionFrameRate");
		if (!IsAvailable(ptrAcquisitionFrameRate) || !IsReadable(ptrAcquisitionFrameRate))
		{
			cout << "Unable to retrieve frame rate. Aborting..." << endl << endl;
			return -1;
		}
		float frameRateToSet = static_cast<float>(ptrAcquisitionFrameRate->GetValue());
		cout << "Frame rate to be set to " << ptrAcquisitionFrameRate->GetValue() << "...";



try
{
	// Set acquisition mode to continuous
	CEnumerationPtr ptrAcquisitionMode = nodeMap.GetNode("AcquisitionMode");
	if (!IsAvailable(ptrAcquisitionMode) || !IsWritable(ptrAcquisitionMode))
	{
		cout << "Unable to set acquisition mode to continuous (node retrieval). Aborting..." << endl << endl;
		return -1;
	}

	CEnumEntryPtr ptrAcquisitionModeContinuous = ptrAcquisitionMode->GetEntryByName("Continuous");
	if (!IsAvailable(ptrAcquisitionModeContinuous) || !IsReadable(ptrAcquisitionModeContinuous))
	{
		cout << "Unable to set acquisition mode to continuous (entry 'continuous' retrieval). Aborting..." << endl << endl;
		return -1;
	}
	int64_t acquisitionModeContinuous = ptrAcquisitionModeContinuous->GetValue();
	ptrAcquisitionMode->SetIntValue(acquisitionModeContinuous);
	cout << "Acquisition mode set to continuous..." << endl;

	//
	// Select option and open AVI filetype
	//
	// *** NOTES ***
	// Depending on the filetype, a number of settings need to be set in
	// an object called an option. An uncompressed option only needs to
	// have the video frame rate set whereas videos with MJPG or H264
	// compressions should have more values set.
	//
	// Once the desired option object is configured, open the AVI file
	// with the option in order to create the image file.
	//
	// *** LATER ***
	// Once all images have been added, it is important to close the file -
	// this is similar to many other standard file streams.
	//
	AVIRecorder aviRecorder;

	// Set maximum AVI file size to 2GB.
	// A new AVI file is generated when 2GB
	// limit is reached. Setting maximum file
	// size to 0 indicates no limit.
	const unsigned int k_aviFileSize = 2048;
	aviRecorder.SetMaximumAVISize(k_aviFileSize);

	if (chosenAviType == UNCOMPRESSED)
	{
		AVIOption option;
		option.frameRate = frameRateToSet;
		aviRecorder.AVIOpen(vidPath, option);
	}
	else if (chosenAviType == MJPG)
	{
		MJPGOption option;
		option.frameRate = frameRateToSet;
		option.quality = 75;
		cout << "Opening recorder...\n";
		aviRecorder.AVIOpen(vidPath, option);
		cout << "Done opening recorder...\n";
	}
	else if (chosenAviType == H264)
	{
		H264Option option;
		option.bitrate = BITRATE;

		option.height = static_cast<unsigned int>(HEIGHT);
		option.width = static_cast<unsigned int>(WIDTH);
		option.frameRate = frameRateToSet;
		aviRecorder.AVIOpen(vidPath, option);
	}

	// Begin acquiring images
	pCam->BeginAcquisition();

	cout << "Acquiring images..." << endl;

	// Retrieve device serial number for filename
	gcstring deviceSerialNumber("");

	CStringPtr ptrStringSerial = nodeMapTLDevice.GetNode("DeviceSerialNumber");
	if (IsAvailable(ptrStringSerial) && IsReadable(ptrStringSerial))
	{
		deviceSerialNumber = ptrStringSerial->GetValue();

		cout << "Device serial number retrieved as " << deviceSerialNumber << "..." << endl;
	}
	cout << endl;




	string pythonMsg;
    namedWindow("PtGrey Live Feed", WINDOW_AUTOSIZE);
    int n_frames = 0;
    high_resolution_clock::time_point start = high_resolution_clock::now();
    int pelletClassifierFrameCount = 0;
	while(1)
	{
        if(file_exists("KILL"))
		{
			break;
        }

		try
		{
			ImagePtr pResultImage = pCam->GetNextImage();

			if (pResultImage->IsIncomplete())
			{
				cout << "Image incomplete with image status " << pResultImage->GetImageStatus() << "..." << endl << endl;
				pResultImage->Release();
			}
			else
			{
                pelletClassifierFrameCount++;
				void* img_ptr = pResultImage->GetData();
				Mat img(HEIGHT, WIDTH, CV_8UC1, img_ptr);

                if(PREVIEW_WINDOW)
                {
				    imshow("PtGrey Live Feed", img);
		            waitKey(1);
		        }
		        else
		        {

		            if(pelletClassifierFrameCount > pelletClassifierFrameInterval)
		            {
		                imwrite("/home/sliasi/HomeCageSinglePellet/temp/pelletClassifierFatMouse.jpg", img);
		                pelletClassifierFrameCount = 0;
		            }


				    aviRecorder.AVIAppend(pResultImage);
				    pResultImage->Release();
				    n_frames++;
				    pelletClassifierFrameCount++;
				}
			}
		}
		catch (Spinnaker::Exception &e)
		{
			cout << "Error: " << e.what() << endl;
			result = -1;
		}

	}

	high_resolution_clock::time_point end = high_resolution_clock::now();
    auto duration = duration_cast<seconds>( end - start ).count();
    ACTUAL_ACQUISITION_DURATION = duration;
    TARGET_ACQUISITION_DURATION = n_frames / FPS;
    FRAMES_RECORDED = n_frames;


	// End acquisition
	pCam->EndAcquisition();
	aviRecorder.AVIClose();
}
catch (Spinnaker::Exception &e)
{
	cout << "Error: " << e.what() << endl;
	result = -1;
}

return result;

}



int main(int argc, char** argv) {

    WIDTH = atoi(argv[2]);
    HEIGHT = atoi(argv[3]);
    OFFSET_X = atoi(argv[4]);
    OFFSET_Y = atoi(argv[5]);
    FPS = atoi(argv[6]);
    EXPOSURE = atoi(argv[7]);
    BITRATE = atoi(argv[8]);
    PREVIEW_WINDOW = atoi(argv[9]);

	cout << "PTGREY BOOTING...\n";

	// Retrieve singleton reference to system object
	SystemPtr system = System::GetInstance();
	// Retrieve list of cameras from the system
	CameraList camList = system->GetCameras();

	unsigned int numCameras = camList.GetSize();
	cout << "Number of cameras detected: " << numCameras << endl << endl;
	// Finish if there are no cameras
	if (numCameras == 0)
	{
		// Clear camera list before releasing system
		camList.Clear();

		// Release system
		system->ReleaseInstance();

		cout << "Not enough cameras!" << endl;
		cout << "Done! Press Enter to exit..." << endl;
		getchar();

		return -1;
	}


	initCameras(camList);
	// Retrieve GenICam nodemap for each camera
	INodeMap & nodeMap = camList.GetByIndex(0)->GetNodeMap();
	// Retrieve TL device nodemap for each camera
	INodeMap & nodeMapTLDevice = camList.GetByIndex(0)->GetTLDeviceNodeMap();
	// Configure Trigger for each camera
	//ConfigureTrigger(nodeMap);
	// Acquire
	AcquireImages(camList.GetByIndex(0), nodeMap, nodeMapTLDevice, argv[1]);



	// Reset trigger
	ResetTrigger(nodeMap);
	// Deinitialize cameras
	deinitCameras(camList);
	// Clear camera list before releasing system
	camList.Clear();
	// Release system
	system->ReleaseInstance();

    cout << "\n\n";
    cout << "FRAMES RECORDED: " << FRAMES_RECORDED << endl;
    cout << "TARGET FPS: " << FPS << endl;
    cout << "TARGET RECORDING DURATION: " << TARGET_ACQUISITION_DURATION << endl;
    cout << "ACTUAL RECORDING DURATION: " << ACTUAL_ACQUISITION_DURATION << endl;

	return 0;
}
