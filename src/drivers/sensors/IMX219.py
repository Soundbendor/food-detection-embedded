""""
Will Richards, Oregon State University, 2023

Abstraction layer for the IMX219 steroscopic imaging camera
"""

import cv2
import numpy
import logging
from multiprocessing import Event
from time import sleep

from drivers.DriverBase import DriverBase

from enum import Enum

class IMX219(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self):
        super().__init__("IMX219")

        # Set loop time to be equivelent to 30 fps
        self.loopTime = 1/60
        self.cameras: list[cv2.VideoCapture] = []

        # List of events to hold, the SHOULD_CAPTURE event 
        self.events = {
            "CAPTURE" : Event()
        }
        
    def initialize(self):
        """
        Create a list of both cameras we are using

        Left Camera ID - 0
        Right Camera ID - 1
        """
        self.cameras.append(self.__createCamera(0))
        self.cameras.append(self.__createCamera(1))
    
        # Check if both camera streams are openable
        self.initialized = False
        for cam in self.cameras:
            self.initialized = cam.isOpened()
        
        if self.initialized:
            logging.info("Cameras successfully initialized!")

    def writeFrames(self, leftFrame, rightFrame, steroFrame):
        try:
            cv2.imwrite("left.jpg", leftFrame)
            cv2.imwrite("right.jpg", rightFrame)
            cv2.imwrite("stereo.jpg", steroFrame)
            logging.info("Images saved succsessfully!")
        except:
            logging.error("Failed to save image(s)!")
    
    """
    Request that each cameara grab the "current" frame
    """
    def _poll(self):
        if self.initialized:
            for cam in self.cameras:
                cam.grab()

    """
    Measure the camera, effectively update the current frame to the latest and then check if a capture event was set to see if we should save the current frame
    """
    def measure(self) -> None:

        # Keep the camera updated
        self._poll()

        # If a capture event was triggered we want to save the current frames including the stero image
        if(self.getEvent("CAPTURE").is_set()):
            leftFrame, rightFrame, stereoFrame = self.capture()
            self.writeFrames(leftFrame, rightFrame, stereoFrame)
            self.getEvent("CAPTURE").clear()
            logging.info("Succsessfully captured image")
    
    """
    Retrieve the waiting frames from the camera and generate a stereo image from the left and rightFrames
    """
    def capture(self) -> tuple:
        if self.initialized:
            # Retrieve waiting frames from the cameras
            _, leftFrame = self.cameras[0].retrieve()
            _, rightFrame = self.cameras[1].retrieve()

            # Create stero image from the two frames
            stereo = cv2.StereoSGBM.create(numDisparities=64, blockSize=15)
            completeFrame = stereo.compute(leftFrame, rightFrame)

            return (leftFrame, rightFrame, completeFrame)

        else:
            logging.error("Depth camera not initialized!")
            return (0, 0, 0)

    """
    Release VideoCaptures on shutdown
    """
    def kill(self):
        for cam in self.cameras:
            cam.release()

    def createDataDict(self):
        return {}

    """
    Create a new camera with a specified device ID
    """
    def __createCamera(self, device_id):
        width = 1280
        height = 720
        fps = 60
        return cv2.VideoCapture(f"nvarguscamerasrc sensor-id={device_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction){fps}/1 ! nvvidconv flip-method=0 ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")