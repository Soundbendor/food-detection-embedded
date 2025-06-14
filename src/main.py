#!../venv/bin/python

"""
Will Richards, Oregon State University, 2023

Detection Loop for all Binsight Devices

Records data when the lid is opened and then closed and once every 2 hours
"""

import os
from time import sleep

from drivers.MainController import MainController
from helpers import Logging, TimeHelper


def main():
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create the instance of our controller
    controller = MainController()
    
    # Register a callback for when the lid is closed so we can sample our data
    while(True):
        try:
            controller.handleCallbacks()
            sleep(0.001)
           
        # On keyboard interrupt we want to cleanly exit
        except KeyboardInterrupt:
            controller.kill()
            break

if __name__ == "__main__":
    logger = Logging(verbose=True)
    main()
