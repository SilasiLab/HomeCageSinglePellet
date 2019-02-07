import cv2
import os
from keras.models import Sequential
from keras.layers import Dense, Dropout, BatchNormalization, Convolution2D, MaxPooling2D, Flatten
from keras.losses import binary_crossentropy
from keras import callbacks
from keras.callbacks import ModelCheckpoint, TensorBoard
import numpy as np
from tqdm import tqdm
from sklearn.model_selection import train_test_split
import time

def preprocess(posTxt, negTxt):
    negList = np.load(negTxt)
    posList = np.load(posTxt)
    length = min([len(negList), len(posList)])
    x = []
    y = []
    for i in tqdm(range(length)):
        item = cv2.resize(negList[i], (80, 80))
        item = np.array(item).reshape((80, 80, 1))
        x.append(item)
        y.append(0)
    for i in tqdm(range(length)):
        item = cv2.resize(posList[i], (80, 80))
        item = np.array(item).reshape((80, 80, 1))
        x.append(item)
        y.append(1)

    index = np.random.permutation(length*2)
    x = np.asarray(x, dtype=np.float32)
    y = np.asarray(y)
    x = x[index]
    y = y[index]
    return x, y



class CNN():

    def __init__(self, model_weight_path, logsDir=''):

        self.imgSize = (80, 80, 1)
        self.model = None
        self.lstmModel = None
        self.model_weight_path = model_weight_path
        self.model_weight_path_backup = model_weight_path + '.backup.h5'
        self.logsDir = logsDir
        self.inputShape = (self.imgSize[0], self.imgSize[1], self.imgSize[2])
        self.model = self.getModel()

    def getModel(self):
        if self.model:
            return self.model
        self.model = Sequential()
        self.model.add(Convolution2D(16, (3, 3), strides=(2, 2), activation='relu', padding='same', input_shape=self.inputShape))
        self.model.add(BatchNormalization())
        self.model.add(Convolution2D(16, (3, 3), strides=(2, 2), activation='relu', padding='same'))
        self.model.add(BatchNormalization())
        self.model.add(Convolution2D(16, (3, 3), strides=(1, 1), activation='relu', padding='same'))
        self.model.add(BatchNormalization())
        self.model.add(MaxPooling2D((2, 2), strides=(2, 2)))
        self.model.add(BatchNormalization())
        self.model.add(Flatten())
        self.model.add(Dropout(0.5))
        self.model.add(Dense(1, activation='sigmoid'))

        self.model.compile(loss=binary_crossentropy, optimizer='adam', metrics=['accuracy'])
        self.model.summary()
        if os.path.exists(self.model_weight_path):
            self.model.load_weights(self.model_weight_path)
        return self.model

    def train(self, trX, trY, teX, teY, batchSize=32, epoch=20):
        if not self.model:
            self.model = self.getModel()
        self.model.compile(loss=binary_crossentropy, optimizer='adam', metrics=['accuracy'])
        self.model.summary()
        if os.path.exists(self.model_weight_path):
            self.model.load_weights(self.model_weight_path)
            print ("model already loaded")

        log = callbacks.CSVLogger(self.logsDir)
        saveBest = ModelCheckpoint(self.model_weight_path, save_best_only=True)
        tb = TensorBoard('logs/')
        self.model.fit(trX, trY, validation_data=(teX, teY), callbacks=[log, saveBest, tb], batch_size=batchSize, epochs=epoch)

        print ("Finished!")


    def predict(self, rawImage):
        tempImage = cv2.cvtColor(rawImage, cv2.COLOR_RGB2GRAY)
        tempImage = cv2.resize(tempImage, (224, 224))
        tempImage = tempImage[116:196, 56:136]
        tempImage = np.asarray(tempImage, np.float32)
        predX = [tempImage]
        predX = np.array(predX, dtype=np.float32).reshape((1, 80, 80, 1))
        predY = self.model.predict(predX)
        return predY[0]

    def takeALook(self, teX, teY):
        model = C.getModel()
        startTime = time.time()
        print("startTime:", startTime)
        result = model.predict(teX)
        endTime = time.time()
        print ("endtime", endTime)
        print ("second per frame %.5f" % (float(endTime - startTime) / float(len(result))))
        for i in range(len(result)):
            print (("true, predict"), (teY[i], result[i][0]))
            cv2.imshow('frame', teX[i])
            cv2.waitKey()



