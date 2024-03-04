"""
Will Richards, Oregon State University, 2024

Provides a functionality to interface with a standard USB microphone using a USB Audio DAC and PyAudio
"""

import logging
import pyaudio
import wave
from pydub import AudioSegment as am
import os
import numpy as np
import whisper
import torch
import numpy as np
import re
import subprocess

class Microphone():

    """
    Create a new instance of the microhpone which will be used to collect item descriptions

    :param record_duration: The lenght of time in seconds that the microphone will record for
    """
    def __init__(self, record_duration=10):

        # Audio recording parameters
        self.sampling_rate = 16000
        self.device_index = 1
        self.channels = 2
        self.frames_per_buffer = 128
        self.format = pyaudio.paInt16
        self.record_duration = record_duration

        self.pAudio = pyaudio.PyAudio()

        # Load the silero-vad Voice Activation Model to reduce overall inference time by ignoring audio with no voice in it
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',model='silero_vad',force_reload=True,onnx=False)
        (self.get_speech_timestamps, self.save_audio, self.read_audio,_, self.collect_chunks) = utils

        # Enable the microphone capture
        with open(os.devnull, 'wb') as devnull:
            subprocess.check_call(['/usr/bin/amixer', '-c', '3', 'set', 'Mic', 'cap'], stdout=devnull, stderr=subprocess.STDOUT)


    """
    Initialize the whisper model and warm it up by feeding 0s into it
    """
    def initialize(self):
        logging.info("Loading model...")
        self.asrModel = whisper.load_model("base.en")
        logging.info("Loading complete! Warming up model...")
        whisper.transcribe(model=self.asrModel, audio=np.zeros(self.record_duration * self.sampling_rate, np.float32), fp16=False)
        logging.info("Model has been warmed up! Ready for inference")
        self.initialized = True
            
    """
    Write some audio data out to a .wav file

    :param data: Data to be written to the wav file
    :param outputFile: The name of the file the data should be written to
    """
    def writeWave(self, data, outputFile):
        # Write the pre downsampled audio to .wav file
        wf = wave.open(outputFile, "wb")
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pAudio.get_sample_size(self.format))
        wf.setframerate(self.sampling_rate)
        wf.writeframes(b''.join(data))
        wf.close()

    """
    Downsample a given audio file to 16khz, and then remove the previous file

    :param inputFile: File that we wish to downsample
    :param outputFile: The resulting downsampled output file
    """
    def downsampleAudio(self, inputFile, outputFile):
        logging.info("Downsampling Audio....")
        sound = am.from_file(inputFile, format="wav", frame_rate=self.sampling_rate)
        sound = sound.set_frame_rate(self.sampling_rate)
        sound.export(outputFile, format="wav")
        os.remove(inputFile)

    """
    Record audio from the microphone and write it to a file

    :param outputFile: File to write the recorded audio to
    """
    def _record(self, outputFile):
        frames = []

        # Attempt to open the microphone stream
        try:
            self.stream = self.pAudio.open(
                format=pyaudio.paInt16,
                rate = self.sampling_rate,
                input=True,
                channels=2,
                input_device_index=self.device_index,
                frames_per_buffer=self.frames_per_buffer,
            )
        except Exception as e:
            logging.error("Failed to open audio input device: {e}")
            self.initialized = False


        logging.info("RECORDING....")
        self.stream.start_stream()

        for _ in range(0, int(self.sampling_rate / self.frames_per_buffer * self.record_duration)):
            data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()

        self.writeWave(frames, outputFile)
        self.stream.close()
        logging.info("STOPPED RECORDING")

    
    """
    Utilize the Silero-VAD model to determine if a given audio contains speaking

    :param inputFile: The file we want to run our voice detection algorithm on
    :param outputFile: The file that if we did find speaking contains only the speaking parts

    :return: Whether or not the VAD detected speaking in the given input file
    """
    def detectSpeaking(self, inputFile, outputFile) -> bool:
        logging.info("Detecting speaking....")
        wav = self.read_audio(inputFile, sampling_rate=self.sampling_rate)
        speech_timestamps = self.get_speech_timestamps(wav, self.model, sampling_rate=self.sampling_rate, speech_pad_ms=500)
        if(len(speech_timestamps) > 0):
            self.save_audio(outputFile, self.collect_chunks(speech_timestamps, wav), sampling_rate=self.sampling_rate) 
            return True
        return False
    
    """
    Utilize the whisper model to transcribe a given input file into the text

    :param inputFile: File to transcribe
    """
    def transcribe(self, inputFile) -> str:
        logging.info("Transcribing audio....")
        audio = whisper.load_audio(inputFile)
        results = whisper.transcribe(model=self.asrModel, audio=audio, fp16=False)
        return results["text"]

    """
    Record a clip from the microphone
    """
    def record(self):
        if self.initialized:
            # Record and downsample the audio to 16khz
            self._record("../data/downsampledAudio.wav")
            
            if(self.detectSpeaking("../data/downsampledAudio.wav", "../data/only_speech.wav")):
                transcribedText = self.transcribe('../data/only_speech.wav')
                transcribedText = re.sub("[.,:;]", "", transcribedText).strip()
                os.remove('../data/only_speech.wav')
                return transcribedText
            else:
                logging.warning("No speaking detected in clip!")
                return ""

        else:
            logging.warning("Microphone not initialized!")
            return ""

    """
    Cleanup thread
    """
    def kill(self):
        self.pAudio.terminate()


        