from model import *
from preprocessing import *
from test import loadNpy

if __name__ == '__main__':
    modelPath = 'models/model.h5'
    logsDir = 'history/log.csv'

    # rootDir = "/home/junzheng/work/silasi/frank/MOUSE2/"

    # dataDir = "data/reachingData/"
    # fileList = findAllTxt(dataDir)
    # content = mergeContent(fileList)
    # trX, trY, teX, teY, trTraceback, teTraceback = getBalancedData(content, 0.2)
    trX, trY, teX, teY, trTraceback, teTraceback = loadNpy()
    print trX.shape
    print teX.shape
    print trY.shape
    print teY.shape

    lstm = lstmModel(modelPath, logsDir)
    lstm.train(trX, trY, teX, teY, 32, 100)
    lstm.tuning(trX, trY, teX, teY, 32, 50)
    lstm.model.load_weights(lstm.model_weight_path)
    bestModel = lstm.model
    result = bestModel.predict(teX)
    newResult = []
    for i in result:
        if i[0]>0.5:
            newResult.append(1)
        else:
            newResult.append(0)
    print newResult
    print teY
    print teTraceback