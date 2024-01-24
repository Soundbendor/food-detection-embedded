"""
Will Richards, Oregon State University, 2023

Wrapper for Microphone and Audio output to be threadified to avoid truly blocking the main thread
"""

from multiprocessing import Event

from drivers.DriverBase import DriverBase
from drivers.sensors.Microphone import Microphone

class SoundController(DriverBase):
    def __init__(self, record_duration = 10):
        super().__init__("SoundController")
        self.record_duration = record_duration
        self.microphone = Microphone()
        self.sound = None

        self.loopTime = 0.05
        
        self.events = {
            "RECORD": Event()
        }

    def measure(self):
        if(self.events["RECORD"][0].is_set()):
            # Todo: Play sound here

            self.microphone.record(self.record_duration)
            self.events["RECORD"][0].clear()
        
    def kill(self):
        # Add sound destruction here too
        self.microphone.kill()

    def createDataDict(self):
        return {}