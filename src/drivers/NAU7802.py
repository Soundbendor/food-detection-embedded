""""
Will Richards, Oregon State University, 2023

Abstraction layer for the NAU7802 to allow us to add stablitiy improvements if needed
"""

import PyNAU7802
import smbus2
import logging
from time import sleep

from .DriverBase import DriverBase

class NAU7802(DriverBase):

    """
    Basic constructor for the NAU7802
    """
    def __init__(self):
        self.nau = PyNAU7802.NAU7802()

    """
    Initialize the NAU7802 to begin taking sensor readings
    """
    def initialize(self):
        i2cBus = smbus2.SMBus(1)
        if self.nau.begin(i2cBus):
            logging.info("Connected to NAU7802!")
        else:
            logging.error("Failed to connect to NAU7802")
            return False

        logging.info("Taring scale...")
        self.tareScale()

    """
    Measure and return the weight read from the load cell
    """
    def measure(self):
        data = []
        for _ in range(3):
            data.append(self.nau.getWeight())
        self.collectedData = sum(data) / len(data)
        return self.collectedData


    """
    Calibrate the load cell with a known weight
    """
    def calibrate(self):
        # Tare the scale again in case any weight was on it during initialize
        logging.info("Remove any weight present on the scale. You have 10 seconds...")
        sleep(10)
        self.tareScale()

        # Prompt the user for the mass of a known object in grams
        mass = int(input("Mass of calibration weight (grams): "))
        logging.info("Waiting 10 seconds for weight to be put on scale")
        sleep(10)

        # Calibrate the scale using the known mass
        self.nau.calculateCalibrationFactor(mass)
    """
    Tare the values of the load cell
    """
    def tareScale(self):
        self.nau.calculateZeroOffset()
        