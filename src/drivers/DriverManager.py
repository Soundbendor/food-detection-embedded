"""
Will Richards, Oregon State University, 2023

"""


from asyncio.windows_events import NULL
from .DriverBase import DriverBase
from .ThreadedDriver import ThreadedDriver

from multiprocessing import Value, Array

from multiprocessing.sharedctypes import SynchronizedArray
from multiprocessing.synchronize import Event

class DriverManager():
    def __init__(self, *sensors: DriverBase):
        self.sensors = list(sensors)
        self.driverThreads = []
        self.data = {}
    
        # Loop over all sensors we are using and "threadify" them
        for sensor in self.sensors:
            self.data[sensor.moduleName] = {}
            self.data[sensor.moduleName]["data"] = Array('d', [NULL]*10)
            self.data[sensor.moduleName]["events"] = sensor.getEvents()     
            for key, value in self.data[sensor.moduleName]["events"].items():
                self.data[sensor.moduleName]["events"][key] = [value, None]


            thread = ThreadedDriver(sensor, self.data[sensor.moduleName]["data"])
            thread.start()
            self.driverThreads.append(thread)

    """
    Basic pretty print for dictionary with Events and Synchronized data types
    
    :param d: The Dictionary we want to print

    """
    def prettyPrint(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key) + "{")
            # Check if the value is another dict and go a layer deeper
            if isinstance(value, dict):
                self.prettyPrint(value, indent+1)
            
            # If not we need to parse the values in a 
            else:
                if(type(value) == list):
                    print('\t' * (indent+1) + str(value[0].is_set()) + ",\n" +  '\t' * (indent+1) + str(value[1]))
                elif(type(value) == SynchronizedArray):
                    print('\t' * (indent+1) + str(list(value)))
                else:
                    print('\t' * (indent+1) + str(value))
            print('\t' * indent + "}")

    """
    Register a function to run on a given call back

    :param event: String formatted as follows to select event SENSOR.EVENT
    :param callback: Function call back to supply for a given events
    """
    def registerEventCallback(self, event: str, callback):
        splitName = event.split(".")

        # Set the call back for the specific event
        self.data[splitName[0]]["events"][splitName[1]][1] = callback
    
    """
    Check what callbacks need to be called per loop
    """
    def handleCallbacks(self):
        # Go through each sensors events and see if there is a callback set and if the event has triggered
        for sensor in self.sensors:
            for key,value in self.data[sensor.moduleName]["events"].items():
                if value[1] != None:
                    if(value[0].is_set()):
                        value[1](value[0])

        
    
    """
    Main driver control loop
    """
    def loop(self):
        self.handleCallbacks()
        self.prettyPrint(self.data)
        

