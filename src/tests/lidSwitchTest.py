"""
Individual component test of the lid switch
"""
import os

from helpers import Logging
from time import sleep

from drivers.sensors.LidSwitch import LidSwitch

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../../data/"):
            os.mkdir("../../data/")

    logger = Logging(__file__)
    manager = DriverManager(LidSwitch())

    while True:
        try:
            print(manager.getJSON())

        except KeyboardInterrupt:
            manager.kill()
            exit(0)
