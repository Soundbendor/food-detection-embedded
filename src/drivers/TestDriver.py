"""
Will Richards, Oregon State University, 2023

Provides a unified parent class that all sensor drivers can inherit from
"""

from drivers.DriverBase import DriverBase
from multiprocessing import Event

import logging

class TestDriver(DriverBase):
    """
    Driver base constructor takes in module name so we can make nice looking logs

    :param modName: Name of the module we are creating
    """
    def __init__(self, name):
        super().__init__(name)
        self.i = 0

        # List of events that the sensor can raise
        self.events = {
            "WEIGHT_CHANGE": Event(),
            "MORE_THAN_20": Event()
        }
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        logging.info("Initialize")
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self):
        logging.info("Measure")
        self.i+= 1

        if(self.i == 10):
            self.getEvent("WEIGHT_CHANGE").set()

        if(self.i > 20):
            self.getEvent("MORE_THAN_20").set()

        return self.i

    """
    Should have the builtin functionality to calibrate a sensor if needed 
    """
    def calibrate(self):
        pass

    def getEvents(self) -> dict:
        return self.events
    
    """
    Get a an event from the driver
    """
    def getEvent(self, event) -> Event:
        return self.events[event][0]
        