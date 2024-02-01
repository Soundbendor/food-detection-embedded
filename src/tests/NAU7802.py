#!./../../venv/bin/python
"""
Will Richards, Oregon State University, 2023

Provides a basic runnable test to check functionality of NAU7802
"""
from drivers.sensors.NAU7802 import NAU7802

import os
import logging
from time import sleep

CALIBRATION_FACTOR = -135.4875

def main():
    # Create a new sensor, using the defaults is fine here
    #nau = NAU7802(CALIBRATION_FACTOR)
    nau = NAU7802()

    # Initialize the sensor and conduct a measurement
    nau.initialize()

    # Measure and print out reading
    while True:
        try:
            logging.info(f"Data measured from NAU7802: {nau.measure()}")
            sleep(1)
        except KeyboardInterrupt:
            break


# Run main as soon as the script starts
if __name__ == "__main__":

    # Configure Logger
    FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging.FileHandler(str(os.path.dirname(os.path.abspath(__file__))) + "/NAU7802_Example.log"), logging.StreamHandler()])

    main()