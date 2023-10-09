#!./../../venv/bin/python
"""
Will Richards, Oregon State University, 2023

Provides a basic runnable test to check functionality of HX711
"""
from ..drivers.HX711 import HX711
import RPi.GPIO as GPIO
import logging

from time import sleep

SHOULD_CALIBRATE = True

def main():
    # Create a new sensor, using the defaults is fine here
    hx711 = HX711()

    # Initialize the sensor and conduct a measurement
    hx711.initialize()
    if SHOULD_CALIBRATE == True:
        logging.info("Preforming calibration...")
        hx711.calibrate()
    else:
        logging.info("Sensor initialized and values have been torn... Waiting 10 seconds for weight to be supplied")
        sleep(10)

    # Measure and print out reading
    while True:
        try:
            logging.info(f"Data measured from HX711: {hx711.measure()}")
            sleep(1)
        except KeyboardInterrupt:
            break

    # Cleanup GPIO beore we exit
    GPIO.cleanup()


# Run main as soon as the script starts
if __name__ == "__main__":

    # Configure Logger
    FORMAT = '%(asctime)s [%(filename)s:%(funcName)s:%(lineno)d] [%(levelname)s] %(message)s'
    logging.basicConfig(format=FORMAT, level=logging.INFO, handlers=[logging])

    main()