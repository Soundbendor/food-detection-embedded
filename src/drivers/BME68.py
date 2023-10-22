""""
Will Richards, Oregon State University, 2023

Abstraction layer for the BME68 gas sensor
"""

from smbus2 import SMBus
import logging
import time

from .DriverBase import DriverBase
from multiprocessing import Event

class BME68(DriverBase):


    """
    Basic constructor for the BME68
    """
    def __init__(self, i2c_address = 0x76):
        super().__init__("BME68")
        self.i2c_address = i2c_address
        self.collectedData = 0
        
        # List of events that the sensor can raise
        self.events = {
           
        }

        

    """
    Initialize the NAU7802 to begin taking sensor readings
    """
    def initialize(self):
        self.i2c_bus = SMBus(1)

        # Read the value out of the ctrl_hum register
        reg_value = self.i2c_bus.read_byte_data(self.i2c_address, 0x72)
        data = 0b10111001 & reg_value

        # Configure humidity oversampling to 1x
        self.i2c_bus.write_byte_data(self.i2c_address, 0x72, data)

        # Configure temperature oversampling to 2x and pressure oversampling to 16x
        data = 0b01010100
        self.i2c_bus.write_byte_data(self.i2c_address, 0x74, data)

        # Set gas_wait_0 to 0x59 for a 100ms warmup
        data = 0b01011001
        self.i2c_bus.write_byte_data(self.i2c_address, 0x64, data)



        
        pass
       

    """
    Measure and return the weight read from the load cell
    """
    def measure(self):
        logging.debug("Measuring...")
        return self.collectedData


    """
    Calibrate the load cell with a known weight
    """
    def calibrate(self):
       pass
  
    """
    Return the dictionary of events
    """
    def getEvents(self) -> dict:
        return self.events
    
    """
    Get a an event from the driver
    """
    def getEvent(self, event) -> Event:
        return self.events[event][0]
    
    def kill(self):
        self.i2c_bus.close()
        