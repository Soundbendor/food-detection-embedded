#!../venv/bin/python

"""
Will Richards, Oregon State University, 2023

Detection Loop for all Binsight Devices

Records data when the lid is opened and then closed and once every 2 hours
"""

import time
import logging
import os
import sys
import json
import logging
from multiprocessing import Event

#from drivers.ThreadedDriver import ThreadedDriver
from drivers.DriverManager import DriverManager

# Sensor Drivers
from drivers.sensors.NAU7802 import NAU7802
from drivers.sensors.RealsenseCamera import RealsenseCam
from drivers.sensors.BME688 import BME688
from drivers.sensors.MLX90640 import MLX90640
from drivers.sensors.LidSwitch import LidSwitch

from helpers import TimeHelper, Logging



"""
Load sensor calibration details from a given file 

:param file: Path to the file we want to load the credentials from

:return: Return a JSON dictionary of the sensor calibration details 
"""
def loadCalibrationDetails(file: str) -> dict:
    logging.info(f"Retrieving calibration details from file: {file}")

    # Attempt to open the file and convert the contents to JSON object
    with open(file, "r") as f:
        data = json.load(f)
        logging.info("Succsessfully loaded calibration details!")
        return data
   

"""
Collect a sample from all of the sensors on the device

:param manager: Takes the DriverManager as a paramter so we can request events and what not
"""
def collectData(manager: DriverManager) -> bool:
    # We want to tell the "cameras" we would like to capture the latest frames
    manager.setEvent("Realsense.CAPTURE")
    manager.setEvent("MLX90640.CAPTURE")

    # While the capture events are still set we should just wait until they are cleared meaning they succeeded
    while manager.getEvent("Realsense.CAPTURE") and manager.getEvent("MLX90640.CAPTURE"):
        time.sleep(0.01)
    

"""
Called when the hall-effect sensor transitions from an open state to a closed one
"""
def lidClosed(event: Event, manager: DriverManager):
    logging.info("Lid closed! Collecting sample...")
    collectData(manager)
    event.clear()
    

def main():
    logger = Logging()
    # Read calibration details as JSON into the file to allow device to be powered on and off without needing to recalibrate 
    calibrationDetails = loadCalibrationDetails("CalibrationDetails.json")
    
    # Create a manager device passing the NAU7802 in as well as a generic TestDriver that just adds two numbers 
    manager = DriverManager(NAU7802(calibrationDetails["NAU7802_CALIBRATION_FACTOR"]), BME688(), MLX90640(), LidSwitch(), RealsenseCam())
    timeHelper = TimeHelper()

    # Register a callback for when the lid is closed so we can sample our data
    manager.registerEventCallback("LidSwitch.LID_CLOSED", lambda event: lidClosed(event, manager))
    
    while(True):
        try:
            manager.loop()
            if timeHelper.twoHourInterval():
                collectData(manager)

            time.sleep(0.001)
           
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            manager.kill()
            break

if __name__ == "__main__":
    main()
