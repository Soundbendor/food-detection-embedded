""""
Will Richards, Oregon State University, 2023

Abstraction layer for the NAU7802 to allow us to add stablitiy improvements if needed
"""

import PyNAU7802
import smbus2
import logging
import time

from drivers.DriverBase import DriverBase
from multiprocessing import Event, Value

class NAU7802(DriverBase):


    """
    Basic constructor for the NAU7802
    """
    def __init__(self, calibration_factor = 0):
        super().__init__("NAU7802", 1)
        self.nau = PyNAU7802.NAU7802()
        self.collectedData = 0
        if(calibration_factor == 0):
            print("No calibration factor entered!")
        self.calFactor = calibration_factor

        # How much additional weight will trigger a weight change event
        self.WEIGHT_THRESHOLD = 1.5
        self.weightDetectedLastTime = 0

        # List of events that the sensor can raise
        self.events = {
            "WEIGHT_CHANGE": Event()
        }

        

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

        
        self.nau.setCalibrationFactor(self.calFactor)
       

    """
    Measure and return the weight read from the load cell
    """
    def measure(self):
        logging.debug("Measuring...")
        self.lastWeight = self.collectedData
        self.collectedData = self.nau.getWeight(True, 18)

        # This will determine wether or not the event has occured in this cycle or not
        self.determineEventState()
        self.data = self.collectedData


    """
    Calibrate the load cell with a known weight
    """
    def calibrate(self):
        # Tare the scale again in case any weight was on it during initialize
        logging.info("Remove any weight present on the scale. You have 10 seconds...")
        time.sleep(10)
        self.tareScale()

        # Prompt the user for the mass of a known object in grams
        mass = int(input("Mass of calibration weight (grams): "))
        logging.info("Waiting 10 seconds for weight to be put on scale")
        time.sleep(10)

        # Calibrate the scale using the known mass
        self.nau.calculateCalibrationFactor(mass)

        print(f"Calibration Factor: {self.nau.getCalibrationFactor()}")
    
    """
    Tare the values of the load cell
    """
    def tareScale(self):
        self.nau.calculateZeroOffset()
    
    """
    Determine wether or not the events on this object should be triggered on this measure cycle
    """
    def determineEventState(self) -> None:
         # If the absolute value of the current weight - the last is greater than the threshold trigger the event, we also don't want to trigger twice in a row
        if(abs(self.collectedData - self.lastWeight) > self.WEIGHT_THRESHOLD and not self.weightDetectedLastTime) :
            self.getEvent("WEIGHT_CHANGE").set()
            self.weightDetectedLastTime = True
        # If our weight didn't change and our weight changed last time then we want to clear this flag so we can trigger another event on the next cycle
        elif(self.weightDetectedLastTime):
            self.weightDetectedLastTime = False
        
    def createDataDict(self):
        self.data = {
            "weight": Value('d', 0.0)
        }
        return self.data