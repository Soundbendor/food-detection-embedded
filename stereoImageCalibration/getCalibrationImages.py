#!../venv/bin/python

"""
Tool to capture and store images for stereo imaging calibration

Will Richards, Oregon State 2024
"""


import cv2
import os
import shutil
from time import sleep

# If we only want to take one test image
ONLY_ONE = True

# Given an ID create a new pipeline for that VideoCapture object
def createPipeline(id):
    return f"nvarguscamerasrc sensor-id={id} sensor-mode=3 ! video/x-raw(memory:NVMM), width=(int)1640, height=(int)1232, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"

# Create or clear data in prexisting calibration image folders
def createDataFolders():
    # If we dont have an images directory in our current folder make one
    if not os.path.isdir("images"):
        os.mkdir("images")
        os.mkdir("images/leftCalibrationImages")
        os.mkdir("images/rightCalibrationImages")
    else:
        # Remove and remake them
        shutil.rmtree("images/leftCalibrationImages")
        shutil.rmtree("images/rightCalibrationImages")
        os.mkdir("images/leftCalibrationImages")
        os.mkdir("images/rightCalibrationImages")

def warmUpCaptures(leftCap: cv2.VideoCapture, rightCap: cv2.VideoCapture):
    for i in range(30):
        leftCap.grab()
        rightCap.grab()

def main():
    leftCap = cv2.VideoCapture(createPipeline(0), cv2.CAP_GSTREAMER)
    rightCap = cv2.VideoCapture(createPipeline(1), cv2.CAP_GSTREAMER)

    input("Procceeding will remove any previously collected calibration images. Would you like to continue? (press enter)")
    print("Captures starting in 2 seconds...")
    sleep(2)
    warmUpCaptures(leftCap, rightCap)

    createDataFolders()

    # Once both captures are opened 
    captureNumber = 0
    if leftCap.isOpened() and rightCap.isOpened():
        for i in range(30):
            try:
                leftCaptureSuccsess = leftCap.grab()
                rightCaptureSuccsess = rightCap.grab()

                if leftCaptureSuccsess and rightCaptureSuccsess:
                    _, leftFrame = leftCap.retrieve()
                    _, rightFrame = rightCap.retrieve()

                    cv2.imwrite(f"images/leftCalibrationImages/leftImage{captureNumber}.jpg", leftFrame)
                    cv2.imwrite(f"images/rightCalibrationImages/rightImage{captureNumber}.jpg", rightFrame)
                    print(f"Captured image {i+1}...")
                    captureNumber += 1
                    if ONLY_ONE:
                        break
                sleep(1/30) 
            except KeyboardInterrupt:
                leftCap.release()
                rightCap.release()
                print("Ctrl + C detected! Exiting...")
                break
    else:
        print("Failed to open one or both video capture devices! Exiting...")
    leftCap.release()
    rightCap.release()

if __name__ == "__main__":
    main()