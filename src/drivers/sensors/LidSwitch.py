"""
Will Richards, Oregon State University, 2023

Provides a basic wrapper for reading values and triggering events upon the changes of a hall-effect sensor
"""

from operator import truediv
from drivers.DriverBase import DriverBase
from multiprocessing import Event, Value
import logging

import Jetson.GPIO as GPIO

class LidSwitch(DriverBase):
    """
    Driver base constructor takes in module name so we can make nice looking logs

    :param modName: Name of the module we are creating
    :param pin: What GPIO pin the hall-effect sensor is connected to
    """
    def __init__(self, pin = 12):
        super().__init__("LidSwitch")

        # The current GPIO pin that the hall-effect sensor is connected to.
        # NOTE: We have to use tegra naming conventions here because the LED driver runs in TEGRA_SOC mode so we have to make a conversion from our normal board pin number to the TEGRA_SOC pin
        # Solution: https://stackoverflow.com/a/61039192
        tegra_to_board_conversion = {k: list(GPIO.gpio_pin_data.get_data()[-1]['TEGRA_SOC'].keys())[i] for i, k in enumerate(GPIO.gpio_pin_data.get_data()[-1]['BOARD'])}
        self.selectedPin = tegra_to_board_conversion[pin]

        # If the lid is open or not
        self.lidOpen = False
        
        # Set default lid state to be closed
        self.lastState = GPIO.LOW
        
        # List of events that the sensor can raise
        self.events = {
            "LID_OPENED": Event(),
            "LID_CLOSED": Event()
        }
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def initialize(self):
        # Set the GPIO numbering to that of the board itself and then set the specified GPIO pin as an input
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.TEGRA_SOC)
        GPIO.setup(self.selectedPin, GPIO.IN)
        logging.info("Succsessfully configured hall effect sensor!")
    
    """
    Should be overloaded on all sub drivers so initialize can be called on all drivers at once
    """
    def measure(self):
        # Handle the changing state of the lid
        self.handleEvents()

        # Update the state of the lid
        self.data["Lid_State"].value = int(self.lidOpen)
    
    """
    Handle the open and close events
    """
    def handleEvents(self):
        currentReading = GPIO.input(self.selectedPin)

        # Set the value of lidOpen equal to whether or not the pin is pulled HIGH
        self.lidOpen = (currentReading == GPIO.HIGH)

        # If between the current reading and the last reading the state of the hall-effect sensor transitioned from LOW to HIGH we opened the lid and should trigger the event
        if (currentReading == GPIO.HIGH and self.lastState == GPIO.LOW):
            self.getEvent("LID_OPENED").set()

        # Tranistion from a HIGH state to a LOW state we know the lid was closed and should trigger the event
        elif(currentReading == GPIO.LOW and self.lastState == GPIO.HIGH):
            self.getEvent("LID_CLOSED").set()

        # Update the last state
        self.lastState = currentReading
        
    """
    Create a specified dictionary of values to create keys for the values we will update
    """
    def createDataDict(self):
        self.data = {
            "Lid_State": Value('i', 0),
        }
        return self.data