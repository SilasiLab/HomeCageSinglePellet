#!/bin/bash

CONFIG_PATH=$1
VIDEO_DIRECTORY=$2
NETWORK_NAME=$3

for video in $VIDEO_DIRECTORY*.avi
do
	echo $video
	source activate DLC2
	python /home/sliasi/.conda/envs/DLC2/lib/python3.6/site-packages/deeplabcut/HCSP_analyze.py analyze-videos $CONFIG_PATH $video 

	source activate HCSP
	videoExtensionRemoved=${video::-4}
	python kinalyze.py $video $videoExtensionRemoved$NETWORK_NAME.h5 $videoExtensionRemoved"_reaches.txt" 0 0 0 1 0 

	mv $video $VIDEO_DIRECTORY"../Temp/"
	mv $videoExtensionRemoved$NETWORK_NAME.h5 $VIDEO_DIRECTORY"../Temp/"
	mv $videoExtensionRemoved$NETWORK_NAME.csv $VIDEO_DIRECTORY"../Temp/"
	mv $videoExtensionRemoved"_reaches.txt" $VIDEO_DIRECTORY"../Temp/"
	rm $VIDEO_DIRECTORY*".pickle"

	cd $VIDEO_DIRECTORY"../Temp/"
	vidExtRmvd=""
	for vid in ./*.avi
	do
		vidExtRmvd=${vid::-4}
		mkdir ../Analyses/$vidExtRmvd
		cd ../Analyses/$vidExtRmvd
	done

	for file in ../../Temp/*
	do
		mv $file ./
	done
	cd ../../../../src/analysis/
		

done
