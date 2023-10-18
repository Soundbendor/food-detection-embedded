"""
Will Richards, Oregon State University, 2023

"""

from .DriverBase import DriverBase

class DriverManager():
    def __init__(self, **sensors: DriverBase):
        self.sensors = list(sensors)
