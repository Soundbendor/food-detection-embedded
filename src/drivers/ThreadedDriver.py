"""
Will Richards, Oregon State University, 2023

Provides a genric wrapper for converting generic drivers into its own driver proccess.
"""

from multiprocessing import Process
from time import sleep

from DriverBase import DriverBase

class ThreadedDriver(Process):

    """
    Ctor for a new driver thread

    :param driver: Instance of the driver we are "threadifying"
    :param data: Manager created dictionary where sensors can populate values within
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
        try:
            self.driver.initialize()
            while(self.isRunning):
                self.driver.measure()
                sleep(self.driver.loopTime)
                
        except KeyboardInterrupt:
            self.kill()
        
    """
    Kill the proccess, doesn't do anything special right now but might eventually
    """
    def kill(self) -> None:
        self.isRunning = False
        self.driver.kill()
    
    
        

