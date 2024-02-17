#!../../venv/bin/python
from time import sleep
import os


from helpers import Logging, CalibrationLoader
from drivers.DriverManager import DriverManager
from drivers.sensors.NAU7802 import NAU7802

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


    logger = Logging(__file__)
    calibration = CalibrationLoader("../CalibrationDetails.json")
    manager = DriverManager(NAU7802(calibration.get("NAU7802_CALIBRATION_FACTOR")))
    
    while True:
        try:
            print(manager.getJSON())
            sleep(1)
        except KeyboardInterrupt:
            manager.kill()
            break