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

if args.verbose:
  os.environ['DEBUG'] = 'true'

httpx_client = httpx.AsyncClient()
image_api = ImageApi(
  httpx_client,
  "http://ec2-54-244-119-45.us-west-2.compute.amazonaws.com"
)
weight_sensor = WeightSensor(PIN.WEIGHT_CLK, PIN.WEIGHT_DAT)
light = Light(PIN.LIGHT)
button = Button(PIN.BUTTON)

def cleanup():
  console.log('Cleaning up.')
  weight_sensor.cleanup()
  light.cleanup()
  button.cleanup()
  GPIO.cleanup()
  console.log('Done.')

async def main():
  console.log('Starting food waste detection.')
  GPIO.setup_io()

  # setup
  console.debug("Setting up devices.")
  weight_sensor.setup()
  light.setup()
  button.setup()

  light.set_status(LightStatus.STANDBY)

  try:
    while True:
      try:
        console.debug("Waiting for button press.")
        button.wait(ButtonEvents.BUTTON_PRESSED)
        now = time.time()
        button.wait(ButtonEvents.BUTTON_RELEASED, timeout=6)
        console.debug(f"Button pressed for {time.time() - now} seconds.")
        if time.time() - now > 5:
          console.log("Shutoff request detected. Exiting.")
          cleanup()
          break
        else:
          console.log("Activation button pressed. Taring scale.")
          light.set_status(LightStatus.TARING)
          weight_sensor.tare()

          console.log("Waiting for object to be placed on scale.")
          light.set_status(LightStatus.ACTIVE)
          now = time.time()
          weight_sensor.wait(WeightSensorEvents.OBJECT_DETECTED, timeout=60)
          console.debug(f"Object detected after {time.time() - now} seconds.")
          if time.time() - now > 59:
            console.log("No object detected. Returning to standby.")
            light.set_status(LightStatus.STANDBY)
            continue

          console.log("Object detected. Gathering data.")
          light.set_status(LightStatus.OBJECT_DETECTED)
          # TODO: Take photo

          console.log("Photo taken. Uploading to server.")
          light.set_status(LightStatus.DIRTY)
          if args.dry:
            pass
          else:
            # Uploads to the server in the background
            asyncio.create_task(image_api.post_image("TODO.jpg", "TODO.jpg"))
      except RuntimeError as e:
        if 'Keyboard' in str(e):
          console.warning("Keyboard interrupt detected. Exiting.")
          break
  except Exception as e:
    console.error("An error ocurred during execution", e)
  finally:
    cleanup()

loop = asyncio.get_event_loop()

try:
  loop.run_until_complete(main())
except Exception as e:
  console.error("An error ocurred during execution", e)
  cleanup()