import pandas as pd
import numpy as np
import math
import cv2
import sys
from multiprocessing import Process
import matplotlib.pyplot as plt
from time import sleep
import matplotlib.axes as axes
from mpl_toolkits.mplot3d import Axes3D

# -------------------------------------------------#
# 				<Load Data>						  #
# -------------------------------------------------#

VIDEO_PATH = sys.argv[1]
H5_PATH = sys.argv[2]

# Load video
video = cv2.VideoCapture(VIDEO_PATH)
frameCount = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
fps = video.get(cv2.CAP_PROP_FPS)

# Load coordinates file
dataframe = pd.read_hdf(H5_PATH)
dataframe.to_csv(H5_PATH[:-3] + ".csv")

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




# Likelihood cutoff for DLC points
LIKELIHOOD_THRESHOLD = 0.99
# Visual output config
POINT_SIZE = 4
LINE_THICKNESS = 3
N_TRAILING_POINTS = 10
PAINT_GHOST_TRAILS = True
DISPLAY_VIDEO = True

# -------------------------------------------------#
# 				</Configure Analysis>			  #
# -------------------------------------------------#


class Point:

    def __init__(self, x, y, likelihood):
        self.x = x
        self.y = y
        self.likelihood = likelihood


class KinematicEvent:

    def __init__(self, startFrame, stopFrame, eventType, data):
        self.startFrame = startFrame
        self.stopFrame = stopFrame
        self.eventType = eventType
        # List of lists where outer list is a frame and inner list is all points for that frame
        self.data = data


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


def paint_ghost_trails(ghostTrailPoints, frame, overlay):
    global colors
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
    ax.set_xlim(0, 10)
    ax.set_ylim(-4, 9)
    ax.set_zlim(8, 18)
    ax.plot(x_points, z_points, y_points)
    ax.text(x_points[0], z_points[0], y_points[0], 'S', size=20, zorder=1, color='g')
    ax.text(x_points[len(x_points) - 1], z_points[len(z_points) - 1], y_points[len(y_points) - 1], 'F', size=20,
            zorder=1, color='r')
    ax.set_xlabel('x')
    ax.set_ylabel('z')
    ax.set_zlabel('y')
    plt.show()
    cv2.waitKey(0)


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

    LEFT_MIRROR_CALIBRATION_OBJECT_WIDTH = int(input("Enter the width of the left mirror calibration object in mm: "))
    LEFT_MIRROR_CALIBRATION_OBJECT_HEIGHT = int(input("Enter the height of the left mirror calibration object in mm: "))
    ACTUAL_CALIBRATION_OBJECT_WIDTH = int(input("Enter the width of the center view calibration object in mm: "))
    ACTUAL_CALIBRATION_OBJECT_HEIGHT = int(input("Enter the height of the center view calibration object in mm: "))
    RIGHT_MIRROR_CALIBRATION_OBJECT_WIDTH = int(input("Enter the width of the right mirror calibration object in mm: "))
    RIGHT_MIRROR_CALIBRATION_OBJECT_HEIGHT = int(input("Enter the height of the right mirror calibration object in mm: "))
    print("\n")

    cv2.namedWindow("calibrationFrame")
    cv2.setMouseCallback("calibrationFrame", click_and_draw_line)


    print("Draw left mirror segmentation line.")
    print("When you're happy with the line, press 's' to save.")
    while(1):
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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
        sleep(0.05)
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








# -----------------------------------------------------------------------------#
# All functions below this line are NOT generic and must be rewritten based on #
# use case.																       #
# ------------------------------------------------------------------------------#


def convert_pixelCoord_to_realWorld(x_points, y_points, z_points):
    global PIXELS_MM_X_ACTUAL
    global PIXELS_MM_Y_RIGHTMIRROR
    global PIXELS_MM_Z_RIGHTMIRROR
    global PIXELS_MM_Y_LEFTMIRROR
    global PIXELS_MM_Z_LEFTMIRROR
    global X_ORIGIN_ACTUAL
    global Y_ORIGIN_RIGHTMIRROR
    global Z_ORIGIN_RIGHTMIRROR
    global Y_ORIGIN_LEFTMIRROR
    global Z_ORIGIN_LEFTMIRROR

    realWorldX = []
    realWorldY = []
    realWorldZ = []

    for point in x_points:
        realWorldX.append((point - X_ORIGIN_ACTUAL) / PIXELS_MM_X_ACTUAL)
    for point in y_points:
        realWorldY.append((Y_ORIGIN_LEFTMIRROR - point) / PIXELS_MM_Y_LEFTMIRROR)
    for point in z_points:
        realWorldZ.append((Z_ORIGIN_LEFTMIRROR - point) / PIXELS_MM_Z_LEFTMIRROR)

    return realWorldX, realWorldY, realWorldZ


def filter_frame_points(dataframe, rowIndex):
    global LEFTSIDE
    global RIGHTSIDE
    global LIKELIHOOD_THRESHOLD
    points = []

    # Package points for left mirror
    h5ColIndex = 0
    for i in range(0, 5):
        x = dataframe.iat[rowIndex, h5ColIndex]
        y = dataframe.iat[rowIndex, h5ColIndex + 1]
        l = dataframe.iat[rowIndex, h5ColIndex + 2]
        if (x <= LEFTSIDE and l >= LIKELIHOOD_THRESHOLD):
            points.append(Point(x, y, l))
        else:
            points.append(-1)
        h5ColIndex += 3

    # Package points for right mirror
    for i in range(6, 11):
        x = dataframe.iat[rowIndex, h5ColIndex]
        y = dataframe.iat[rowIndex, h5ColIndex + 1]
        l = dataframe.iat[rowIndex, h5ColIndex + 2]
        if (x >= RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
            points.append(Point(x, y, l))
        else:
            points.append(-1)
        h5ColIndex += 3

    # Package points for middle (left paw)
    for i in range(11, 16):
        x = dataframe.iat[rowIndex, h5ColIndex]
        y = dataframe.iat[rowIndex, h5ColIndex + 1]
        l = dataframe.iat[rowIndex, h5ColIndex + 2]
        if (x > LEFTSIDE and x < RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
            points.append(Point(x, y, l))
        else:
            points.append(-1)
        h5ColIndex += 3

    # Package points for middle (right paw)
    for i in range(16, 21):
        x = dataframe.iat[rowIndex, h5ColIndex]
        y = dataframe.iat[rowIndex, h5ColIndex + 1]
        l = dataframe.iat[rowIndex, h5ColIndex + 2]
        if (x > LEFTSIDE and x < RIGHTSIDE and l >= LIKELIHOOD_THRESHOLD):
            points.append(Point(x, y, l))
        else:
            points.append(-1)
        h5ColIndex += 3

    return points


def gen_trajectory_reconsutrction_xyz(framePoints):
    x_points = []
    y_points = []
    z_points = []
    last_x = None
    last_y = None
    last_z = None

    for points in framePoints:
        x = 0
        y = 0
        z = 0

        # Determine which hand is being reached with
        leftCount = 0
        rightCount = 0
        for point in range(10, 14):
            if points[point] != -1:
                leftCount += 1
        for point in range(15, 19):
            if points[point] != -1:
                rightCount += 1

        # Take paw-center label location as x coordinate
        if leftCount >= rightCount:
            if points[14] != -1:
                x = points[14].x
        else:
            if points[19] != -1:
                x += points[19].x

        nMirror = 0
        for point in range(1, 2):
            if points[point] != -1:
                z += points[point].x
                y += points[point].y
                nMirror += 1
        if nMirror != 0:
            y = y / nMirror
            z = z / nMirror

        if x == 0 and last_x == None:
            continue
        elif y == 0 and last_y == None:
            continue
        elif z == 0 and last_z == None:
            continue

        if x != 0:
            x_points.append(x)
        else:
            x_points.append(last_x)

        if y != 0:
            y_points.append(y)
        else:
            y_points.append(last_y)

        if z != 0:
            z_points.append(z)
        else:
            z_points.append(last_z)

    return x_points, y_points, z_points




# ----------------------------------------------------------------------------------#



# These hold information for each reach. Right now we're manually setting
# start/stop frames. Eventually we can write something to find the events
# automatically
#eventStartFrame = 1900
#eventStopFrame = 2050
#eventPoints = []
#eventFrames = []
#kinematicEvents = extractEvents.extractEvents([2,5,8,11], [17,20,23,26], dataframe,"DeepCut_resnet50_manualSinglePellet2Sep30Shuffle1_300000", "manualSinglePellet", 0.95, 5, 20, LEFTSIDE, RIGHTSIDE)
#for event in kinematicEvents:
#    print(event.eventType)
#    print(event.startFrame)
#    print(event.stopFrame)

#extractEvents.review_events(kinematicEvents,sys.argv[1],video)
#exit()




# Perform manual calibration
ret, calibrationFrame = video.read()
video.set(cv2.CAP_PROP_POS_FRAMES, 0)
perform_manual_calibration(calibrationFrame)

# Load point data
# Gen list of colors for points
# Gen lists that will contain "ghost trail" points
labels, nLabels = get_labels(dataframe)
colors = gen_point_colors(nLabels)
ghostTrailPoints = gen_ghost_trail_point_lists(nLabels)
filteredPoints = []

def main():


    # Loop over every frame in the video/DLC-data
    for row in range(0, len(dataframe.index) - 1):


        # Load the frame
        ret, frame = video.read()
        # Make an overlay for ghostly trails
        overlay = frame.copy()


        # Pull out the points for this frame (This function should filter any obviously erroneous points)
        # The points that this function pulls out or filters will be specific to each use case and this function
        # should therefore be rewritten on a case by case basis.
        # Add the filtered points to the list of filtered frame points.
        points = filter_frame_points(dataframe, row)
        filteredPoints.append(points)


        # Pass the points generated in above step to ghostly trail functions
        # Toggle PAINT_GHOST_TRAILS global to turn this on or off.
        if(PAINT_GHOST_TRAILS):
            update_ghost_trail_point_lists(ghostTrailPoints, points)
            paint_ghost_trails(ghostTrailPoints, frame, overlay)


    # TODO: Parse reaching event frame ranges
    # Now that frame data has been filtered, process the frame data to
    # generate a list of "reaching events". Each event should contain:
    #
    # - Start frame index of event
    # - Stop frame index of event
    events = []


    # TODO: For each event generated in the above step, perform kinematic analysis.
    for event in events:

        # Generate x,y,z of trajectory reconstruction by analyzing the (Y,Z) pixel coordinates of left mirror
        # and right mirror, and the (X,Y) coordinates of center view.
        x, y, z = gen_trajectory_reconsutrction_xyz(event)

        # Use calibration constants to transform pixel coordinates into real-world coordinates.
        x, y, z = convert_pixelCoord_to_realWorld(x, y, z)

        # Spawn a graph displaying reconstruction
        spawn_3D_graph(np.asarray(x), np.asarray(y), np.asarray(z))

        # TODO: Save (x,y,z), graph .png, DLC data + video frames for the range of frames covered by event.




if __name__ == "__main__":
    main()
