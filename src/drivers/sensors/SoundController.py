"""
Will Richards, Oregon State University, 2023

Wrapper for Microphone and Audio output to be threadified to avoid truly blocking the main thread
"""

from multiprocessing import Event, Value
import subprocess
import os

from drivers.DriverBase import DriverBase
from drivers.sensors.Microphone import Microphone
from drivers.sensors.Speaker import Speaker

class SoundController(DriverBase):

    """
    Create a new SoundController device to manage our microphone and speaker

    :param soundControllerConnection: This is a reference to a multiproccessing.Pipe to send our transcription back to the main thread
    :param record_duration: The lenght of time the microphone should be recording for
    """
    def __init__(self, soundControllerConnection, record_duration = 10):
        super().__init__("SoundController")

        # Create our new mic and speaker instances
        self.microphone = Microphone(record_duration)
        self.speaker = Speaker()
        self.soundControllerConnection = soundControllerConnection
        self.alsaSoundCardNum = 2

        # Set our loop time to 0.05 cause we dont need super fast looping
        self.loopTime = 0.05
        
        self.events = {
            "RECORD": Event()
        }

    """
    Mute both the speaker and microphone to avoid feedback and then initialize our microphone
    """
    def initialize(self):
        self.muteMic()
        self.muteSpeaker()
        self.microphone.initialize()
        self.initialized = True
        self.data["initialized"].value = 1

    """
    Mute the speaker attatched to the waveshare adapter
    """
    def muteSpeaker(self):
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/usr/bin/amixer', '-c', str(self.alsaSoundCardNum), 'sset', 'Speaker', 'mute'], stdout=devnull, stderr=subprocess.STDOUT)

    """
    Unmute the speaker attatched to the waveshare adapter
    """
    def unmuteSpeaker(self):
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/usr/bin/amixer', '-c', str(self.alsaSoundCardNum), 'sset', 'Speaker', 'unmute'], stdout=devnull, stderr=subprocess.STDOUT)

    """
    Mute the mic attatched to the waveshare adapter
    """
    def muteMic(self):
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/usr/bin/amixer', '-c', str(self.alsaSoundCardNum), 'sset', 'Mic', 'mute'], stdout=devnull, stderr=subprocess.STDOUT)

    """
    Unmute the mic attatched to the waveshare adapter
    """
    def unmuteMic(self):
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/usr/bin/amixer', '-c', str(self.alsaSoundCardNum), 'sset', 'Mic', 'unmute'], stdout=devnull, stderr=subprocess.STDOUT)

    """
    If a capture request was recieved we want to play the audio and then record a clip until a non-silent clip is recieved
    """
    def measure(self):
        if(self.events["RECORD"][0].is_set()):
            # NOTE: We must mute and unmute the speaker and micophpone channels otherwise the cause huge amounts of deafening feedback
            self.unmuteSpeaker()
            self.speaker.playClip("../media/itemRequest.wav")
            self.muteSpeaker()

            # Check if we actually saved the audio to the file or not if not we want to ask the user for another transcription
            gotRecording = False
            retries = 0
            while not gotRecording and retries < 3:

                # Record the microphone and return the file name that it was saved at
                self.unmuteMic()
                fileName = self.microphone.record()
                self.muteMic()

                # If the file was saved succsessfully send it and move on but if not TELL the user that we are re-recording
                if(len(fileName) != 0):
                    gotRecording = True
                    self.soundControllerConnection.send({"voiceRecording": fileName})
                else:
                    self.unmuteSpeaker()
                    self.speaker.playClip("../media/didntCatch.wav")
                    self.muteSpeaker()
                    retries += 1
            self.events["RECORD"][0].clear()
        
    """
    Shutdown our microphone and speaker
    """
    def kill(self):
        self.microphone.kill()
        self.speaker.kill()

    """
    Add TranscribedText to our data dictionary that will be populated by the main thread
    """
    def createDataDict(self):
        self.data = {
                "TranscribedText": "",
                "initialized": Value('i', 0)
            }
        return self.data