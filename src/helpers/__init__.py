from time import time
import logging
import sys
import os
import json

TWO_HOURS_SECONDS = 7200

class TimeHelper():
    def __init__(self):
        self.lastTime = time()
    
    """
    Check to see if we have reached the two hour interval and should trigger the collection

    :return A bool representing if our 2 hour interval is up
    """
    def twoHourInterval(self) -> bool:
        currentTime = int(time())
        if (currentTime % TWO_HOURS_SECONDS) == 0 and currentTime != self.lastTime:
            self.lastTime = currentTime
            return True
        return False
    
class Logging():
    """
    Configure logging format and output type based on arguments passed to the program
    """
    def __init__(self, path):
        FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'

        # Check if we want to specify an output file for the logging
        if(len(sys.argv) < 2):
            logging.basicConfig(format=FORMAT, level=logging.INFO)
            logging.info("No output file specified file logging will be disabled to enable: ./main.py <outputfilepath>")
        else:
            logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler(str(os.path.dirname(os.path.abspath(path))) + "/" + sys.argv[1]), logging.StreamHandler()])

"""
Load sensor calibration details from a given file 
"""
class CalibrationLoader():

    def __init__(self, file = "CalibrationDetails.json"):
        logging.info(f"Retrieving calibration details from file: {file}")

        # Attempt to open the file and convert the contents to JSON object
        with open(file, "r") as f:
            self.data = json.load(f)
            logging.info("Succsessfully loaded calibration details!")
    
    """
    Retrieve the given calibration data
    """
    def get(self, field):
        return self.data[field]