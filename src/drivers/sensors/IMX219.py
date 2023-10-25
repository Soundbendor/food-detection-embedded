""""
Will Richards, Oregon State University, 2023

Abstraction layer for the IMX219 steroscopic imaging camera
"""

from drivers.DriverBase import DriverBase

class IMX219(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self):
        super().__init__("IMX219", 1)

    def initialize(self):
        return super().initialize()

    def measure(self) -> list:
        return super().measure()
    

        