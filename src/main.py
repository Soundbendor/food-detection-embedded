#!../venv/bin/python

"""
Will Richards, Oregon State University, 2023

Detection Loop for all Binsight Devices

Records data when the lid is opened and then closed and once every 2 hours
"""

from time import sleep

from drivers.MainController import MainController
from helpers import TimeHelper    

def main():
    # Read calibration parameters in and setup our debug logging, additionally setup our time tracker
    timeHelper = TimeHelper()
    controller = MainController()
    
    # Register a callback for when the lid is closed so we can sample our data
    while(True):
        try:
            controller.handleCallbacks()
            if timeHelper.twoHourInterval():
                controller.collectData()

            sleep(0.001)
           
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            controller.kill()
            break

if __name__ == "__main__":
    main()
