#!../venv/bin/python

"""
Will Richards, Add Other Names, Oregon State University, 2023

Main runner module for the entire system all code should 
"""

from logging import config

#from drivers.ThreadedDriver import ThreadedDriver
from drivers.DriverManager import DriverManager

from drivers.NAU7802 import NAU7802

from multiprocessing import Event

from time import sleep
import logging
import os
import sys
import json

"""
Load sensor calibration details from a given file 

:param file: Path to the file we want to load the credentials from
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

def main():
    # Read calibration details as JSON into the file to allow device to be powered on and off without needing to recalibrate 
    calibrationDetails = loadCalibrationDetails("CalibrationDetails.json")
    
    manager = DriverManager(NAU7802())

    while(True):
        try:
           
            sleep(0.01)  
        
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            break
    """
    # Create and start a new "threaded" instance of the NAU7802
    weightEvent = Event()
    
    driver = ThreadedDriver(NAU7802(weightChangeEvent=weightEvent, calibration_factor=calibrationDetails["NAU7802_Calibration_Factor"]))
    driver.start()

    while(True):
        try:
            # Check if the weight changed on this pass through
            if(weightEvent.is_set()):
                print("WEIGHT CHANGED!!!")
                weightEvent.clear()
            
            sleep(0.01)  
        
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            driver.kill()
            break
    """

if __name__ == "__main__":
    configureLogging()
    main()
