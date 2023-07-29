#!venv/bin/python
"""
Daniel Lau, Oregon State University, 2023
Food Waste Project

Matthew Morgan, Oregon State University, 2023
Food Waste Project

Brayden Morse, Oregon State University-Cascades, 2022
Food Waste Project

Detects whether or not a tray is in place under the camera using the load cell sensor.
Begins with a calibration of the load cell, ultrasonic sensor, and camera.
Once detected, the neopixel light ring lights up and the camera takes a photo.
Utilizes adafruit-blinka library for neopixel ring, HCSR04, and a github library for hx711 sensor.

Credit to Tatobari for the hx711 library
https://github.com/tatobari/hx711py
"""

import time
from datetime import datetime
import requests
import os
from dotenv import load_dotenv
import asyncio
import httpx
import signal
import sys
import argparse

import food_waste.gpio as GPIO
from food_waste.io import PIN, Light, LightStatus, Button, ButtonEvents, WeightSensor, WeightSensorEvents
import food_waste.log as console
from food_waste.api import *

load_dotenv()

argument_parser = argparse.ArgumentParser(description='Detects when food is placed on the scale and sends the data to the cloud for processing.')
argument_parser.add_argument('--dry', action='store_true', help='See how the program would run without sending data to the server.')
argument_parser.add_argument('-v', '--verbose', action='store_true', help='Prints more information to the console. Also enabled by the DEBUG environment variable.')
args = argument_parser.parse_args()

if args['verbose']:
  os.environ['DEBUG'] = 'true'

# TODO: Provide pins
weight_sensor = WeightSensor(None, None)
light = Light(None)
button = Button(None)

def cleanup():
  console.log('Error occurred. Cleaning up and exiting.')
  weight_sensor.cleanup()
  light.cleanup()
  button.cleanup()
  GPIO.cleanup()
  console.log('Done.')

async def main():
  console.log('Starting food waste detection.')
  GPIO.setup_io()

  # setup
  weight_sensor.setup()
  light.setup()
  button.setup()

  try:
    while True:
      button.wait(ButtonEvents.BUTTON_PRESSED)
      now = time.time()
      button.wait(ButtonEvents.BUTTON_RELEASED, timeout=6)
      if time.time() - now > 4.5:
        # TODO: Exit program properly
        cleanup()
        exit(0)
  except Exception as e:
    console.error(e)
  finally:
    cleanup()

loop = asyncio.get_event_loop()

try:
  loop.run_until_complete(main())
except Exception as e:
  cleanup()
