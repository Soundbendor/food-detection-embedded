#!../../venv/bin/python
from time import sleep
from pathlib import Path
import os
import multiprocessing

from helpers import Logging
from drivers.DriverManager import DriverManager
from drivers.sensors.SoundController import SoundController

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    path = Path(__file__)
    os.chdir(path.parent.absolute().parent.absolute())

    logger = Logging(__file__)
    mainControllerConnection, soundControllerConnection = multiprocessing.Pipe()
    manager = DriverManager(SoundController(soundControllerConnection))
    while True:
        try:
            manager.setEvent("SoundController.RECORD")
            while manager.getEvent("SoundController.RECORD"):
                sleep(0.2)

            # Add the transcribed text into the JSON document, only update if value was returned
            transcription = mainControllerConnection.recv()
            if len(transcription) > 1:
                manager.getData()["SoundController"]["data"]["TranscribedText"] = transcription

            print(manager.getJSON())
        except KeyboardInterrupt:
            break

    manager.kill()
    exit(0)