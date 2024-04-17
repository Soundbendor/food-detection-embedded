"""
Individual component test of the lid switch
"""
import os
import logging
from pathlib import Path

from helpers import Logging, RequestHandler
from time import sleep

from drivers.NetworkDriver import WiFiManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    path = Path(__file__)
    os.chdir(path.parent.absolute().parent.absolute())

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../data/"):
            os.mkdir("../data/")

    logger = Logging(__file__)
    wifi = WiFiManager()

    