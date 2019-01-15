import os
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from keras.preprocessing.sequence import pad_sequences
import shutil
from tqdm import tqdm
import copy

def findAllPairs(rootDir):
    dirList = os.listdir(rootDir)
    fileList = []
    for d in dirList:
        secondDir = os.path.join(rootDir, d)
        for dataFile in os.listdir(secondDir):
            if dataFile.count('reaches_scored.txt'):
                item = os.path.join(secondDir, dataFile)
                fileList.append(item)
    return fileList

def findAllTxtData(dir1, dir2, tarDir):
    if not os.path.exists(tarDir):
        os.mkdir(tarDir)

    dir1List = os.listdir(dir1)
    dir2List = os.listdir(dir2)

    contentList = []

    for item in tqdm(dir1List):
        entireDir = os.path.join(dir1, item)

        for txtFile in os.listdir(entireDir):
            if txtFile.count("_reaches_scored.txt") > 0:
                source = os.path.join(entireDir, txtFile)
                target = os.path.join(tarDir, txtFile)
        if len(os.listdir(entireDir)) >= 5:
            shutil.copy(source, target)
            contentList.append(os.path.basename(source))

    for item in tqdm(dir2List):
        entireDir = os.path.join(dir2, item)

        for txtFile in os.listdir(entireDir):
            if txtFile.count("_reaches_scored.txt") > 0:
                source = os.path.join(entireDir, txtFile)
                target = os.path.join(tarDir, txtFile)
        lenDir = len(os.listdir(entireDir))
        baseName = os.path.basename(source)

        if lenDir >= 4 and baseName not in contentList:
            shutil.copy(source, target)
            contentList.append(os.path.basename(source))

    print "datasize: %d"%len(contentList)

def findAllTxt(dataDir):
    dirList = os.listdir(dataDir)
    newDirList = []
    for item in dirList:
        newDirList.append(os.path.join(dataDir, item))
    return newDirList

def mergeContent(fileList):
    content = []
    for file in fileList:

        with open(file, 'r') as f:
            itemLines = f.readlines()
            newItemLines = []
            for item in itemLines:
                if len(item) > 1 and len(item) < 7:
                    item += file
                newItemLines.append(item)

            content.extend(newItemLines)

    return content


def getBalancedData(content, testSize=0.2):
    X = []
    Y = []
    X_sample = []
    traceBack = []
    i = 0
    position = 0
    success = 0
    flag = False
    traceBackItem = []
    for line in content:

        line = line.replace('\n', '')

        listLine = line.split(',')

        if len(listLine) == 1:
            i += 1
            if line != '':
                traceBackItem.append(line)
        if i == 3:
            if len(listLine) == 1:
                if listLine[0] == "Successful Grasp":
                    Y.append(1)
                    success += 1
                    flag = True
                    traceBack.append(traceBackItem)
                elif listLine[0] != "Successful Grasp" and success > 0:
                    Y.append(0)
                    success -= 1
                    flag = True
                    traceBack.append(traceBackItem)
            else:
                if flag:
                    newx = []
                    line2 = content[position]
                    line2 = line2.replace('\n', '')
                    line2 = line2.replace('\r', '')
                    line2 = line2.replace(',', ' ')
                    listLine2 = line2.split(' ')
                    for x in listLine2:
                        newx.append(float(x))
                    X_sample.append(newx)

        if i >= 5:
            if flag:
                X.append(X_sample)
            X_sample = []
            i = 0
            flag = False
            traceBackItem = []

        position += 1

    index = np.random.permutation(len(Y))

    maxLen = 0
    minX = 0
    for item in X:
        if len(item) > maxLen:
            maxLen = len(item)
            for numberList in item:
                if min(numberList)<minX:
                    minX = min(numberList)

    print "Max Length: %d, min X: %.4f"%(maxLen, minX)

    # paddingValue = minX - 1.

    X = pad_sequences(X, maxlen=200, dtype='float32', value=0)


    X = np.asarray(X).astype(np.float32)
    Y = np.asarray(Y)
    traceBack = np.asarray(traceBack, dtype=np.str)

    # minX = X.min()
    # maxX = X.max()
    # X = (X - minX) / (maxX - minX)

    X = X[index]
    Y = Y[index]
    traceBack = traceBack[index]


    trX, teX, trY, teY = train_test_split(X, Y, test_size=testSize,shuffle=False)

    trTraceback = traceBack[0: trX.shape[0]]
    teTraceback = traceBack[trX.shape[0]:]
    return trX, trY, teX, teY, trTraceback, teTraceback

def saveNpy(trX, trY, teX, teY, trTraceback, teTraceback, fileDir='data'):
    dataList = [trX, trY, teX, teY, trTraceback, teTraceback]
    nameList = ['trX', 'trY', 'teX', 'teY', 'trTraceback', 'teTraceBack']
    newNameList = []
    for name in nameList:
        newNameList.append(os.path.join(fileDir, name))

    for i in tqdm(range(len(dataList))):
        np.save(newNameList[i], dataList[i])

def loadNpy(fileDir='data'):
    nameList = ['trX', 'trY', 'teX', 'teY', 'trTraceback', 'teTraceBack']
    dataList = []
    newNameList = []
    for name in nameList:
        newNameList.append(os.path.join(fileDir, name + '.npy'))

    for i in tqdm(range(len(newNameList))):
        dataList.append(np.load(newNameList[i]))
    return dataList[0], dataList[1], dataList[2], dataList[3], dataList[4], dataList[5]

if __name__ == '__main__':

    dataDir = "data/reachingData/"
    fileList = findAllTxt(dataDir)
    content = mergeContent(fileList)
    trX, trY, teX, teY, trTraceback, teTraceback = getBalancedData(content, 0.2)
    print trX.shape
    print teX.shape

    saveNpy(trX, trY, teX, teY, trTraceback, teTraceback)
    trX, trY, teX, teY, trTraceback, teTraceback = loadNpy()
    print trX.shape
    print teX.shape

    # a = [0, 0, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 0, 1, 1, 1, 1, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 1, 1]
    # b = "0 0 0 0 1 0 1 0 1 1 0 0 1 0 0 1 0 1 0 0 0 1 1 0 0 0 1 0 0 1 0 1 1 1 1 0 0 0 0 0 1 0 0 0 1 0 0 1 1 1 1 0 0 1 1 1 0 1 1 0 0 0 0 0 1 1 1 1 1 0 0 1 0 0 0 1 1 1 0 1 1"
    # listB = b.split(' ')
    # b = []
    # for item in listB:
    #     b.append(int(item))
    #
    # true = 0
    # false = 0
    # for i in range(len(a)):
    #     if a[i] == b[i]:
    #         true += 1
    #     else:
    #         false += 1
    #
    # print "True: %d, False: %d"%(true, false)
    # print "Accuracy on validation set: %.5f"%(float(true)/float(len(a)))