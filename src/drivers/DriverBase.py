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
    def __init__(self, modName, numOutputs):
        self.moduleName = modName
        self.numOutputs = numOutputs
        self.events = {}
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        pass
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self) -> None:
        pass

    """
    Should have the builtin functionality to calibrate a sensor if needed 
    """
    def calibrate(self):
        pass

    """
    Get the events that the driver has
    """
    def getEvents(self) -> dict:
        return self.events
    
    """
    Get a specific event from the dictionary
    """
    def getEvent(self, event) -> Event:
         return self.events[event][0]

    """
    What to do when execution is ending
    """
    def kill(self):
        pass

    """
    Create and return a dictionary of the data that the specific sensor will be supplying
    """
    def createDataDict(self):
        pass
    """
    Get the number of measurements that this sensor will output
    """
    def getNumberOfOutputs(self) -> int:
        return self.numOutputs

        