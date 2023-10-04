from .. import log as console
import pyaudio
import wave

CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 8000
RECORD_SECONDS = 5

class Microphone:

  def __init__(self):
    self.audio = None
    self.stream = None

  def setup(self):
    self.audio = pyaudio.PyAudio()

  def record(self, seconds = RECORD_SECONDS):
    console.debug("Microphone: Recording.")
    self.stream = self.audio.open(
      format=FORMAT,
      channels=CHANNELS,
      rate=RATE,
      input=True
    )
    frames = []
    for i in range(0, int(RATE / CHUNK * seconds)):
      data = self.stream.read(CHUNK)
      frames.append(data)

    console.debug("Microphone: Recording finished.")

    self.stream.close()
    self.audio.terminate()
    self.setup()
    return frames

  def cleanup(self):
    if self.stream is not None:
      self.stream.close()
    if self.audio is not None:
      self.audio.terminate()
