"""
Will Richards, Oregon State University, 2024

Handles the asynchronous trascription of audio data and the subsequent API request 
"""
import os
from multiprocessing import Queue
from drivers.DriverBase import DriverBase

from drivers.sensors.AudioTranscriber import AudioTranscriber
from helpers import RequestHandler

class AsyncPublisher(DriverBase):

    """
    Create a new instance of the async publisher

    :param dataQueue: A queue of tuples of (fileNameDict, dataPacketDict)
    """
    def __init__(self, dataQueue: Queue):
         super().__init__("AsyncPublisher")
         self.requests = RequestHandler()
         self.transcriber = AudioTranscriber()
         self.dataQueue = dataQueue
         self.lastTranscription = ""

    """
    Initialize the asynchoronous transcription and request handler
    """
    def initialize(self):
        self.data["initialized"].value = 1
    
    def measure(self) -> None:
        if not self.dataQueue.empty():
            fileNames, data = self.dataQueue.get_nowait()
            
            # Check if the data collection was triggered by the user or the 2 hour 
            if(bool(data["DriverManager"]["data"]["userTrigger"]) == True):
                self.lastTranscription = self.transcriber.transcribe(fileNames["voiceRecording"])

            data["SoundController"]["data"]["TranscribedText"] = self.lastTranscription

            # If our request succeeded  we don't need the files on device anymore
            if self.requests.sendAPIRequest(fileNames, data):
                # Delete the transmitted files
                for key in fileNames.keys():
                    os.remove(fileNames[key])
            