#!../venv/bin/python

"""
Will Richards, Oregon State University, 2023

Detection Loop for all Binsight Devices

Records data when the lid is opened and then closed and once every 2 hours
"""

from time import sleep
import os

from drivers.MainController import MainController
from helpers import TimeHelper, Logging    

def main():
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Read calibration parameters in and setup our debug logging, additionally setup our time tracker
    timeHelper = TimeHelper()
    controller = MainController()
    
    
    # Register a callback for when the lid is closed so we can sample our data00000000
    while(True):
        try:
            controller.handleCallbacks()
            if timeHelper.twoHourInterval():
                controller.collectData(triggeredByLid=False)

            sleep(0.001)
           
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            controller.kill()
            break

if __name__ == "__main__":
    logger = Logging(verbose=True)
    main()
