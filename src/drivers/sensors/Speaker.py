"""
Will Richards, Oregon State University, 2024

Provides a functionality to interface with a standard USB speaker using PyAudio and play sound over it
"""

import logging
import pyaudio
import wave


class Speaker():

    """
    Create a new instance of a speaker
    """
    def __init__(self):

        # Audio playback parameters
        self.device_index = 11
        self.pAudio = pyaudio.PyAudio()
        self.initialized = True

    
    """
    Play a given audio file out of the waveshare connected speaker

    :pram clipName: The name of the .wav file to paly
    """
    def playClip(self, clipName):
        wf = wave.open(clipName, 'r')

        # Attempt to open the speaker stream
        try:
            self.stream = self.pAudio.open(format = self.pAudio.get_format_from_width(wf.getsampwidth()),
                channels = 1,
                rate = wf.getframerate(),
                output = True,
                output_device_index=11)
        except Exception as e:
            logging.error("Failed to open audio input device: {e}")
            self.initialized = False

        # Only if the device succsessfully initialized should we actually attempt to write to it
        if(self.initialized):
            data = wf.readframes(self.frames_per_buffer)
            while data:
                self.stream.write(data)
                data = wf.readframes(self.frames_per_buffer)
        
        self.stream.close()

    def kill(self):
        self.pAudio.terminate()


        