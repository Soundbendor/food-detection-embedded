#!../venv/bin/python
"""
Auxilary code to take the collected images generated from teh previous script and calculate the calibration parameters

Per this video: https://www.youtube.com/watch?v=yKypaVl6qQo
Author(s): Will Richards, Oregon State 2023
"""

import numpy as np
import cv2 
import glob

############################### FIND THE CHESSBOARD CORNERS - OBJECT POINTS AND IMAGE POINTS ###############################

# These numbers are the total squares ignoring the one in the far corners 
chessboardSize = (9,6)
frameSize = (1920,1080)

# termination criteria
criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 30, 0.001)

objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)

objp = objp * 20
print(objp)

# Arrays to store object points and image points for all the images
objpoints = []
imgpointsL = []
imgpointsR = []

imagesLeft = glob.glob("images/leftCalibrationImages/*.png")
imagesRight = glob.glob("images/rightCalibrationImages/*.png")

num = 0

# Load each image in and convert to grayscale
for imgLeft, imgRight in zip(imagesLeft, imagesRight):
    print(f"Loading image {num}")
    imgL = cv2.imread(imgLeft)
    imgR = cv2.imread(imgRight)
    grayL = cv2.cvtColor(imgL, cv2.COLOR_BGR2GRAY)
    grayR = cv2.cvtColor(imgR, cv2.COLOR_BGR2GRAY)

    # Find corners for left and right images
    retL, cornersL = cv2.findChessboardCorners(grayL, chessboardSize, None)
    retR, cornersR = cv2.findChessboardCorners(grayR, chessboardSize, None)

    # If we found corners in both images we want to add this obj to the list
    if retL and retR:
        objpoints.append(objp)

        # Refine the accuracy of the chessboard corners
        cornersL = cv2.cornerSubPix(grayL, cornersL, (11,11), (-1,-1), criteria)
        imgpointsL.append(cornersL)

        cornersR = cv2.cornerSubPix(grayR, cornersR, (11,11), (-1,-1), criteria)
        imgpointsR.append(cornersR)

        cv2.drawChessboardCorners(imgL, chessboardSize, cornersL, retL)
        cv2.imwrite("images/leftWithCorners/ImageL" + str(num) + ".png", imgL) 
        cv2.drawChessboardCorners(imgR, chessboardSize, cornersR, retR)
        cv2.imwrite("images/leftWithCorners/ImageR" + str(num) + ".png", imgR) 
    num += 1

