import cv2


class PoseEvent:

    def __init__(self, startFrame, stopFrame, eventType):

        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType



def packageEvent(frameIndexes, poseName):

    tempEvent = PoseEvent(frameIndexes[0], frameIndexes[len(frameIndexes) - 1], poseName)
    return tempEvent


def extractEvents(leftMirrorPawIndexes, centerPawIndexes, rightMirrorPawIndexes, points, poseName, avgLikelihoodThreshold_eventStart, minFrameCountThreshold_eventStart, maxFrameCountThreshold_eventEnd, minFramesBetweenEvents):

    eventStarted = False
    contiguousPositiveCount = 0
    contiguousNegativeCount = 0
    tempEventFrameRange = []
    events = []

    for row in points:

        confidence = 0

        for index in leftMirrorPawIndexes:

            if row[index] != -1:
                confidence += row[index].likelihood

        for index in centerPawIndexes:

            if row[index] != -1:
                confidence += row[index].likelihood

        for index in rightMirrorPawIndexes:

            if row[index] != -1:
                confidence += row[index].likelihood

        confidence = (confidence) / (len(leftMirrorPawIndexes) + len(centerPawIndexes) + len(rightMirrorPawIndexes) - 3)



        if(eventStarted):
            if(confidence < avgLikelihoodThreshold_eventStart):
                contiguousNegativeCount += 1
            else:
                contiguousNegativeCount = 0

            tempEventFrameRange.append(row)

            if(contiguousNegativeCount >= maxFrameCountThreshold_eventEnd):
                contiguousPositiveCount = 0
                contiguousNegativeCount = 0
                events.append(packageEvent(tempEventFrameRange, poseName))
                tempEventFrameRange = []
                row += minFramesBetweenEvents
                eventStarted = False

            row += 1
            continue

        if(confidence >= avgLikelihoodThreshold_eventStart):

            contiguousPositiveCount += 1
            tempEventFrameRange.append(row)
        else:
            contiguousPositiveCount = 0
            tempEventFrameRange = []

        if(contiguousPositiveCount >= minFrameCountThreshold_eventStart):
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