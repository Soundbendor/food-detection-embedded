"""
Will Richards, Oregon State University, 2024

Abstraction layer for automated speech recognition (ASR) of recorded audio
"""
import subprocess
import logging

class AudioTranscriber():
    def __init__(self, model="base.en-q5_0"):
        self.modelPath = f"../whisper.cpp/models/ggml-{model}.bin"

    def transcribe(self, inputFile: str):
        full_command = f"../whisper.cpp/main -m {self.modelPath} -f {inputFile} -np -nt"
        process = subprocess.Popen(full_command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # Get the output and error (if any)
        output, error = process.communicate()

        if error:
            logging.error(f"Error proccessing audio: {error.decode('utf-8')}")

        # Process and return the output string
        decoded_str = output.decode('utf-8').strip()
        processed_str = decoded_str.replace('[BLANK_AUDIO]', '').strip()

        return processed_str
        