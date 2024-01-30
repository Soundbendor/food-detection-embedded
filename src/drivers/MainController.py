"""
Will Richards, Oregon State University, 2024

Provides the top level of the whole system so individual components can be utilized individually without needing to give them their own thread via the DriverManager
"""

import multiprocessing
import time
import os

from drivers.DriverManager import DriverManager

# Sensor Drivers
from drivers.sensors.NAU7802 import NAU7802
from drivers.sensors.RealsenseCamera import RealsenseCam
from drivers.sensors.BME688 import BME688
from drivers.sensors.MLX90640 import MLX90640
from drivers.sensors.LidSwitch import LidSwitch
from drivers.sensors.LEDDriver import LEDDriver
from drivers.sensors.SoundController import SoundController

# Additional Helper Methods
from helpers import Logging, CalibrationLoader, RequestHandler


class MainController():

    """
    Create a new instance of our main controlller
    """
    def __init__(self) -> None:
        logger = Logging(__file__, verbose=True)
        calibration = CalibrationLoader("CalibrationDetails.json")
        self.requests = RequestHandler()
 
        if not os.path.exists("../data/"):
            os.mkdir("../data/")

        # Create a manager device passing the NAU7802 in as well as a generic TestDriver that just adds two numbers
        self.mainControllerConnection, soundControllerConnection = multiprocessing.Pipe()
        self.manager = DriverManager(LEDDriver(), NAU7802(calibration.get("NAU7802_CALIBRATION_FACTOR")), BME688(), MLX90640(), LidSwitch(), RealsenseCam(), SoundController(soundControllerConnection))
        
        # After we have initialzied all the proccesses we want to flash green to signifiy we are done
        if self.manager.allProcsInitialized:
            self.manager.setEvent("LEDDriver.DONE")
            time.sleep(2)
            self.manager.setEvent("LEDDriver.NONE")
        else:
            self.manager.setEvent("LEDDriver.ERROR")
            time.sleep(2)
            self.manager.setEvent("LEDDriver.NONE")


    """
    Handles events that need to be checked quickly in the main loop
    """
    def handleCallbacks(self):
        # Check the state of the LidSwitch
        if(self.manager.getEvent("LidSwitch.LID_CLOSED")):
            self.collectData(triggeredByLid=True)
            self.manager.clearEvent("LidSwitch.LID_CLOSED")
  

    """
    Collect a sample from all of the sensors on the device

    :param triggeredByLid: Whether or not our current sample was triggered by the lid opening or just the "cron job"
    """
    def collectData(self, triggeredByLid=True) -> bool:
        # We want to tell the "cameras" we would like to capture the latest frames
        self.manager.setEvent("LEDDriver.CAMERA")
        self.manager.setEvent("Realsense.CAPTURE")
        self.manager.setEvent("MLX90640.CAPTURE")
        

        # While the capture events are still set we should just wait until they are cleared meaning they succeeded
        while self.manager.getEvent("Realsense.CAPTURE") or self.manager.getEvent("MLX90640.CAPTURE"):
            time.sleep(0.2)

        # Set the light to yellow before recording the 
        self.manager.setEvent("LEDDriver.PROCESSING")

        # If we actaully want to prompt for entry or it is part of the "cron job"
        if(triggeredByLid):
            self.manager.setEvent("SoundController.RECORD")
            while self.manager.getEvent("SoundController.RECORD"):
                time.sleep(0.2)
            
            # Add the transcribed text into the JSON document, only update if value was returned
            transcription = self.mainControllerConnection.recv()
            if len(transcription) > 1:
                self.manager.getData()["SoundController"]["data"]["TranscribedText"] = transcription

        print(self.manager.getJSON())

        # Upload the current files in our data folder to S3 and send the API request
        self.requests.sendAPIRequest(self.manager.getJSON())

        # After we have sent all the stuff and are done, set the leds to green for a few seconds and then turn them off
        self.manager.setEvent("LEDDriver.DONE")
        time.sleep(2)
        self.manager.setEvent("LEDDriver.NONE")

    """
    Shutdown device connected via the DriverManager
    """
    def kill(self):
        self.manager.kill()