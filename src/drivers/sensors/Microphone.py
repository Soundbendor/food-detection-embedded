"""
Will Richards, Oregon State University, 2023

Provides a functionality to interface with a standard USB microphone using a USB Audio DAC and PyAudio
"""

import logging
from cv2 import exp
import pyaudio
import wave
from pydub import AudioSegment as am
import os
import numpy as np
import whisper
import torch
import numpy as np

class Microphone():
    def __init__(self, record_duration):

        # Audio recording parameters
        self.sampling_rate = 44100
        self.downsample_rate = 16000
        self.device_index = 11
        self.frames_per_buffer = 128
        self.format = pyaudio.paInt16
        self.record_duration = record_duration

        self.pAudio = pyaudio.PyAudio()
        self.initialized = True

        # Load the silero-vad Voice Activation Model to reduce overall inference time by ignoring audio with no voice in it
        self.model, utils = torch.hub.load(repo_or_dir='snakers4/silero-vad',model='silero_vad',force_reload=True,onnx=False)
        (self.get_speech_timestamps, self.save_audio, self.read_audio,_, self.collect_chunks) = utils

        # Attempt to open the microphone stream
        try:
            self.stream = self.pAudio.open(
                format=pyaudio.paInt16,
                rate = self.sampling_rate,
                input=True,
                channels=1,
                input_device_index=self.device_index,
                frames_per_buffer=self.frames_per_buffer,
                start=False,
            )
        except Exception as e:
            logging.error("Failed to open audio input device: {e}")
            self.initialized = False

    """
    Initialize the whisper model and warm it up by feeding 0s into it
    """
    def initialize(self):
        if(self.initialized):
            logging.info("Loading model...")
            self.asrModel = whisper.load_model("base.en")
            logging.info("Loading complete! Warming up model...")
            whisper.transcribe(model=self.asrModel, audio=np.zeros(self.record_duration * self.downsample_rate, np.float32), fp16=False)
            logging.info("Model has been warmed up! Ready for inference")
            
    """
    Write some audio data out to a .wav file
    """
    def writeWave(self, data, outputFile):
        # Write the pre downsampled audio to .wav file
        wf = wave.open(outputFile, "wb")
        wf.setnchannels(1)
        wf.setsampwidth(self.pAudio.get_sample_size(self.format))
        wf.setframerate(self.sampling_rate)
        wf.writeframes(b''.join(data))
        wf.close()

    """
    Downsample a given audio file to 16khz, and then remove the previous file
    """
    def downsampleAudio(self, inputFile, outputFile):
        logging.info("Downsampling Audio....")
        sound = am.from_file(inputFile, format="wav", frame_rate=self.sampling_rate)
        sound = sound.set_frame_rate(self.downsample_rate)
        sound.export(outputFile, format="wav")
        os.remove(inputFile)

    """
    Record audio from the microphone and write it to a file
    """
    def _record(self, outputFile):
        frames = []

        logging.info("RECORDING....")
        self.stream.start_stream()

        for _ in range(0, int(self.sampling_rate / self.frames_per_buffer * self.record_duration)):
            data = self.stream.read(self.frames_per_buffer, exception_on_overflow=False)
            frames.append(data)

        self.stream.stop_stream()

        self.writeWave(frames, outputFile)
        logging.info("STOPPED RECORDING")
    
    """
    Utilize the Silero-VAD model to determine if a given audio contains speaking

    Return true or false, if true write spoken parts to a file
    """
    def detectSpeaking(self, inputFile, outputFile) -> bool:
        logging.info("Detecting speaking....")
        wav = self.read_audio(inputFile, sampling_rate=self.downsample_rate)
        speech_timestamps = self.get_speech_timestamps(wav, self.model, sampling_rate=self.downsample_rate)
        if(len(speech_timestamps) > 0):
            self.save_audio(outputFile, self.collect_chunks(speech_timestamps, wav), sampling_rate=self.downsample_rate) 
            return True
        return False
    
    """
    Utilize the whisper model to transcribe a given input file into the text
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
            self._record("../data/preDownsampledAudio.wav")
            self.downsampleAudio("../data/preDownsampledAudio.wav", "../data/downsampledAudio.wav")
            if(self.detectSpeaking("../data/downsampledAudio.wav", "../data/only_speech.wav")):
                transcibedText = self.transcribe('../data/only_speech.wav')
                #logging.info(f"Transcribed Text: {transcibedText}")
                os.remove('../data/only_speech.wav')
                return transcibedText
            else:
                logging.warning("No speaking detected in clip!")
                return ""
                # TODO: If no speaking was detected in the clip we probably want to prompt the user for what was put in again

        else:
            logging.warning("Microphone not initialized!")
            return ""



    def kill(self):
        if self.initialized:
            self.stream.close()
        self.pAudio.terminate()


        