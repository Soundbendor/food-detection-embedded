#!../venv/bin/python

"""
Will Richards, Add Other Names, Oregon State University, 2023

Main runner module for the entire system all code should 
"""
import time
import logging
import os
import sys
import json

from logging import config
from multiprocessing import Event

#from drivers.ThreadedDriver import ThreadedDriver
from drivers.DriverManager import DriverManager

# Sensor Drivers
from drivers.sensors.NAU7802 import NAU7802
from drivers.sensors.TestDriver import TestDriver
from drivers.sensors.IMX219 import IMX219

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
Configure logging format and output type based on arguments passed to the program
"""
def configureLogging() -> None:
    FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'

    # Check if we want to specifiy an output file for the loging
    if(len(sys.argv) < 2):
        logging.basicConfig(format=FORMAT, level=logging.INFO)
        logging.info("No output file specified file logging will be disabled to enable: ./main.py <outputfilepath>")
    else:
        logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler(str(os.path.dirname(os.path.abspath(__file__))) + "/" + sys.argv[1]), logging.StreamHandler()])

"""
Callback for when the weight of the bucket has changed

:param event: The event that caused this callback
"""
def bucketWeightChanged(event):
    logging.info("WEIGHT CHANGED!!!!!")
    event.clear()

def main():
    # Read calibration details as JSON into the file to allow device to be powered on and off without needing to recalibrate 
    calibrationDetails = loadCalibrationDetails("CalibrationDetails.json")
    
    # Create a manager device passing the NAU7802 in as well as a generic TestDriver that just adds two numbers 
    #manager = DriverManager(NAU7802(calibrationDetails["NAU7802_CALIBRATION_FACTOR"]), TestDriver("Test1"))
    manager = DriverManager(IMX219(True))

    # Register a callback for a weight change on the NAU7802
    #manager.registerEventCallback("NAU7802.WEIGHT_CHANGE", bucketWeightChanged)
    i = 0
    while(True):
        try:
        
            manager.loop()
            if(i == 100):
                #print(json.dumps(manager.getJSON(), indent=4))
                i = 0
            time.sleep(0.001)
            i += 1

        
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            manager.kill()
            break

if __name__ == "__main__":
    configureLogging()
    main()
