#!../../venv/bin/python
from time import sleep
import os


from helpers import Logging
from drivers.DriverManager import DriverManager
from drivers.sensors.NAU7802 import NAU7802

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    logger = Logging(__file__)
    manager = DriverManager(NAU7802(1))
    manager.setEvent("NAU7802.CALIBRATE")

    while manager.getEvent("NAU7802.CALIBRATE"):
        sleep(0.2)
    
    print("Calibration complete!")
    manager.kill()