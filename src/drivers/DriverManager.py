"""
Will Richards, Oregon State University, 2023

"""

from .DriverBase import DriverBase
from .ThreadedDriver import ThreadedDriver
from multiprocessing import Value, Array
import logging

from multiprocessing.sharedctypes import SynchronizedArray
from multiprocessing.synchronize import Event

class DriverManager():
    def __init__(self, *sensors: DriverBase):
        # Store a list of sensors, spawned sensor proccesses and a data dictionary to store our data
        self.sensors = list(sensors)
        self.proccessList = []
        self.data = {}
    
        # Loop over all sensors we are using and "threadify" them
        for sensor in self.sensors:
            
            # Format a new sensor objecti in the dectionary
            self._formatNewSensor(sensor)

            # Spawn the sensor into a proccess passing the data object along to be manipulated
            proccess = ThreadedDriver(sensor, self.data[sensor.moduleName]["data"])

            # Start the proccess
            proccess.start()
            self.proccessList.append(proccess)
        
        self.createJSONFormattedDict()
    """
    Basic pretty print for dictionary with Events and Synchronized data types
    
    :param d: The Dictionary we want to print
    :param indent: The number of indents we want before all of it

    """
    def prettyPrint(self, d, indent=0):
        for key, value in d.items():
            print('\t' * indent + str(key) + "{")
            # Check if the value is another dict and go a layer deeper
            if isinstance(value, dict):
                self.prettyPrint(value, indent+1)
            
            # If not we need to parse the values into a readable format based on their type
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
        try:
            splitName = event.split(".")

            # Set the call back for the specific event
            self.data[splitName[0]]["events"][splitName[1]][1] = callback
        except KeyError:
            logging.error("Specified event/sensor doesn't exist!")
    
    """
    Set an event on a given sub-module
    """
    def setEvent(self, event):
        splitName = event.split(".")
        self.data[splitName[0]]["events"][splitName[1]][0].set()
    """
    Check what callbacks need to be called per loop, and execute them as needed
    """
    def handleCallbacks(self):
        # Go through each sensors events and see if there is a callback set and if the event has triggered
        for sensor in self.sensors:
            for key,value in self.data[sensor.moduleName]["events"].items():
                if value[1] != None:
                    if(value[0].is_set()):
                        value[1](value[0])

    """
    Get the data from the manager

    :return: Dictionary of sensor data
    """
    def getData(self) -> dict:
        return self.data
    
    """
    Create the initial JSON dictionary so that we can just update values later
    """
    def createJSONFormattedDict(self):
        self.jsonDict = {}
        originalData = self.getData()
        for key, value in originalData.items():
            self.jsonDict[key] = {}
            #self.jsonDict[key]["data"] = originalData[key]["data"]
            self.jsonDict[key]["data"] = {}
            for dataKey, value in originalData[key]["data"].items():
                self.jsonDict[key]["data"][dataKey] = value.value
            self.jsonDict[key]["events"] = {}
            for eventKey, eventValue in originalData[key]["events"].items():
                self.jsonDict[key]["events"][eventKey] = list(originalData[key]["events"][eventKey])
                self.jsonDict[key]["events"][eventKey][0] = self.jsonDict[key]["events"][eventKey][0].is_set()

                if(self.jsonDict[key]["events"][eventKey][1] != None):
                    self.jsonDict[key]["events"][eventKey][1] = self.jsonDict[key]["events"][eventKey][1].__name__
        return self.jsonDict
    
    """
    Parse our data into a JSON readable format
    """
    def getJSON(self):
        originalData = self.getData()

        # Update the data values for each sensor
        for key, value in originalData.items():
            for dataKey, value in self.jsonDict[key]["data"].items():
                    self.jsonDict[key]["data"][dataKey] = originalData[key]["data"][dataKey].value
        
        
        # Update teh events for each sensor
        for key, value in originalData.items():
            for eventKey, value in self.jsonDict[key]["events"].items():
                    self.jsonDict[key]["events"][eventKey][0] = originalData[key]["events"][eventKey][0].is_set()

                    if(originalData[key]["events"][eventKey][1] != None):
                        self.jsonDict[key]["events"][eventKey][1] = originalData[key]["events"][eventKey][1].__name__
        return self.jsonDict

    """
    Format the dictionary to add a new sensor

    :param sensor: The sensor we are formatting for
    """
    def _formatNewSensor(self, sensor: DriverBase) -> None:
        self.data[sensor.moduleName] = {}
        self.data[sensor.moduleName]["data"] = sensor.createDataDict()
        self.data[sensor.moduleName]["events"] = sensor.getEvents()     
        for key, value in self.data[sensor.moduleName]["events"].items():
            self.data[sensor.moduleName]["events"][key] = [value, None]
    
    """
    Main driver control loop
    """
    def loop(self):
        self.handleCallbacks()

    """
    Shutdown the manager killing all running proccess
    """
    def kill(self):
        for proc in self.proccessList:
            proc.kill()

        

