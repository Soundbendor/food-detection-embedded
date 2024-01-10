#!../venv/bin/python
"""
Take in a video stream and convert it to stereo images on the output

Per this video: https://www.youtube.com/watch?v=yKypaVl6qQo
Author(s): Will Richards, Oregon State 2023
"""

import cv2
import numpy as np
from time import sleep

leftCap = cv2.VideoCapture("nvarguscamerasrc sensor-id=0 ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=0 ! video/x-raw, width=640, height=480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv2.CAP_GSTREAMER)
rightCap = cv2.VideoCapture("nvarguscamerasrc sensor-id=1 ! video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=0 ! video/x-raw, width=640, height=480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink", cv2.CAP_GSTREAMER)

num = 0
while leftCap.isOpened() and rightCap.isOpened():
    try:
        if leftCap.grab() and rightCap.grab():
            _, leftFrame = leftCap.retrieve()
            _, rightFrame = rightCap.retrieve()
        
            cv2.imwrite(f"images/leftCalibrationImages/leftImage{num}.jpg", leftFrame)
            cv2.imwrite(f"images/rightCalibrationImages/rightImage{num}.jpg", rightFrame)

            num += 1
        sleep(1/30)
    except KeyboardInterrupt:
        break