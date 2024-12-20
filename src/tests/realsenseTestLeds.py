"""
Individual component test of the realsense camera
"""
import os
from multiprocessing import Pipe
from pathlib import Path

from helpers import Logging
from time import sleep

from drivers.sensors.RealsenseCamera import RealsenseCam
from drivers.sensors.LEDDriver import LEDDriver

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    path = Path(__file__)
    os.chdir(path.parent.absolute().parent.absolute())

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../data/"):
            os.mkdir("../data/")

    _, realsenseControllerConenction = Pipe()
    logger = Logging()
    manager = DriverManager(RealsenseCam(realsenseControllerConenction), LEDDriver())

    while True:
        try:
            print("Sending capture request!")
            manager.setEvent("LEDDriver.CAMERA")
            sleep(0.4)
            manager.setEvent("Realsense.CAPTURE")
            while manager.getEvent("Realsense.CAPTURE"):
                sleep(0.1)
            sleep(0.4)
            manager.setEvent("LEDDriver.NONE")
            sleep(5)
            print("Capture complete!")

        except KeyboardInterrupt:
            manager.kill()
            exit(0)
