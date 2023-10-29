""""
Will Richards, Oregon State University, 2023

Abstraction layer for the MLX90640 
"""

from drivers.DriverBase import DriverBase

class MLX90640(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self):
        super().__init__("MLX90640", 1)

    def initialize(self):
        return super().initialize()

    def measure(self) -> list:
        return super().measure()
    

        