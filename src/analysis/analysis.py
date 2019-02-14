"""
Walk through all the mice folders, and generate the csv files containing the analysed data.
 Written by Frank
 1/15/2019
"""
import os
import csv
from tqdm import tqdm


def readAllFiles():
    '''
    Input: Nothing, use just the relevant directory.
    This function will go through all the folders belonging to different mice, and find all the scored- output of deeplabcut
    :return:
    A list contains the directory of all the text file of scored-output of deeplabcut
    '''
    relevantDir = "../../AnimalProfiles"
    absDir = os.path.abspath(relevantDir)
    txtFileList = []
    for item in os.listdir(absDir):
        for videoDir in os.listdir(os.path.join(absDir, item, 'Analyses')):
            for txt in os.listdir(os.path.join(absDir, item, 'Analyses', videoDir)):
                if txt.count('reaches_scored.txt') > 0:
                    entireTxtDir = os.path.join(absDir, item, 'Analyses', videoDir, txt)
                    if os.path.exists(entireTxtDir):
                        txtFileList.append(entireTxtDir)
    return txtFileList

def txt2Reaches(txtFile, dict):
    '''
    This function takes the directory of txt file as input, and convert the content of it to a dictionary.
    This dictionary contains some global features and the details for each reach.
    :param txtFile: file name of a txt file, containg the scored data
    :param dict: a dict holding all the labels
    :return:
    A dictionary contains some global features and the details for each reach.
    '''
    i = 0
    none = 'Valid'
    dataList = {
                'fileName': none,
                'max_speed': none,
                'max_speed_id': none,
                'min_speed': none,
                'min_speed_id': none,
                'reaches': []
                }

    labels = []
    numReaches = 0
    pathForwardLength = 0.
    pathBackwardLength = 0.
    reachFrame = 0

    with open(txtFile, 'r') as f:
        lines = f.readlines()

    tempReach = {
            'id': none,
            'start_frame': none,
            'end_frame': none,
            'label': none,
            'max_speed': none,
            'max_speed_coordinates': none,
            'min_speed': none,
            'min_speed_coordinates': none,
            'path_length_paw_forward': none,
            'path_length_paw_backward': none,
            'reach_frame': none,
            'speed_per_moment': [],
            'path_paw': [],
            }

    for line in lines:

        line = line.replace('\n', '')

        listLine = line.split(',')

        if len(listLine) == 1:

            i += 1
            try:
                num = int(listLine[0])
            except ValueError:
                num = False
                if len(listLine[0]) > 0:
                    if listLine[0] in dict.keys():
                        tempReach['label'] = listLine[0]

            if num:
                if i == 1:
                    tempReach['id'] = numReaches
                    tempReach['start_frame'] = num
                elif i == 2:
                    tempReach['end_frame'] = num
                labels.append(num)
        if i == 3:
            if len(listLine)>1:
                if len(tempReach['path_paw']) > 0:
                    [x1, y1, z1] = [float(listLine[0]), float(listLine[1]), float(listLine[2])]
                    [x2, y2, z2] = tempReach['path_paw'][-1]
                    distance = ((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2) ** 0.5
                    if z1 - z2 > 0:
                        pathForwardLength += distance
                        reachFrame += 1
                    else:
                        pathBackwardLength += distance

                    speed = distance * 40.
                    tempReach['speed_per_moment'].append(speed)
                tempReach['path_paw'].append([float(listLine[0]), float(listLine[1]), float(listLine[2])])

        if i >= 5:
            if len(tempReach['speed_per_moment']) > 0:
                maxSpeed = max(tempReach['speed_per_moment'])
                tempReach['max_speed'] = maxSpeed
                tempReach['max_speed_coordinates'] = tempReach['speed_per_moment'].index(maxSpeed)
                minSpeed = min(tempReach['speed_per_moment'])
                tempReach['min_speed'] = minSpeed
                tempReach['min_speed_coordinates'] = tempReach['speed_per_moment'].index(minSpeed)
                tempReach['reach_frame'] = reachFrame
                tempReach['path_length_paw_forward'] = pathForwardLength
                tempReach['path_length_paw_backward'] = pathBackwardLength
                dataList['reaches'].append(tempReach)

                reachFrame = 0
                pathForwardLength = 0.
                pathBackwardLength = 0.
                labels = []
                i = 0
                tempReach = {
                    'id': none,
                    'start_frame': none,
                    'end_frame': none,
                    'label': none,
                    'max_speed': none,
                    'max_speed_coordinates': none,
                    'min_speed': none,
                    'min_speed_coordinates': none,
                    'path_length_paw_forward': none,
                    'path_length_paw_backward': none,
                    'reach_frame': none,
                    'speed_per_moment': [],
                    'path_paw': [],
                }
                numReaches += 1
    maxSpeed = 0
    minSpeed = float('inf')
    maxId = 0
    minId = 0
    for i in range(len(dataList['reaches'])):

        if dataList['reaches'][i]['max_speed'] > maxSpeed:
            maxSpeed = dataList['reaches'][i]['max_speed']
            maxId = dataList['reaches'][i]['id']

        if dataList['reaches'][i]['min_speed'] < maxSpeed:
            minSpeed = dataList['reaches'][i]['min_speed']
            minId = dataList['reaches'][i]['id']

    dataList['fileName'] = txtFile
    dataList['max_speed'] = maxSpeed
    dataList['max_speed_id'] = maxId
    dataList['min_speed'] = minSpeed
    dataList['min_speed_id'] = minId

    return dataList

def write2CSV(data, targetDir):
    '''
    This function takes the data dictionary and a target directory as input and will eventually write them into a csv file.

    :param data: the output of the function txt2Reaches
    :param targetDir: a target file name
    :return: Nothing
    '''
    f = open(targetDir, 'w')
    writer = csv.writer(f)
    for k in data.keys():
        if k != "reaches":
            line = [k]
            line.append(data[k])
            writer.writerow(line)
    line = []
    writer.writerow(line)
    reachList = data['reaches']
    for reach in reachList:
        for k in reach.keys():
            if k != 'path_paw' and k != 'speed_per_moment':
                line = [k]
                line.append(reach[k])
                writer.writerow(line)


        line = ['path_paw']
        line.extend(reach['path_paw'])
        writer.writerow(line)

        line = ['speed_per_moment']
        line.extend(reach['speed_per_moment'])
        writer.writerow(line)

        line = []
        writer.writerow(line)
    f.close()

def run(targetDir, dict):

    '''
    This is the main entrance of analysis.py
    :param targetDir: a folder to hold the output csv files
    :param dict: A dictionary contains some global features and the details for each reach.
    :return: nothing
    '''
    txtFileList = readAllFiles()

    for i in tqdm(range(len(txtFileList))):
        baseName = os.path.basename(txtFileList[i])
        baseName = baseName.replace('_reaches_scored', '').replace('txt', 'csv')
        targetFile = os.path.join(targetDir, baseName)
        data = txt2Reaches(txtFileList[i], dict)
        write2CSV(data, targetFile)

def runTest(dict):

    '''
    This is the main entrance of analysis.py
    :param targetDir: a folder to hold the output csv files
    :param dict: A dictionary contains some global features and the details for each reach.
    :return: nothing
    '''
    txtFileList = readAllFiles()

    for i in tqdm(range(len(txtFileList))):
        data = txt2Reaches(txtFileList[i], dict)
        targetFile = txtFileList[i].replace('_reaches_scored', '_analysed').replace('txt', 'csv')
        write2CSV(data, targetFile)

def runOneFile(txtFile, dict):

    '''
    Take one txt file directory and the labels dictionary as input
    And this function will generate a analysed result csv file in the same directory as the txt file.

    :param dict: A dictionary contains some global features and the details for each reach.
    :return: nothing
    '''

    data = txt2Reaches(txtFile, dict)
    targetFile = txtFile.replace('_reaches_scored', '_analysed').replace('txt', 'csv')
    write2CSV(data, targetFile)

if __name__ == '__main__':

    targetDir = "/home/junzheng/work/silasi/analyses/test"
    dict = {'Background': 0, 'Invalid Trial': 1, 'Pellet Knocked Off': 2, 'Grasp2': 3, 'Successful Grasp': 4}
    run(targetDir, dict)

