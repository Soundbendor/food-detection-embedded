"""
Individual component test of the lid switch
"""
import os
import logging
from pathlib import Path

from helpers import Logging, RequestHandler
from time import sleep

from drivers.DriverManager import DriverManager

if __name__ == "__main__":
    # Change our current working directory to this file so our relative paths still work no matter where this file was called from
    path = Path(__file__)
    os.chdir(path.parent.absolute().parent.absolute())

    # Create our data folder if it doesn't exist already
    if not os.path.exists("../data/"):
            os.mkdir("../data/")

    logger = Logging()
    requests = RequestHandler("../data")

    logging.info("Attempting to send heartbeat...")
    requests.sendHeartbeat()

    logging.info("Attempting to send complete API request files...")
    exampleData = {'LEDDriver': {'data': {'initialized': 1}, 'events': {'CAMERA': [False, None], 'PROCESSING': [False, None], 'DONE': [False, None], 'NONE': [False, None], 'ERROR': [False, None]}}, 'NAU7802': {'data': {'weight': 4.216175274216712, 'weight_delta': 2.6806743905518453, 'initialized': 1}, 'events': {'WEIGHT_CHANGE': [False, None], 'CALIBRATE': [False, None]}}, 'BME688': {'data': {'temperature(c)': 19.61, 'pressure(kpa)': 102.096, 'humidity(%rh)': 46.77, 'gas_resistance(ohms)': 25376.685170499604, 'iaq': 25.0, 'sIAQ': 25.0, 'CO2-eq': 500.0, 'bVOC-eq': 0.4999999403953552, 'initialized': 1}, 'events': {}}, 'MLX90640': {'data': {'initialized': 1}, 'events': {'CAPTURE': [False, None]}}, 'LidSwitch': {'data': {'Lid_State': 1, 'initialized': 1}, 'events': {'LID_OPENED': [True, None], 'LID_CLOSED': [True, None]}}, 'Realsense': {'data': {'initialized': 1}, 'events': {'CAPTURE': [False, None]}}, 'SoundController': {'data': {'TranscribedText': 'Tomatoes.', 'initialized': 1}, 'events': {'RECORD': [False, None]}}, 'DriverManager': {'data': {'userTrigger': True}, 'events': {}}}
    requests.sendAPIRequest({}, exampleData)