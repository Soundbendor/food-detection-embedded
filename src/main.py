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
import logging
from multiprocessing import Event

#from drivers.ThreadedDriver import ThreadedDriver
from drivers.DriverManager import DriverManager

# Sensor Drivers
from drivers.sensors.NAU7802 import NAU7802
from drivers.sensors.IMX219 import IMX219
from drivers.sensors.BME688 import BME688
from drivers.sensors.MLX90640 import MLX90640
from drivers.sensors.LidSwitch import LidSwitch

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
def configureLogging():
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
def bucketWeightChanged(event: Event):
    logging.info("WEIGHT CHANGED!!!!!")
    event.clear()

def lidOpened(event: Event):
    logging.info("Lid opened!")
    event.clear()

def lidClosed(event: Event):
    logging.info("Lid closed!")
    event.clear()
    

def main():
    # Read calibration details as JSON into the file to allow device to be powered on and off without needing to recalibrate 
    calibrationDetails = loadCalibrationDetails("CalibrationDetails.json")
    
    # Create a manager device passing the NAU7802 in as well as a generic TestDriver that just adds two numbers 
    manager = DriverManager(NAU7802(calibrationDetails["NAU7802_CALIBRATION_FACTOR"]), BME688(), MLX90640(), LidSwitch(), IMX219())
    #manager = DriverManager(IMX219())
    #steroCam = IMX219()
    #manager = DriverManager(BME688())
    #manager = DriverManager(MLX90640())
    #manager = DriverManager(LidSwitch())

    # Register a callback for a weight change on the NAU7802
    #manager.registerEventCallback("NAU7802.WEIGHT_CHANGE", bucketWeightChanged)
    #manager.registerEventCallback("LidSwitch.LID_OPENED", lidOpened)
    #manager.registerEventCallback("LidSwitch.LID_CLOSED", lidClosed)
    #manager.setEvent("MLX90640.Capture")

    bmeCap = lambda: manager.setEvent("BME688.CAPTURE")
    imxCap = lambda: manager.setEvent("IMX219.CAPTURE")
    
    while(True):
        try:
            manager.loop()
            #manager.triggerEvery(1, "displayData", manager.displayData)
            manager.triggerEvery(1, "bmeCapture", lambda: manager.setEvent("BME688.CAPTURE"))
            manager.triggerEvery(10, "imxCapture", lambda: manager.setEvent("IMX219.CAPTURE"))
            manager.triggerEvery(5, "mlxCapture", lambda: manager.setEvent("MLX90640.CAPTURE"))
            
            time.sleep(0.001)
           

        
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            manager.kill()
            break

if __name__ == "__main__":
    configureLogging()
    main()
