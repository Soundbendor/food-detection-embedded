"""
Individual component test of the LEDs
"""
import os

from helpers import Logging
from time import sleep

from drivers.sensors.LEDDriver import LEDDriver

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../../data/"):
            os.mkdir("../../data/")

    logger = Logging(__file__)
    manager = DriverManager(LEDDriver())

    while True:
        try:
            print("Camera mode...")
            manager.setEvent("LEDDriver.CAMERA")
            sleep(5)
            print("Proccessing mode...")
            manager.setEvent("LEDDriver.PROCESSING")
            sleep(5)
            print("Done mode...")
            manager.setEvent("LEDDriver.DONE")
            sleep(5)
            print("Error mode...")
            manager.setEvent("LEDDriver.ERROR")
            sleep(5)
            print("None mode...")
            manager.setEvent("LEDDriver.NONE")
            sleep(5)

        except KeyboardInterrupt:
            manager.kill()
            exit(0)
