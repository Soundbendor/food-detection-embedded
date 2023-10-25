"""
Will Richards, Oregon State University, 2023

Provides a genric wrapper for converting generic drivers into its own driver proccess.
We wait to use multiproccessing instead of threads to avoid GIL in python
"""

from multiprocessing import Event, Manager, Process, Value

from time import sleep, time
import logging


from .DriverBase import DriverBase

class ThreadedDriver(Process):

    """
    Ctor for a new driver thread

    :param driver: Instance of the driver we are "threadifying"
    :param data: Manager controlled data object to handle all the different sensors in use
    """
    def __init__(self, driver: DriverBase, data):
        super().__init__()
        self.driver: DriverBase = driver
        self.isRunning = True
        self.data = data

    """
    Overridden process runner so that we can initialize and use all our drivers the same because we know exactly how they will be have
    """
    def run(self) -> None:
        self.driver.initialize()
        while(True):
            self._measureSensor()
            sleep(0.001)
        

    """
    Local method to handle measuring of the senosor
    """
    def _measureSensor(self):
        if(self.driver.shouldMeasure()):
            # Convert the measured values into the list of threaded 
            measurement = self.driver.measure()
            for i in range(len(measurement)):
                self.data[i] = measurement[i]
    """
    Kill the proccess, doesn't do anything special right now but might eventually
    """
    def kill(self) -> None:
        self.driver.kill()
        return super().kill()
        

