""""
Will Richards, Oregon State University, 2023

Abstraction layer for the IMX219 steroscopic imaging camera
"""

from nanocamera import Camera
import cv2
import logging
from multiprocessing import Event
from time import sleep

from drivers.DriverBase import DriverBase

from enum import Enum

# Enum to map CAMERA_SIDES to IDs
class CAMERA_SIDE(Enum):
    LEFT_CAMERA = 0
    RIGHT_CAMERA = 1

class IMX219(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self, debug=False):
        super().__init__("IMX219", 1)
        """
        Left Camera ID - 0
        Right Camera ID - 1
        """
        self.cameras: list[Camera] = []
        self.debugMode = debug

        # We shouldn't always measure
        self.shouldMeasure = False

        # List of events to hold, the SHOULD_CAPTURE event 
        self.events = {
            "SHOULD_CAPTURE" : Event()
        }
        
    def initialize(self):
        # Add both camears into the list of cameras

        gstream_str = "nvarguscamerasrc sensor-id=0 ! 'video/x-raw(memory:NVMM), width=1920, height=1080, format=(string)NV12, framerate=(fraction)30/1' ! nvvidconv flip-method=0 ! 'video/x-raw, width=(int)1920, height=(int)1080, format=(string)BGRx' ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"
        cap = cv2.VideoCapture(gstream_str, cv2.CAP_GSTREAMER)
        
        ret, frame = cap.read()
        print(ret)
            
        #cv2.imwrite("test.jpg", frame)
        #cap.release()
        
        """ 
        self.cameras.append(Camera(device_id=CAMERA_SIDE.LEFT_CAMERA.value, flip = 0, width = 1280, height = 720, fps = 120, debug = self.debugMode))
        #self.cameras.append(Camera(device_id=CAMERA_SIDE.RIGHT_CAMERA.value, flip = 0, width = 1920, height = 1080, fps = 5, debug = self.debugMode))

        for camera in self.cameras:
            if(camera.isReady() != True):
                camName = CAMERA_SIDE(camera.camera_id).name
                logging.error(f"{camName} setup failed, see error code below...")
                
                # Get the cameara error
                code, has_err = camera.hasError()
                if(has_err):
                    logging.error(f"{camName} failed with error: {code}")
        """

    def measure(self) -> list:
        return []
    

        