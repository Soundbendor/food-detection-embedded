"""
Will Richards, Oregon State University, 2023

Provides a genric wrapper for converting generic drivers into its own driver proccess.
We wait to use multiproccessing instead of threads to avoid GIL in python
"""

from multiprocessing import Event, Process
from time import sleep

from .DriverBase import DriverBase

class ThreadedDriver(Process):

    """
    Ctor for a new driver thread

    :param driver: Instance of the driver we are "threadifying"
    """
    def __init__(self, driver: DriverBase):
        super().__init__()
        self.driver: DriverBase = driver
        self.isRunning = True

    """
    Overridden proccess runner so that we can initialize and use all our drivers the same because we know exactly how they will be have
    """
    def run(self) -> None:
        # Initialize and loop indefinatley until the proccess is killed
        self.driver.initialize()
        while(True):
            print(self.driver.measure())
            sleep(0.1)
        

    """
    Kill the proccess, doesn't do anything special right now but might eventually
    """
    def kill(self) -> None:
        return super().kill()
        

