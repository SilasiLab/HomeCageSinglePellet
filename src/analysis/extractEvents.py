import cv2


class PoseEvent:

    def __init__(self, startFrame, stopFrame, eventType):

        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType



def packageEvent(frameIndexes, poseName):

    tempEvent = PoseEvent(frameIndexes[0], frameIndexes[len(frameIndexes) - 1], poseName)
    return tempEvent


def extractEvents(leftBodypartIndexes, rightBodypartIndexes, h5file, modelName, poseName, likelihoodCutoff, minFrameCount, maxFrameCount, leftSide, rightSide):

    eventStarted = False
    contiguousPositiveCount = 0
    contiguousNegativeCount = 0
    tempEventFrameRange = []
    events = []
    row = 0

    while row < len(h5file.index):
        confidence = 1

        for index in leftBodypartIndexes:
            if h5file.iat[row, index - 2] > leftSide:
                confidence = 0
            else:
                confidence *= h5file.iat[row, index]

        for index in rightBodypartIndexes:
            if h5file.iat[row, index - 2] < rightSide:
                confidence = 0
            else:
                confidence *= h5file.iat[row, index]

        if(eventStarted):
            if(confidence < likelihoodCutoff):
                contiguousNegativeCount += 1
            else:
                contiguousNegativeCount = 0

            tempEventFrameRange.append(row)

            if(contiguousNegativeCount >= maxFrameCount):
                contiguousPositiveCount = 0
                contiguousNegativeCount = 0
                events.append(packageEvent(tempEventFrameRange, poseName))
                tempEventFrameRange = []
                row += 200
                eventStarted = False

            row += 1
            continue

        if(confidence >= likelihoodCutoff):

            contiguousPositiveCount += 1
            tempEventFrameRange.append(row)
        else:
            contiguousPositiveCount = 0
            tempEventFrameRange = []

        if(contiguousPositiveCount >= minFrameCount):
            eventStarted = True

        row += 1

    return events




def review_events(events, videoName, video):
    for event in events:
        print("Event: " + event.eventType)
        print("Start Frame: " + str(event.startFrame))
        print("Stop Frame:" + str(event.stopFrame))
        print("\n")
        video.set(1,event.startFrame)
        for frame in range(event.startFrame, event.stopFrame):
            ret, frame = video.read()
            cv2.imshow(videoName, frame)
            if cv2.waitKey(0) & 0xFF == ord('q'):
                break