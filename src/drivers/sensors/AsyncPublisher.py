"""
Will Richards, Oregon State University, 2024

Handles the asynchronous trascription of audio data and the subsequent API request 
"""
import os
from multiprocessing import Queue
from time import sleep
import uuid
import json
import logging

from drivers.DriverBase import DriverBase
from drivers.sensors.AudioTranscriber import AudioTranscriber
from drivers.sensors.Speaker import Speaker
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
         self.speaker = Speaker()
         self.dataQueue = dataQueue
         self.lastTranscription = ""
         self.isConnected = True
         self.cachedQueue = {}

    """
    Initialize the asynchoronous transcription and request handler
    """
    def initialize(self):
        self.data[self.moduleName]["data"]["initialized"].value = 1

        # Load data that was still waiting to be transmitted last round
        if os.path.exists("../data/cachedData.dat"):
            with open("../data/cachedData.dat", "r+") as file:

                    # Handle JSON files that are malformed and just write and empty dictionary so they are good to go for next time
                    try:
                        loadedData = json.load(file)
                    except json.JSONDecodeError as e:
                        logging.error("Failed to load cached data file.")
                        file.seek(0)
                        json.dump({}, file)
                        loadedData = {}
                        
                    self.cachedQueue = loadedData
                    for uid in self.cachedQueue:
                        self.dataQueue.put((uid, self.cachedQueue[uid]["fileNames"], self.cachedQueue[uid]["data"]))
    
    def measure(self) -> None:
        if not self.dataQueue.empty():
            # Get the uid for this packet, the file names associated with it and the data itself
            uid, fileNames, data = self.dataQueue.get_nowait()
            

            # Update our runtime dictionary of all the data packets that need to be sent
            self.cachedQueue[uid] = {
                "fileNames": fileNames,
                "data": data
            }
            
            # Write them out to our cached data
            with open("../data/cachedData.dat", "w") as file:
                json.dump(self.cachedQueue, file)

            # If we think we have internet access attempt to transmit the data
            if self.isConnected:

                # Check if the data collection was triggered by the user or the 2 hour 
                if(bool(data["DriverManager"]["data"]["userTrigger"]) == True):
                    self.lastTranscription = self.transcriber.transcribe(fileNames["voiceRecording"])

                data["SoundController"]["data"]["TranscribedText"] = self.lastTranscription

                # If our request succeeded  we don't need the files on device anymore
                requestSuccess, responseCode = self.requests.sendAPIRequest(fileNames, data)
                if requestSuccess:
                    # Delete the transmitted files
                    for key in fileNames.keys():
                        os.remove(fileNames[key])
                    
                    # Once we transmit the packet with the given unique identifier then we want to delete it from our local list and update the list on the disk
                    del self.cachedQueue[uid]
                    with open("../data/cachedData.dat", "w") as file:
                        json.dump(self.cachedQueue, file)
                    
                    # If our LEDDriver exists in the entry and it has been initialized then we want to flash green
                    if "LEDDriver" in self.data and self.data["LEDDriver"]["data"]["initialized"] == 1:
                        # If we succsessffully published we want to flash green and then off again
                        self.data["LEDDriver"]["events"]["DONE"][0].set()
                        time.sleep(2)
                        self.data["LEDDriver"]["events"]["NONE"][0].set()
                else:

                    # Determine what happened sorta, if device side failed to upload (-1 is returnd then we say something was wrong with the device) any other non 200 error is a internal server error
                    clipPath = "../media/"
                    if responseCode != -1:
                        clipPath += "failedToUpload.wav"
                    else:
                        clipPath += "internalServerError.wav"

                    self.speaker.unmuteSpeaker(2)
                    try:
                        self.speaker.playClip(clip)
                    except:
                        pass
                    self.speaker.muteSpeaker(2)

                    # We failed to upload so we want to flash red on and offf
                    # If our LEDDriver exists in the entry and it has been initialized then we want to flash green
                    if "LEDDriver" in self.data and self.data["LEDDriver"]["data"]["initialized"] == 1:
                        # If we succsessffully published we want to flash green and then off again
                        self.data["LEDDriver"]["events"]["ERROR"][0].set()
                        time.sleep(2)
                        self.data["LEDDriver"]["events"]["NONE"][0].set()

                    # Since we failed to upload our data we want to check if we can access the API at all if not then we know we have disconnected and as such 
                    self.isConnected = self.requests.sendHeartbeat()

                    # Since our connection failed we want to put the data we popped from the queue back in so that it will be retransmitted at some point
                    self.dataQueue.put((uid, fileNames, data))

            # If we aren't connected we want to push the data back into the queue that we popped off last and then attempt to ping the server for a connection
            elif not self.isConnected:
                # Since our connection failed we want to put the data we popped from the queue back in so that it will be retransmitted at some point
                self.dataQueue.put((uid, fileNames, data))
                self.isConnected = self.requests.sendHeartbeat()
                sleep(1)
                
            