""""
Will Richards, Oregon State University, 2023

Abstraction layer for the IMX219 steroscopic imaging camera
"""

import pyrealsense2 as rs
import cv2
import numpy as np
import logging
from multiprocessing import Event
from drivers.DriverBase import DriverBase
from time import time, gmtime, strftime


class RealsenseCam(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self, width = 640, height = 480, fps = 30):
        super().__init__("Realsense")

        # Set loop time to be 0 because it will block automatically
        self.loopTime = 0.15
        self.framerate = fps
        self.camera_width = width
        self.camera_height = height

        # Realsense paramters
        self.realsense_pipeline = rs.pipeline()
        self.realsense_config = rs.config()
        self.realsense_colorizer = rs.colorizer()

        # Polygon Output Parameters
        self.realsense_ply = rs.save_to_ply("../data/depth.ply")
        self.realsense_ply.set_option(rs.save_to_ply.option_ply_binary, True)
        self.realsense_ply.set_option(rs.save_to_ply.option_ply_normals, True)
        

        # List of events to hold
        self.events = {
            "CAPTURE" : Event()
        }
    

    """
    Initialize our realsense camera streams for both color and depth
    """
    def initialize(self):
        self.realsense_config.enable_stream(rs.stream.color, self.camera_width, self.camera_height, rs.format.bgr8, self.framerate)
        self.realsense_config.enable_stream(rs.stream.depth, self.camera_width, self.camera_height, rs.format.z16, self.framerate)

        try:
            self.realsense_pipeline.start(self.realsense_config)
        except RuntimeError as e:
            logging.error(f"An Error occurred: {e}")
            self.initialized = False

        if self.initialized:
            logging.info("Successfully initialized realsense camera!")

    """
    Check if the CAPTURE event was triggered this cycle and if so we want to collect our depthImage, colorImage and .ply depth file
    """
    def measure(self) -> None:

        # If a capture event was triggered we want to grab the current frames from the camera
        if(self.getEvent("CAPTURE").is_set()):

            # If the device didn't initialize we want to clear the capture so we don't hang forever
            if not self.initialized:
                self.getEvent("CAPTURE").clear()
                return
            
            # Attempt to retrive the most recent frame from the realsense camera
            capSuccsess, frames = self.realsense_pipeline.try_wait_for_frames()

            if capSuccsess:

                # Actually pull the frames out of our wait attempt and verify they are valid
                depth_frame = frames.get_depth_frame()
                color_frame = frames.get_color_frame()
                if depth_frame and color_frame:

                    # Convert our images into array's and colorize the depth map
                    colorized = self.realsense_colorizer.process(frames)
                    depth_image = np.asanyarray(depth_frame.get_data())
                    color_image = np.asanyarray(color_frame.get_data())
                    depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)

                    # Generate our .ply file and save our images to the disk
                    self.realsense_ply.process(colorized)
                    cv2.imwrite("../data/depthImage.jpg", depth_colormap)
                    cv2.imwrite("../data/colorImage.jpg", color_image)


                    # Only clear capture event on successful retrieval
                    self.getEvent("CAPTURE").clear()
                    logging.info("Captured frames successfully!")
                else:
                    logging.warn("Unable to retrieve frame(s)")
                    
            else:
                logging.error("Failed to retrieve last frame")

    
    """
    Release RealSense pipeline on shutdown
    """
    def kill(self):
        try:
            self.realsense_pipeline.stop()
        except RuntimeError as e:
            logging.error(f"An error occurred: {e}")