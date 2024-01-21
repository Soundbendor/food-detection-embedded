"""
Will Richards, Oregon State University, 2024

Provides the top level of the whole system so individual components can be utilized individually without needing to give them their own thread via the DriverManager
"""

import time

from drivers.DriverManager import DriverManager

# Sensor Drivers
from drivers.sensors.NAU7802 import NAU7802
from drivers.sensors.RealsenseCamera import RealsenseCam
from drivers.sensors.BME688 import BME688
from drivers.sensors.MLX90640 import MLX90640
from drivers.sensors.LidSwitch import LidSwitch

# Additional Helper Methods
from helpers import Logging, CalibrationLoader


class MainController():
    def __init__(self) -> None:
        logger = Logging(__file__)
        calibration = CalibrationLoader("CalibrationDetails.json")

        # Create a manager device passing the NAU7802 in as well as a generic TestDriver that just adds two numbers 
        self.manager = DriverManager(NAU7802(calibration.get("NAU7802_CALIBRATION_FACTOR")), BME688(), MLX90640(), LidSwitch(), RealsenseCam())

    """
    Handles events that need to be checked quickly in the main loop
    """
    def handleCallbacks(self):
        # Check the state of the LidSwitch
        if(self.manager.getEvent("LidSwitch.LID_CLOSED")):
            self.collectData()
            self.manager.clearEvent("LidSwitch.LID_CLOSED")

    """
    Collect a sample from all of the sensors on the device

    :param manager: Takes the DriverManager as a paramter so we can request events and what not
    """
    def collectData(self) -> bool:
        # We want to tell the "cameras" we would like to capture the latest frames
        self.manager.setEvent("Realsense.CAPTURE")
        self.manager.setEvent("MLX90640.CAPTURE")

        # While the capture events are still set we should just wait until they are cleared meaning they succeeded
        while self.manager.getEvent("Realsense.CAPTURE") and self.manager.getEvent("MLX90640.CAPTURE"):
            time.sleep(0.01)

        print(self.manager.getJSON())

    
    def kill(self):
        self.manager.kill()