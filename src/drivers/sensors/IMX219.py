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
        
        """
        Create a list of both cameras we are using

        Left Camera ID - 0
        Right Camera ID - 1
        """
        self.cameras: list[cv2.VideoCapture] = [
            self.__createCamera(0),
            self.__createCamera(1),
        ]

        # List of events to hold, the SHOULD_CAPTURE event 
        self.events = {
            "SHOULD_CAPTURE" : Event()
        }
        
    def initialize(self):
        
        # Check if both camera streams are openable
        self.initialized = False
        for cam in self.cameras:
            self.initialized = cam.isOpened()
        
        if self.initialized:
            logging.info("Cameras successfully initialized!")

        self.capture()
        

    def measure(self) -> None:
        pass
    
    def capture(self):
        if self.initialized:
            # Read and save the image 
            for cam in self.cameras:
                cam.grab()

            _, leftFrame = self.cameras[0].retrieve()
            _, rightFrame = self.cameras[1].retrieve()

            stereo = cv2.StereoSGBM.create(numDisparities=64, blockSize=15)
            completeFrame = stereo.compute(leftFrame, rightFrame)
            cv2.imwrite("stereo.jpg", completeFrame)
            cv2.imwrite("left.jpg", leftFrame)
            cv2.imwrite("right.jpg", rightFrame)

        else:
            logging.error("Depth camera not initialized!")

    """
    Release VideoCaptures on shutdown
    """
    def kill(self):
        for cam in self.cameras:
            cam.release()

    def createDataDict(self):
        return {}

    def __createCamera(self, device_id):
        width = 3264
        height = 1848
        return cv2.VideoCapture(f"nvarguscamerasrc sensor-id={device_id} ! video/x-raw(memory:NVMM), width=(int){width}, height=(int){height}, format=(string)NV12, framerate=(fraction)21/1 ! nvvidconv flip-method=0 ! video/x-raw, width=(int){width}, height=(int){height}, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink")