"""
Will Richards, Oregon State University, 2023

Provides a functionality to interface with a standard USB microphone using a USB Audio DAC and PyAudio
"""

import pyaudio
import wave
from pydub import AudioSegment as am
import os

class Microphone():
    def __init__(self):

        self.sampling_rate = 44100
        self.downsample_rate = 16000
        self.device_index = 11
        self.frames_per_buffer = 128
        self.format = pyaudio.paInt16
        
        self.pAudio = pyaudio.PyAudio()
        self.stream = self.pAudio.open(
            format=pyaudio.paInt16,
            rate = self.sampling_rate,
            input=True,
            channels=1,
            input_device_index=self.device_index,
            frames_per_buffer=self.frames_per_buffer,
            start=False
        )

    """
    Record a clip from the microphone
    """
    def record(self, duration):
        frames = []

        self.stream.start_stream()

        for i in range(0, int(self.sampling_rate / self.frames_per_buffer * duration)):
            data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()

        # Write the pre downsampled audio to .wav file
        wf = wave.open("../data/preDownsampledAudio.wav", "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.pAudio.get_sample_size(self.format))
        wf.setframerate(self.sampling_rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        # Downsample and file and save removing the preDownsampledAudio file
        sound = am.from_file("../data/preDownsampledAudio.wav", format="wav", frame_rate=self.sampling_rate)
        sound = sound.set_frame_rate(self.downsample_rate)
        sound.export("../data/downsampledAudio.wav", format="wav")

        os.remove("../data/preDownsampledAudio.wav")



    def kill(self):
        self.stream.close()
        self.pAudio.terminate()


        