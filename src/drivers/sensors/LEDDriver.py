"""
Will Richards, Oregon State University, 2024

Provides a wrapper for the TCLC59711 SPI LED Driver
"""

import enum
from drivers.DriverBase import DriverBase
from multiprocessing import Event
import logging
import adafruit_tlc59711
import board

"""
Device modes that the LED's are used to represent
CAMERA - The camera is currently taking an image, solid white
PROCCESSING - The bin is in the middle of computing results / taking measurements, Breathing yellow 
DONE - The bin has finished taking readings and is now idle, green
NONE - The device is currently idle, black
ERROR - Something went wrong, red
"""
class LEDMode(enum.Enum):
    CAMERA = 0,
    PROCESSING = 1,
    DONE = 2,
    NONE = 3,
    ERROR = 4


class LEDDriver(DriverBase):

    """
    LED Driver constructor

    :param pixel_count: The number of LED "pixels" that are connected to the controller
    """
    def __init__(self, pixel_count = 16):
        super().__init__("LEDDriver")

        spi = board.SPI()
        self.pixels = adafruit_tlc59711.TLC59711(spi, pixel_count=pixel_count)
        self.mode = LEDMode.PROCESSING
        self.initialized = False
        self.events = {
            "CAMERA": Event(),
            "PROCESSING": Event(),
            "DONE": Event(),
            "NONE": Event(),
            "ERROR": Event()
        }
    
    """
    This doesn't do anything other than tell us the driver has been initialized succsessfully
    """
    def initialize(self):
        # Set the GPIO numbering to that of the board itself and then set the specified GPIO pin as an input
        logging.info("Succsessfully configured LED Driver!")
        self.data["initialized"].value = 1
    
    """
    Updates the LED's based on the given device mode
    """
    def measure(self):
        self.handleEvents()

        if(self.mode == LEDMode.CAMERA):
           self.cameraMode()
        elif(self.mode == LEDMode.PROCESSING):
            self.proccessingMode()
        elif(self.mode == LEDMode.DONE):
            self.doneMode()
        elif(self.mode == LEDMode.ERROR):
            self.errorMode()
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

        elif self.getEvent("ERROR").is_set():
            self.mode = LEDMode.ERROR
            self.getEvent("ERROR").clear()
            
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
        self.pixels.set_pixel_all((1, 0.917, 0))

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
    Informs the user something went wrong by turning all pixels to red
    """
    def errorMode(self):
        self.pixels.set_pixel_all((1,0,0))

   