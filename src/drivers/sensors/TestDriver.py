"""
Will Richards, Oregon State University, 2023

Provides a test no-hardware driver for simulating a sesnor in use with the ThreadedDriver and DriverManager
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
        super().__init__(name, 2)
        self.i = 0
        self.c = 0
        
        # List of events that the sensor can raise
        self.events = {
            "WEIGHT_CHANGE": Event(),
            "MORE_THAN_20": Event()
        }
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        logging.debug("Initialize")
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self):
        logging.debug("Measure")
        self.i+= 1
        self.c += 1

        if(self.i == 10):
            self.getEvent("WEIGHT_CHANGE").set()

        if(self.c > 20):
            self.getEvent("MORE_THAN_20").set()

        return [self.i, self.c]