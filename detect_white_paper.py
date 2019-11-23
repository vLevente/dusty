# import the necessary packages
from imutils import paths
import numpy as np
import imutils
import cv2
from imutils.video import VideoStream
import time
import matplotlib.pyplot as plt


def find_marker(image):
    # convert the image to grayscale, blur it, and detect edges
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)
    gray = cv2.bilateralFilter(gray, 7, 50, 50)
    edged = cv2.Canny(gray, 35, 125)

    # find the contours in the edged image and keep the largest one;
    # we'll assume that this is our piece of paper in the image
    cnts = cv2.findContours(edged.copy(), cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    c = max(cnts, key=cv2.contourArea)

    # compute the bounding box of the of the paper region and return it
    return cv2.minAreaRect(c)


def distance_to_camera(knownWidth, focalLength, perWidth):
    # compute and return the distance from the maker to the camera
    return (knownWidth * focalLength) / perWidth


KNOWN_DISTANCE = 119.0

KNOWN_WIDTH = 30

image = cv2.imread("test.jpg")
marker = find_marker(image)
focalLength = (marker[1][0] * KNOWN_DISTANCE) / KNOWN_WIDTH

test_pix = marker[1][0]
test_width = 30
px = test_width / test_pix  #1 pixel hany cm


pix = KNOWN_WIDTH/marker[1][0]
# loop over the images

# load the image, find the marker in the image, then compute the
# distance to the marker from the camera
vs = VideoStream(usePiCamera=True).start()
time.sleep(1.0)
cap = cv2.VideoCapture(0)

while True:
    start = time.time()
    frame = vs.read()
    time.sleep(.1)
    image = frame  # cv2.imread(frame)
    marker = find_marker(image)
    distance = distance_to_camera(KNOWN_WIDTH, focalLength, marker[1][0])

    # draw a bounding box around the image and display it
    box = cv2.cv.BoxPoints(marker) if imutils.is_cv2() else cv2.boxPoints(marker)
    box = np.int0(box)

    cX = int(np.average(box[:, 0]))
    cY = int(np.average(box[:, 1]))
    cv2.circle(image, (cX, cY), 20, (0, 255, 0), -1)
    # print("paper's centre: ", cX, " ", cY)

    iX = int(image.shape[1] / 2)
    iY = int(image.shape[0] / 2)
    cv2.circle(image, (int(iX), int(iY)), 20, (0, 255, 0), -1)
    # print("image's centre: ", iX, " ", iY)

    dx = iX - cX
    dy = iY - cY
    centre_dist_px = (dx, dy)
    print("dist_in_px: ", centre_dist_px)

    centre_dist = dx * px
    print("dist_in_cm: ", centre_dist)
    cv2.drawContours(image, [box], -1, (0, 255, 0), 2)
    cv2.putText(image, "%.1fcm" % (distance / 10),
                (image.shape[1] - 120, image.shape[0] - 15), cv2.FONT_HERSHEY_SIMPLEX,
                1.0, (0, 255, 0), 2)
    print("distance: ", distance/10)
    #cv2.imshow("image", image)
    key = cv2.waitKey(1) & 0xFF
    #print(inches/10, " cm")
    # if the `q` key was pressed, break from the loop
    if key == ord("q"):
        break
    stop = time.time()
    fps = 1/(stop-start)
    # print(fps)