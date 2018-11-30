import pandas as pd
import numpy as np
import csv
import math
import cv2
import sys
from multiprocessing import Process
import matplotlib.pyplot as plt
from time import sleep
import matplotlib.axes as axes
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.patches import Circle
# -------------------------------------------------#
# 				<Load Data>						  #
# -------------------------------------------------#

VIDEO_PATH = sys.argv[1]
H5_PATH = sys.argv[2]
OUTPUT_PATH = sys.argv[3]
DISPLAY_VIDEOS = int(sys.argv[4])
DISPLAY_GRAPHS = int(sys.argv[5])
EXTRACT_VIDEO_CLIPS = int(sys.argv[6])
GEN_CSV = int(sys.argv[7])
PERFORM_CALIBRATION = int(sys.argv[8])


# Load video
video = cv2.VideoCapture(VIDEO_PATH)
frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# Load coordinates file
print("Loading DeepLabCut data...")
dataframe = pd.read_hdf(H5_PATH)
dataframe.to_csv(H5_PATH[:-3] + ".csv")
print("DeepLabCut data loaded")
# -------------------------------------------------#
# 				</Load Data>					  #
# -------------------------------------------------#


# -------------------------------------------------#
# 				<Configure Analysis>			  #
# -------------------------------------------------#


# Calibration temp data
x1, y1, x2, y2 = -1, -1, -1, -1
drawing = False
# Calibration Constants
LEFTSIDE = None
RIGHTSIDE = None
LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH = None
ACTUAL_CALIBRATION_OBJECT_WIDTH = None
RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH = None
LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT = None
ACTUAL_CALIBRATION_OBJECT_HEIGHT = None
RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT = None
PIXELS_MM_Y_LEFTMIRROR = None
PIXELS_MM_Z_LEFTMIRROR = None
PIXELS_MM_X_ACTUAL = None
PIXELS_MM_Y_ACTUAL = None
PIXELS_MM_Y_RIGHTMIRROR = None
PIXELS_MM_Z_RIGHTMIRROR = None
Y_ORIGIN_LEFTMIRROR = None
Z_ORIGIN_LEFTMIRROR = None
X_ORIGIN_ACTUAL = None
Y_ORIGIN_ACTUAL = None
Y_ORIGIN_RIGHTMIRROR = None
Z_ORIGIN_RIGHTMIRROR = None




# Pose event parsing config
LIKELIHOOD_THRESHOLD = 0.5
MIN_FRAME_COUNT_EVENT_START = 10
MAX_FRAME_COUNT_EVENT_STOP = 20
MIN_FRAME_COUNT_BETWEEN_EVENTS = 30
# Visual output config
POINT_SIZE = 4
LINE_THICKNESS = 3
N_TRAILING_POINTS = 10
PAINT_GHOST_TRAILS = True
# -------------------------------------------------#
# 				</Configure Analysis>			  #
# -------------------------------------------------#


class PoseEvent:

    def __init__(self, startFrame, stopFrame, eventType):

        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType
        self.xVals = None
        self.yVals = None
        self.zVals = None

def packageEvent(frameIndexes, poseName):

    tempEvent = PoseEvent(frameIndexes[0], frameIndexes[len(frameIndexes) - 1], poseName)
    return tempEvent


def extractEvents(leftMirrorPawIndexes, centerPawIndexes, rightMirrorPawIndexes, points, poseName):

    global LIKELIHOOD_THRESHOLD
    global MIN_FRAME_COUNT_EVENT_START
    global MAX_FRAME_COUNT_EVENT_STOP
    global MIN_FRAME_COUNT_BETWEEN_EVENTS


    eventStarted = False
    contiguousPositiveCount = 0
    contiguousNegativeCount = 0
    tempEventFrameRange = []
    events = []
    row = 0
    while row < len(points) - 1:

        confidence = 0

        for index in leftMirrorPawIndexes:

            if points[row][index] != -1:
                confidence += points[row][index].likelihood

        for index in centerPawIndexes:

            if points[row][index] != -1:
                confidence += points[row][index].likelihood

        for index in rightMirrorPawIndexes:

            if points[row][index] != -1:
                confidence += points[row][index].likelihood

        confidence = (confidence) / (len(leftMirrorPawIndexes) + len(centerPawIndexes) + len(rightMirrorPawIndexes) - 3)



        if(eventStarted):
            if(confidence < LIKELIHOOD_THRESHOLD):
                contiguousNegativeCount += 1
            else:
                contiguousNegativeCount = 0

            tempEventFrameRange.append(row)

            if(contiguousNegativeCount >= MAX_FRAME_COUNT_EVENT_STOP):
                contiguousPositiveCount = 0
                contiguousNegativeCount = 0
                events.append(packageEvent(tempEventFrameRange, poseName))
                tempEventFrameRange = []
                row += MIN_FRAME_COUNT_BETWEEN_EVENTS
                eventStarted = False

            row += 1
            continue

        if(confidence >= LIKELIHOOD_THRESHOLD):

            contiguousPositiveCount += 1
            tempEventFrameRange.append(row)
        else:
            contiguousPositiveCount = 0
            tempEventFrameRange = []

        if(contiguousPositiveCount >= MIN_FRAME_COUNT_EVENT_START):

            eventStarted = True

            # If an event is started, grab the first 20 frames before the event started
            eventFramePadding = []
            for i in range(row - MIN_FRAME_COUNT_EVENT_START - 20, row - MIN_FRAME_COUNT_EVENT_START + 1):
                if(i >= 0 and i < len(points)):
                    eventFramePadding.append(i)

            tempEventFrameRange = eventFramePadding + tempEventFrameRange
            eventFramePadding = []

        row += 1

    return events


def review_event(event, videoName, video, points):
        

    print("Event: " + event.eventType)
    print("Start Frame: " + str(event.startFrame))
    print("Stop Frame:" + str(event.stopFrame))
    print("\n")


    video.set(1,event.startFrame)
    for frame in range(event.startFrame, event.stopFrame + 1):
        ret, fr = video.read()
        paint_frame_points(points[frame],fr)
        cv2.imshow(videoName, fr)
        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    return 0


def spawn_event_review_process(event, videoName, video, points):
    p = Process(target=review_event, args=(event, videoName, video, points))
    p.start()
    return p


class Point:

    def __init__(self, x, y, likelihood):
        self.x = x
        self.y = y
        self.likelihood = likelihood



def gen_point_colors(nLabels):
    colors = []

    for i in range(0, nLabels):
        b = np.random.randint(0, 256)
        g = np.random.randint(0, 256)
        r = np.random.randint(0, 256)
        color = (b, g, r)
        colors.append(color)

    return colors


def get_labels(dataframe):
    dfl = list(dataframe)
    nLabels = int(len(dfl) / 3)
    labels = []

    for i in range(0, nLabels):
        labels.append(dfl[i * 3][1])

    return labels, nLabels


def paint_frame_points(points, frame):
    for point in points:
        if (point != -1):
            cv2.circle(frame, (int(point.x), int(point.y)), POINT_SIZE, (255, 0, 0), -1)


def gen_ghost_trail_point_lists(nLabels):
    lists = []
    for l in range(0, nLabels):
        lists.append([-1] * nLabels)
    return lists


def update_ghost_trail_point_lists(lists, points):
    if (len(lists) != len(points)):
        print("Error: The number of lists does not equal the numbers of points!")

    for i in range(0, len(lists)):

        if (len(lists[i]) >= N_TRAILING_POINTS):
            lists[i].pop(0)

        lists[i].append(points[i])


def paint_ghost_trails(ghostTrailPoints, frame, overlay, colors):

    global POINT_SIZE
    global LINE_THICKNESS

    colorIndex = 0
    opacityStepSize = 1 / len(ghostTrailPoints)

    for points in ghostTrailPoints:

        opacity = opacityStepSize
        for p in range(1, len(points)):
            if (points[p - 1] != -1 and points[p] != -1):
                point1 = (int(points[p - 1].x), int(points[p - 1].y))
                point2 = (int(points[p].x), int(points[p].y))
                cv2.circle(overlay, point1, POINT_SIZE, colors[colorIndex], -1)
                cv2.line(overlay, point1, point2, colors[colorIndex], LINE_THICKNESS)
                cv2.addWeighted(overlay, opacity, frame, 1 - opacity, 0, frame)
                opacity += opacityStepSize
                overlay = frame.copy()
        if (points[len(points) - 1] != -1):
            cv2.circle(frame, (int(points[len(points) - 1].x), int(points[len(points) - 1].y)), POINT_SIZE,
                       colors[colorIndex], -1)

        colorIndex += 1


def get_point_distance(point1, point2):

    x_dist = abs(point1[0] - point2[0])
    y_dist = abs(point1[1] - point2[1])
    dist = math.sqrt(pow(x_dist, 2) + pow(y_dist, 2))

    return dist


def graph_3D_trajectory(x_points, y_points, z_points):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.set_xlim(-10, 10)
    ax.set_ylim(-17, 3)
    ax.set_zlim(-5, 5)
    ax.plot(x_points, z_points, y_points)
    ax.scatter(0.5, 0.5, 0.5, color="black", s=100)
    ax.text(0,0,0,'P',size=15,zorder=1,color='black')
    ax.text(x_points[0], z_points[0], y_points[0], 'S', size=20, zorder=1, color='g')
    ax.text(x_points[len(x_points) - 1], z_points[len(z_points) - 1], y_points[len(y_points) - 1], 'F', size=20, zorder=1, color='r')
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')
    plt.show()
    cv2.waitKey(0)
    return 0

def spawn_3D_graph(x_points, y_points, z_points):
    p = Process(target=graph_3D_trajectory, args=(x_points, y_points, z_points,))
    p.start()
    return p




def print_calibration_info():

    # Calibration Constants
    global LEFTSIDE
    global RIGHTSIDE
    global LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global ACTUAL_CALIBRATION_OBJECT_WIDTH
    global RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global ACTUAL_CALIBRATION_OBJECT_HEIGHT
    global RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR

    print("LEFTSIDE=" + str(LEFTSIDE))
    print("RIGHTSIDE=" + str(RIGHTSIDE))
    print("LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH=" + str(LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH))
    print("LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT=" + str(LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT))
    print("ACTUAL_CALIBRATION_OBJECT_WIDTH=" + str(ACTUAL_CALIBRATION_OBJECT_WIDTH))
    print("ACTUAL_CALIBRATION_OBJECT_HEIGHT=" + str(ACTUAL_CALIBRATION_OBJECT_HEIGHT))
    print("RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH=" + str(RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH))
    print("RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT=" + str(RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT))
    print("PIXELS_MM_Y_LEFT_MIRROR=" + str(PIXELS_MM_Y_LEFTMIRROR))
    print("PIXELS_MM_Z_LEFT_MIRROR=" + str(PIXELS_MM_Z_LEFTMIRROR))
    print("PIXELS_MM_X_ACTUAL=" + str(PIXELS_MM_X_ACTUAL))
    print("PIXELS_MM_Y_ACTUAL=" + str(PIXELS_MM_Y_ACTUAL))
    print("PIXELS_MM_Y_RIGHT_MIRROR=" + str(PIXELS_MM_Y_RIGHTMIRROR))
    print("PIXELS_MM_Z_RIGHT_MIRROR=" + str(PIXELS_MM_Z_RIGHTMIRROR))
    print("Y_ORIGIN_LEFTMIRROR=" + str(Y_ORIGIN_LEFTMIRROR))
    print("Z_ORIGIN_LEFTMIRROR=" + str(Z_ORIGIN_LEFTMIRROR))
    print("X_ORIGIN_ACTUAL=" + str(X_ORIGIN_ACTUAL))
    print("Y_ORIGIN_ACTUAL=" + str(Y_ORIGIN_ACTUAL))
    print("Y_ORIGIN_RIGHTMIRROR=" + str(Y_ORIGIN_RIGHTMIRROR))
    print("Z_ORIGIN_RIGHTMIRROR=" + str(Z_ORIGIN_RIGHTMIRROR))



def click_and_draw_line(event, x, y, flags, param):

    global manualCalibrationPoints, x1, y1, x2, y2, drawing, mode

    if event == cv2.EVENT_LBUTTONDOWN:
        x1 = x
        y1 = y
        x2 = x
        y2 = y
        drawing = True

    elif event == cv2.EVENT_MOUSEMOVE:

        if(drawing):
            x2 = x
            y2 = y

    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False

def perform_manual_calibration(calibrationFrame):

    # Calibration Constants
    global LEFTSIDE
    global RIGHTSIDE
    global LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global ACTUAL_CALIBRATION_OBJECT_WIDTH
    global RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global ACTUAL_CALIBRATION_OBJECT_HEIGHT
    global RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR

    LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH = float(input("Enter the width of the left mirror calibration object in mm: "))
    LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT = float(input("Enter the height of the left mirror calibration object in mm: "))
    ACTUAL_CALIBRATION_OBJECT_WIDTH = float(input("Enter the width of the center view calibration object in mm: "))
    ACTUAL_CALIBRATION_OBJECT_HEIGHT = float(input("Enter the height of the center view calibration object in mm: "))
    RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH = float(input("Enter the width of the right mirror calibration object in mm: "))
    RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT = float(input("Enter the height of the right mirror calibration object in mm: "))
    print("\n")

    cv2.namedWindow("calibrationFrame")
    cv2.setMouseCallback("calibrationFrame", click_and_draw_line)


    print("Draw left mirror segmentation line.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (0,255,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            print("LEFTSIDE saved as x=" + str(x1))
            LEFTSIDE = x1
            break
    print("\n")

    print("Draw right mirror segmentation line.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (255,0,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            print("RIGHTSIDE saved as x=" + str(x1))
            RIGHTSIDE = x1
            break
    print("\n")

    print("Draw line across width of calibration object in left mirror.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (0,255,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_Z_LEFTMIRROR = (dist / LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH)
            break
    print("\n")

    print("Draw line across height of calibration object in left mirror.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (255,0,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_Y_LEFTMIRROR = (dist / LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT)
            break
    print("\n")

    print("Draw line across width of calibration object in center view.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (0,255,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_X_ACTUAL = (dist / ACTUAL_CALIBRATION_OBJECT_WIDTH)
            break
    print("\n")

    print("Draw line across height of calibration object in center view.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (255,0,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_Y_ACTUAL = (dist / ACTUAL_CALIBRATION_OBJECT_HEIGHT)
            break
    print("\n")

    print("Draw line across width of calibration object in right mirror.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (0,255,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_Z_RIGHTMIRROR = (dist / RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH)
            break
    print("\n")

    print("Draw line across height of calibration object in right mirror.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.line(modified_calibrationFrame, (x1,y1), (x2,y2), (255,0,0), 1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            dist = get_point_distance((x1,y1),(x2,y2))
            PIXELS_MM_Y_RIGHTMIRROR = (dist / RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT)
            break
    print("\n")

    print("Click on Y origin in left mirror.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (0,255,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            Y_ORIGIN_LEFTMIRROR = y1
            break
    print("\n")

    print("Click on Z origin in left mirror.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (255,0,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            Z_ORIGIN_LEFTMIRROR = x1
            break
    print("\n")

    print("Click on X origin in center view.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (0,255,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            X_ORIGIN_ACTUAL = x1
            break
    print("\n")

    print("Click on y origin in center view.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (255,0,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            Y_ORIGIN_ACTUAL = y1
            break
    print("\n")

    print("Click on Y origin in right mirror.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (0,255,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            Y_ORIGIN_RIGHTMIRROR = y1
            break
    print("\n")

    print("Click on Z origin in right mirror.")
    print("When you're happy with the point, press 's' to save.")
    while(1):
        modified_calibrationFrame = calibrationFrame.copy()
        cv2.circle(modified_calibrationFrame, (x1,y1), 2, (255,0,0), -1)
        cv2.imshow("calibrationFrame", modified_calibrationFrame)
        if cv2.waitKey(1) & 0xFF == ord('s'):
            Z_ORIGIN_RIGHTMIRROR = x1
            break
    print("\n")

    print("Recapping calibration values...\n")
    print_calibration_info()


    return 0


def save_calibration_data():

    # Calibration Constants
    global LEFTSIDE
    global RIGHTSIDE
    global LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global ACTUAL_CALIBRATION_OBJECT_WIDTH
    global RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global ACTUAL_CALIBRATION_OBJECT_HEIGHT
    global RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR


    with open("../../config/3D_reconstruction_calibration.txt", 'w') as f:
         f.write(str(LEFTSIDE) + "\n")
         f.write(str(RIGHTSIDE) + "\n")
         f.write(str(LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH) + "\n")
         f.write(str(ACTUAL_CALIBRATION_OBJECT_WIDTH) + "\n")
         f.write(str(RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH) + "\n")
         f.write(str(LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT) + "\n")
         f.write(str(ACTUAL_CALIBRATION_OBJECT_HEIGHT) + "\n")
         f.write(str(RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT) + "\n")
         f.write(str(PIXELS_MM_Y_LEFTMIRROR) + "\n")
         f.write(str(PIXELS_MM_Z_LEFTMIRROR) + "\n")
         f.write(str(PIXELS_MM_X_ACTUAL) + "\n")
         f.write(str(PIXELS_MM_Y_ACTUAL) + "\n")
         f.write(str(PIXELS_MM_Y_RIGHTMIRROR) + "\n")
         f.write(str(PIXELS_MM_Z_RIGHTMIRROR) + "\n")
         f.write(str(Y_ORIGIN_LEFTMIRROR) + "\n")
         f.write(str(Z_ORIGIN_LEFTMIRROR) + "\n")
         f.write(str(X_ORIGIN_ACTUAL) + "\n")
         f.write(str(Y_ORIGIN_ACTUAL) + "\n")
         f.write(str(Y_ORIGIN_RIGHTMIRROR) + "\n")
         f.write(str(Z_ORIGIN_RIGHTMIRROR) + "\n")


def load_calibration_data():

    # Calibration Constants
    global LEFTSIDE
    global RIGHTSIDE
    global LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global ACTUAL_CALIBRATION_OBJECT_WIDTH
    global RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global ACTUAL_CALIBRATION_OBJECT_HEIGHT
    global RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR


    with open("../../config/3D_reconstruction_calibration.txt") as f:

        LEFTSIDE = int(f.readline())
        RIGHTSIDE = int(f.readline())
        LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH = float(f.readline())
        ACTUAL_CALIBRATION_OBJECT_WIDTH = float(f.readline())
        RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH = float(f.readline())
        LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT = float(f.readline())
        ACTUAL_CALIBRATION_OBJECT_HEIGHT = float(f.readline())
        RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT = float(f.readline())
        PIXELS_MM_Y_LEFTMIRROR = float(f.readline())
        PIXELS_MM_Z_LEFTMIRROR = float(f.readline())
        PIXELS_MM_X_ACTUAL = float(f.readline())
        PIXELS_MM_Y_ACTUAL = float(f.readline())
        PIXELS_MM_Y_RIGHTMIRROR = float(f.readline())
        PIXELS_MM_Z_RIGHTMIRROR = float(f.readline())
        Y_ORIGIN_LEFTMIRROR = int(f.readline())
        Z_ORIGIN_LEFTMIRROR = int(f.readline())
        X_ORIGIN_ACTUAL = int(f.readline())
        Y_ORIGIN_ACTUAL = int(f.readline())
        Y_ORIGIN_RIGHTMIRROR = int(f.readline())
        Z_ORIGIN_RIGHTMIRROR = int(f.readline())


def filter_points_missing_dimension(x,y,z):


    filteredX = []
    filteredY = []
    filteredZ = []

    for i in range(0,len(x)):
        if(x[i]!=None and y[i]!=None and z[i]!=None):
            filteredX.append(x[i])
            filteredY.append(y[i])
            filteredZ.append(z[i])

    return filteredX, filteredY, filteredZ

    


def convert_pixelCoord_to_realWorld(x_points, y_points, z_points):


    # Calibration Constants
    global LEFTSIDE
    global RIGHTSIDE
    global LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global ACTUAL_CALIBRATION_OBJECT_WIDTH
    global RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH
    global LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global ACTUAL_CALIBRATION_OBJECT_HEIGHT
    global RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR

    realWorldX = []
    realWorldY = []
    realWorldZ = []

    for point in x_points:
        if point != None and point != -1:
            realWorldX.append((point - X_ORIGIN_ACTUAL) / PIXELS_MM_X_ACTUAL)
        else:
            realWorldX.append(None)
    for point in y_points:
        if point != None and point != -1:
            realWorldY.append((Y_ORIGIN_LEFTMIRROR - point) / PIXELS_MM_Y_LEFTMIRROR)
        else:
            realWorldY.append(None)
    for point in z_points:
        if point != None and point != -1:
            realWorldZ.append((Z_ORIGIN_LEFTMIRROR - point) / PIXELS_MM_Z_LEFTMIRROR)
        else:
            realWorldZ.append(None)

    if(not (len(realWorldX) == len(realWorldY) == len(realWorldZ))):
        print("Error: convert_pixelCoord_to_realWorld(): Coordinate list lengths do not match")
        exit()

    realWorldX, realWorldY, realWorldZ = filter_points_missing_dimension(realWorldX, realWorldY, realWorldZ)

    return realWorldX, realWorldY, realWorldZ
 


# -----------------------------------------------------------------------------#
# All functions below this line are NOT generic and must be rewritten based on #
# use case.																       #
# ------------------------------------------------------------------------------#

def filter_trajectory_points(dataframe):
    global LEFTSIDE
    global RIGHTSIDE
    global LIKELIHOOD_THRESHOLD
    filteredPoints = []

    for row in range(0, len(dataframe.index) - 1):

        framePoints = []
        h5ColIndex = 0

        # Filter left mirror paw points
        for i in range(0, 5):
            x = dataframe.iat[row, h5ColIndex]
            y = dataframe.iat[row, h5ColIndex + 1]
            l = dataframe.iat[row, h5ColIndex + 2]
            if (x <= LEFTSIDE and l >= LIKELIHOOD_THRESHOLD):
                framePoints.append(Point(x, y, l))
            else:
                framePoints.append(-1)
            h5ColIndex += 3

        # Filter points for center paw
        for i in range(0, 5):
            x = dataframe.iat[row, h5ColIndex]
            y = dataframe.iat[row, h5ColIndex + 1]
            l = dataframe.iat[row, h5ColIndex + 2]
            if (x >= LEFTSIDE and x <= RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
                framePoints.append(Point(x, y, l))
            else:
                framePoints.append(-1)
            h5ColIndex += 3

        # Filter points for right paw
        for i in range(0, 5):
            x = dataframe.iat[row, h5ColIndex]
            y = dataframe.iat[row, h5ColIndex + 1]
            l = dataframe.iat[row, h5ColIndex + 2]
            if (x >= RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
                framePoints.append(Point(x, y, l))
            else:
                framePoints.append(-1)
            h5ColIndex += 3


        # Filter point for left mirror pellet
        x = dataframe.iat[row, h5ColIndex]
        y = dataframe.iat[row, h5ColIndex + 1]
        l = dataframe.iat[row, h5ColIndex + 2]

        if (x <= LEFTSIDE and l >= LIKELIHOOD_THRESHOLD):
            framePoints.append(Point(x, y, l))
        else:
            framePoints.append(-1)
        h5ColIndex += 3

        # Filter point for center pellet
        x = dataframe.iat[row, h5ColIndex]
        y = dataframe.iat[row, h5ColIndex + 1]
        l = dataframe.iat[row, h5ColIndex + 2]

        if (l >= LIKELIHOOD_THRESHOLD):
            framePoints.append(Point(x, y, l))
        else:
            framePoints.append(-1)
        h5ColIndex += 3

        # Filter point for right mirror pellet
        x = dataframe.iat[row, h5ColIndex]
        y = dataframe.iat[row, h5ColIndex + 1]
        l = dataframe.iat[row, h5ColIndex + 2]

        if (x >= RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
            framePoints.append(Point(x, y, l))
        else:
            framePoints.append(-1)
        h5ColIndex += 3



        # Filter points for center face
        for i in range(0, 6):
            x = dataframe.iat[row, h5ColIndex]
            y = dataframe.iat[row, h5ColIndex + 1]
            l = dataframe.iat[row, h5ColIndex + 2]
            if (x >= LEFTSIDE and x <= RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
                framePoints.append(Point(x, y, l))
            else:
                framePoints.append(-1)
            h5ColIndex += 3


        filteredPoints.append(framePoints)


    return filteredPoints


def gen_reach_trajectory_reconsutrction_xyz(event, points, reachingHand):

    x_points = []
    y_points = []
    z_points = []
    last_x = None
    last_y = None
    last_z = None


    for frameIndex in range(event.startFrame, event.stopFrame + 1):

        frameX = 0
        frameY = 0
        frameZ = 0
        tempN = 0


        if(reachingHand == "LEFT"):
            # Get Y from Left Mirror Paw
            for point in range(1,3):
                if points[frameIndex][point] != -1:
                    frameY += points[frameIndex][point].y
                    tempN += 1
            if(tempN != 0):
                frameY = frameY / tempN
                tempN = 0

            # Get Z from Left Mirror Paw
            for point in range(1,3):
                if points[frameIndex][point] != -1:
                    frameZ += points[frameIndex][point].x
                    tempN += 1
            if(tempN != 0):
                frameZ = frameZ / tempN
                tempN = 0

            # Get X from Center Paw
            for point in range(7,9):
                if points[frameIndex][point] != -1:
                    frameX += points[frameIndex][point].x
                    tempN += 1
            if(tempN !=0):
                frameX = frameX / tempN
                tempN = 0

        elif(reachingHand == "RIGHT"):

            # Get Y from Right Mirror Paw
            for point in range(12, 13):
                if points[frameIndex][point] != -1:
                    frameY += points[frameIndex][point].y
                    tempN += 1
            if (tempN != 0):
                frameY = frameY / tempN
                tempN = 0

            # Get Z from Right Mirror Paw
            for point in range(12, 13):
                if points[frameIndex][point] != -1:
                    frameZ += points[frameIndex][point].x
                    tempN += 1
            if (tempN != 0):
                frameZ = frameZ / tempN
                tempN = 0

            # Get X from Center Paw
            for point in range(5, 10):
                if points[frameIndex][point] != -1:
                    frameX += points[frameIndex][point].x
                    tempN += 1
            if (tempN != 0):
                frameX = frameX / tempN
                tempN = 0


        if(last_x == None and frameX > 0):
                last_x = frameX

        if(last_y == None and frameY > 0):
                last_y = frameY

        if(last_z == None and frameZ > 0):
                last_z = frameZ




        if(frameX > 0):
            x_points.append(frameX)
            last_x = frameX
        elif(last_x != None):
            x_points.append(last_x)
        else:
            x_points.append(-1)
            last_x = None

        if(frameY > 0):
            y_points.append(frameY)
            last_y = frameY
        elif(last_y != None):
            y_points.append(last_y)
        else:
            y_points.append(-1)
            last_y = None

        if(frameZ > 0):
            z_points.append(frameZ)
            last_z = frameZ
        elif(last_z != None):
            z_points.append(last_z)
        else:
            z_points.append(-1)
            last_z = None


    if(not (len(x_points) == len(y_points) == len(z_points))):
        print("Error: gen_reach_trajectory_reconstruction_xyz(): Coordinate list lengths do not match")
        exit()

    return x_points, y_points, z_points
# ----------------------------------------------------------------------------------#




def extract_vid_range(start, stop, video, ghostTrailPoints, filteredPoints, colors, name):

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(name+".avi",fourcc,139.0,(1180,480))
    video.set(cv2.CAP_PROP_POS_FRAMES, start)
    for f in range(start, stop):
        ret, frame = video.read()
        overlay = frame.copy()
        update_ghost_trail_point_lists(ghostTrailPoints, filteredPoints[f])
        paint_ghost_trails(ghostTrailPoints, frame, overlay, colors)
        out.write(frame)








def main():


    if(PERFORM_CALIBRATION):
        ret, calibrationFrame = video.read()
        video.set(cv2.CAP_PROP_POS_FRAMES, 0)
        perform_manual_calibration(calibrationFrame)
        save_calibration_data()
    else:
        print("Loading calibration data...")
        load_calibration_data()
        print("Calibration data loaded.")

    labels, nLabels = get_labels(dataframe)
    colors = gen_point_colors(nLabels)
    ghostTrailPoints = gen_ghost_trail_point_lists(nLabels)
    print("Filtering DeepLabCut points...")
    filteredPoints = filter_trajectory_points(dataframe)
    print("DeepLabCut points filtered")

    # Extract reaching events
    print("Finding reaches...")
    events = extractEvents([0, 1, 2, 3, 4], [5, 6, 7, 8, 9], [10, 11, 12, 13, 14], filteredPoints, "reachingReconstruction")
    print("Reaches found: " + str(len(events)))

    print("Computing 3D reconstructions...")
    for event in events:
        x, y, z = gen_reach_trajectory_reconsutrction_xyz(event, filteredPoints, "LEFT")
        x, y, z = convert_pixelCoord_to_realWorld(x, y, z)
        event.xVals = x
        event.yVals = y
        event.zVals = z
    print("3D reconstructions completed")

    # Gen output for each event
    print("Generating output...")
    for event in events:


        if(DISPLAY_VIDEOS):
            review_event(event, VIDEO_PATH, video, filteredPoints)
            cv2.waitKey(0)
        if(DISPLAY_GRAPHS):
            spawn_3D_graph(np.asarray(event.xVals), np.asarray(event.yVals), np.asarray(event.zVals))
            cv2.waitKey(0)
        if(EXTRACT_VIDEO_CLIPS):
            extract_vid_range(event.startFrame, event.stopFrame, video, ghostTrailPoints, filteredPoints, colors,str(event.startFrame))
        if(GEN_CSV):
            with open(OUTPUT_PATH, 'a', newline='') as outputFile:

                outputFile.write(str(event.startFrame) + "\n")
                outputFile.write(str(event.stopFrame) + "\n")
                wr = csv.writer(outputFile)

                for i in range(0, len(event.xVals)):
                    line = []
                    line.append(event.xVals[i])
                    line.append(event.yVals[i])
                    line.append(event.zVals[i])
                    wr.writerow(line)
                outputFile.write("\n\n")
    print("Done")



if __name__ == "__main__":
    main()
