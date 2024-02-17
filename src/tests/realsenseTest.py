"""
Individual component test of the realsense camera
"""
import os

from helpers import Logging
from time import sleep

from drivers.sensors.RealsenseCamera import RealsenseCam

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../../data/"):
            os.mkdir("../../data/")

    logger = Logging(__file__)
    manager = DriverManager(RealsenseCam())

    while True:
        try:
            print("Sending capture request!")
            manager.setEvent("Realsense.CAPTURE")
            while manager.getEvent("Realsense.CAPTURE"):
                sleep(0.1)
            sleep(5)
            print("Capture complete!")

        except KeyboardInterrupt:
            manager.kill()
            exit(0)
