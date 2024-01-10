#!../venv/bin/python
"""
Take in a video stream and convert it to stereo images on the output

Per this video: https://www.youtube.com/watch?v=yKypaVl6qQo
Author(s): Will Richards, Oregon State 2023
"""

import cv2
import numpy as np

#leftCap = cv2.VideoCapture("nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=0 ! video/x-raw, width=640, height=480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv2.CAP_GSTREAMER)
#rightCap = cv2.VideoCapture("nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=0 ! video/x-raw, width=640, height=480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv2.CAP_GSTREAMER)

ndisparities = 16*5
SADWindowSize = 21
stereo = cv2.StereoSGBM.create(ndisparities, 23*2 + 5)

cv_file = cv2.FileStorage("stereoMap.xml", cv2.FILE_STORAGE_READ)

leftMapX = cv_file.getNode('stereoMapL_x').mat()
leftMapY = cv_file.getNode('stereoMapL_y').mat()
rightMapX = cv_file.getNode('stereoMapR_x').mat()
rightMapY = cv_file.getNode('stereoMapR_y').mat()

cv_file.release()

# stereo.setNumDisparities(16*6)
# stereo.setBlockSize(23*2 + 5)
# # stereo.setPreFilterType(0)
# # stereo.setPreFilterSize(5*2 + 5)
# stereo.setPreFilterCap(30)
# # stereo.setTextureThreshold(33)
# stereo.setUniquenessRatio(1)
# stereo.setSpeckleRange(80)
# stereo.setSpeckleWindowSize(5*2)
# stereo.setDisp12MaxDiff(8)
# stereo.setMinDisparity(5)

leftCap = cv2.imread("leftImage.png")
rightCap = cv2.imread("rightImage.png")

disparity = stereo.compute(leftCap, rightCap)

cv2.imwrite(f"leftImage{0}.jpg", leftCap)
cv2.imwrite(f"rightImage{0}.jpg", rightCap)
cv2.imwrite(f"disparityImage{0}.jpg", disparity)

num = 0
# while leftCap.isOpened() and rightCap.isOpened():
#     try:
#         if leftCap.grab() and rightCap.grab():
#             _, leftFrame = leftCap.retrieve()
#             _, rightFrame = rightCap.retrieve()

#             # Convert to grayscale
#             leftFrame = cv2.cvtColor(leftFrame, cv2.COLOR_RGB2GRAY)
#             rightFrame = cv2.cvtColor(rightFrame, cv2.COLOR_RGB2GRAY)

#             leftFrame = cv2.remap(leftFrame, leftMapX, leftMapY, cv2.INTER_LINEAR)
#             rightFrame = cv2.remap(rightFrame, rightMapX, rightMapY, cv2.INTER_LINEAR)
            
#             disparity = stereo.compute(leftFrame, rightFrame)
            
#             cv2.imwrite(f"leftImage{num}.jpg", leftFrame)
#             cv2.imwrite(f"rightImage{num}.jpg", rightFrame)
#             cv2.imwrite(f"disparityImage{num}.jpg", disparity)
            
#     except KeyboardInterrupt:
#         leftCap.release()
#         rightCap.release()
#         break