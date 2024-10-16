"""
Individual component test of the realsense camera
"""
import os
from pathlib import Path
from multiprocessing import Pipe

from helpers import Logging
from time import sleep

from drivers.sensors.MLX90640 import MLX90640

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    path = Path(__file__)
    os.chdir(path.parent.absolute().parent.absolute())

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../../data/"):
            os.mkdir("../../data/")

    logger = Logging()

    _, mlxController = Pipe()
    manager = DriverManager(MLX90640(mlxController))

    while True:
        try:
            print("Sending capture request!")
            manager.setEvent("MLX90640.CAPTURE")
            while manager.getEvent("MLX90640.CAPTURE"):
                sleep(0.1)
            sleep(5)
            print("Capture complete!")

        except KeyboardInterrupt:
            manager.kill()
            exit(0)
