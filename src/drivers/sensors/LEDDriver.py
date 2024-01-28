"""
Will Richards, Oregon State University, 2023

Provides a wrapper for the TCLC59711 SPI LED Driver
"""

import enum
from drivers.DriverBase import DriverBase
from multiprocessing import Event
import logging
import adafruit_tlc59711
import board
import busio

class LEDMode(enum.Enum):
    CAMERA = 0,
    PROCESSING = 1,
    DONE = 2,
    NONE = 3


class LEDDriver(DriverBase):
    """
    Driver base constructor takes in module name so we can make nice looking logs

    :param modName: Name of the module we are creating
    :param pin: What GPIO pin the hall-effect sensor is connected to
    """
    def __init__(self, pixel_count = 16):
        super().__init__("LEDDriver")

        spi = board.SPI()
        self.pixels = adafruit_tlc59711.TLC59711(spi, pixel_count=pixel_count)
        self.mode = LEDMode.NONE

        """
            List of events that the sensor can raise, this sensor uses them to trigger different lighting conditions
            CAMERA - Changes the current mode to camera, which is just white to take the picture
            PROCESSING - Breathing yellow color
            DONE - Solid Green
            NONE - LEDs are off
        """
        self.events = {
            "CAMERA": Event(),
            "PROCESSING": Event(),
            "DONE": Event(),
            "NONE": Event()
        }
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        # Set the GPIO numbering to that of the board itself and then set the specified GPIO pin as an input
        logging.info("Succsessfully configured LED Driver!")
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self):
        self.handleEvents()

        if(self.mode == LEDMode.CAMERA):
           self.cameraMode()
        elif(self.mode == LEDMode.PROCESSING):
            self.proccessingMode()
        elif(self.mode == LEDMode.DONE):
            self.doneMode()
        else:
            self.noneMode()
        
        self.pixels.show()

    """
    Handles mode switching depending on if an event was set or not
    """
    def handleEvents(self):
        if self.getEvent("CAMERA").is_set():
            self.mode = LEDMode.CAMERA
            self.getEvent("CAMERA").clear()
        
        elif self.getEvent("PROCESSING").is_set():
            self.mode = LEDMode.PROCESSING
            self.getEvent("PROCESSING").clear()

        elif self.getEvent("DONE").is_set():
            self.mode = LEDMode.DONE
            self.getEvent("DONE").clear()
            
        elif self.getEvent("NONE").is_set():
            self.mode = LEDMode.NONE
            self.getEvent("NONE").clear()
    
    """
    Drives the LEDs to white for the camera to take a picture
    """
    def cameraMode(self):
        self.pixels.set_pixel_all((1, 1, 1))

    """
    Drives the LEDs to breath yellow while we are proccessing the data
    """
    def proccessingMode(self):
        self.pixels.set_pixel_all((255, 234, 0))

    """
    Drives the LEDs to solid green to signify we are done with the sample
    """
    def doneMode(self):
        self.pixels.set_pixel_all((0, 1, 0))

    """
    Drives the LEDs to off to signify we are not doing anything
    """
    def noneMode(self):
        self.pixels.set_all_black()

    """
    Create a specified dictionary of values to create keys for the values we will update
    """
    def createDataDict(self):
        self.data = {}
        return self.data