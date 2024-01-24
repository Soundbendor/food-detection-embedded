#!../venv/bin/python

from time import sleep
import logging 
from drivers.sensors.RealsenseCamera import RealsenseCam

FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'

if __name__ == "__main__":
    logging.basicConfig(format=FORMAT, level=logging.INFO)
    camera = RealsenseCam()
    camera.initialize()
    while True:
        try:
            camera.events["CAPTURE"].set()
            camera.measure()
        except KeyboardInterrupt:
            camera.kill()
            break