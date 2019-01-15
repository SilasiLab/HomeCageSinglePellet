import os
import keras
from keras.models import Sequential, Model
from keras.layers import Dense, LSTM, Dropout,Input,Lambda, BatchNormalization, TimeDistributed
from keras.losses import categorical_crossentropy, binary_crossentropy
from keras import callbacks
from keras.callbacks import ModelCheckpoint, TensorBoard
from keras import regularizers, optimizers

class lstmModel():
    def __init__(self, model_weight_path, logsDir):
        self.data_dim = 27
        self.timesteps = 200
        self.num_classes = 2
        self.model = None
        self.lstmModel = None
        self.model_weight_path = model_weight_path
        self.model_weight_path_backup = model_weight_path + '.backup.h5'
        self.logsDir = logsDir
        self.inputShape = (self.timesteps, self.data_dim)
        self.model = self.getModel()

    def getModel(self):
        if self.model:
            return self.model
        self.model = Sequential()
        self.model.add(LSTM(128, return_sequences=True,input_shape=self.inputShape, kernel_regularizer=regularizers.l2(0.01)))  # returns a sequence of vectors of dimension 32
        self.model.add(BatchNormalization())

        self.model.add(LSTM(128, return_sequences=True, kernel_regularizer=regularizers.l2(0.01)))  # returns a sequence of vectors of dimension 32
        self.model.add(BatchNormalization())


        self.model.add(LSTM(128, dropout=0.2, kernel_regularizer=regularizers.l2(0.01)))
        self.model.add(BatchNormalization())

        self.model.add(Dropout(0.5))
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dense(1024, activation='relu'))
        self.model.add(Dense(1, activation='sigmoid'))
        # rms = RMSprop()

        self.model.summary()
        return self.model

    def train(self, trX, trY, teX, teY, batchSize=32, epoch=20):
        if not self.model:
            self.model = self.getModel()
        self.model.compile(loss=binary_crossentropy, optimizer='adam', metrics=['accuracy'])

        if os.path.exists(self.model_weight_path):
            self.model.load_weights(self.model_weight_path)
            print "model already loaded"

        log = callbacks.CSVLogger(self.logsDir)
        saveBest = ModelCheckpoint(self.model_weight_path, save_best_only=True)
        tb = TensorBoard('logs/')
        self.model.fit(trX, trY, validation_data=(teX, teY), callbacks=[log, saveBest, tb], batch_size=batchSize, epochs=epoch)

        print "Finished!"

    def tuning(self, trX, trY, teX, teY, batchSize=32, epoch=20):
        if not self.model:
            self.model = self.getModel()
        sgd = optimizers.SGD(lr=0.0005, decay=0.05, momentum=0.9, nesterov=True)
        self.model.compile(loss=binary_crossentropy, optimizer=sgd, metrics=['accuracy'])

        if os.path.exists(self.model_weight_path):
            self.model.load_weights(self.model_weight_path)
            print "model already loaded"

        log = callbacks.CSVLogger(self.logsDir)
        saveBest = ModelCheckpoint(self.model_weight_path_backup, save_best_only=True)
        tb = TensorBoard('2ndlogs/')
        self.model.fit(trX, trY, validation_data=(teX, teY), callbacks=[log, saveBest, tb], batch_size=batchSize,
                       epochs=epoch)

        print "Finished!"

    def predict(self, x):
        if not self.model:
            self.model = self.getModel()
        if os.path.exists(self.model_weight_path):
            self.model.load_weights(self.model_weight_path)
            print "model already loaded"
        predX = []
        predX.extend(x)
        predY = self.model.predict(predX)
        print predY