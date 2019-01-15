from model import *
import os
from keras.preprocessing.sequence import pad_sequences
import numpy as np
from tqdm import tqdm

def getFileList(rootDir = "/home/junzheng/HomeCageSinglePellet/AnimalProfiles/MOUSE_2/Analyses"):
    dirList = os.listdir(rootDir)
    sourceList = []
    targetList = []
    for dir_1 in dirList:
        for dir_2 in os.listdir(os.path.join(rootDir, dir_1)):
            if dir_2.count('_reaches.txt')>0:
                source = os.path.join(rootDir, dir_1, dir_2)
                target = os.path.join(rootDir, dir_1, 'predict.txt')
                sourceList.append(source)
                targetList.append(target)

    return sourceList, targetList


def readData(source):
    content = []
    with open(source, 'r') as f:
        itemLines = f.readlines()
        newItemLines = []
        for item in itemLines:
            newItemLines.append(item)

        content.extend(newItemLines)
    return content

def preprocessData(content):

    X = []
    X_sample = []
    i = 0

    for line in content:

        line = line.replace('\n', '')

        listLine = line.split(',')

        if len(listLine) == 1:
            i += 1

        if i == 3:
            newx = []
            if len(listLine) != 1:
                for x in listLine:
                    newx.append(float(x))
                X_sample.append(newx)

        if i >= 5:

            X.append(X_sample)
            X_sample = []
            i = 0

    X = pad_sequences(X, maxlen=200, dtype='float32')

    X = np.asarray(X)

    return X


def predict():
    pass


def run():
    sourceList, targetList = getFileList()
    modelPath = 'models/model.h5'
    logsDir = 'history/log.csv'
    lstm = lstmModel(modelPath, logsDir)
    model = lstm.getModel()
    model.compile(loss=binary_crossentropy, optimizer='adam', metrics=['accuracy'])
    model.load_weights(lstm.model_weight_path)

    for i in tqdm(range(len(sourceList))):
        content = readData(sourceList[i])
        x = preprocessData(content)
        pred = model.predict(x, batch_size=32)
        processedPred = []
        for p in pred.tolist():
            processedPred.append(p[0])

        np.savetxt(targetList[i], processedPred)

if __name__ == '__main__':
    run()