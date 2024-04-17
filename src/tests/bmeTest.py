#!../../venv/bin/python
from time import sleep
import os


from helpers import Logging
from drivers.DriverManager import DriverManager
from drivers.sensors.BME688 import BME688

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    os.chdir(os.path.dirname(os.path.abspath(__file__)))


    logger = Logging()
    manager = DriverManager(BME688())
    
    while True:
        try:
            print(manager.getJSON())
            sleep(1)
        except KeyboardInterrupt:
            manager.kill()
            break