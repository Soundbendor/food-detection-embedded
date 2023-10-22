"""
Will Richards, Oregon State University, 2023

Provides a unified parent class that all sensor drivers can inherit from
"""

from multiprocessing import Event

class DriverBase:
    """
    Driver base constructor takes in module name so we can make nice looking logs

    :param modName: Name of the module we are creating
    """
    def __init__(self, modName):
        self.moduleName = modName
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        pass
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self):
        pass

    """
    Should have the builtin functionality to calibrate a sensor if needed 
    """
    def calibrate(self):
        pass

    """
    Get a dictionary of the events on the Driver
    """
    def getEvents(self) -> dict:
        pass

    """
    Get a specific event from the dictionary
    """
    def getEvent(self, event) -> Event:
        pass

    """
    What to do when execution is ending
    """
    def kill(self):
        pass
        