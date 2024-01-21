from time import time
import logging
import sys
import os

TWO_HOURS_SECONDS = 10

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
    def __init__(self):
        FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'

        # Check if we want to specify an output file for the logging
        if(len(sys.argv) < 2):
            logging.basicConfig(format=FORMAT, level=logging.INFO)
            logging.info("No output file specified file logging will be disabled to enable: ./main.py <outputfilepath>")
        else:
            logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler(str(os.path.dirname(os.path.abspath(__file__))) + "/" + sys.argv[1]), logging.StreamHandler()])
