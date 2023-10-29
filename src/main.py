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

import Jetson.GPIO
from food_waste.use_gpio import use_gpio
use_gpio(Jetson.GPIO)

import food_waste.gpio as GPIO
from system.io import Camera, StatusLight, TareButton, TareButtonStatus, WeightSensor, DepthCamera
import food_waste.log as console
from food_waste.api import ImageApi, MissingSecretsError, RequestFailedError

load_dotenv()

dirname = os.path.dirname(os.path.realpath(__file__))

argument_parser = argparse.ArgumentParser(description='Detects when food is placed on the scale and sends the data to the cloud for processing.')
argument_parser.add_argument('--dry', action='store_true', help='See how the program would run without sending data to the server.')
argument_parser.add_argument('-v', '--verbose', action='store_true', help='Prints more information to the console. Also enabled by the DEBUG environment variable.')
args = argument_parser.parse_args()

if args.verbose:
  console.log("Debug mode enabled.")
  os.environ['DEBUG'] = 'true'

if args.dry:
  console.log("Dry run enabled.")

httpx_client = httpx.AsyncClient(timeout=60.0)
image_api = ImageApi(
  httpx_client,
  "http://ec2-54-214-80-154.us-west-2.compute.amazonaws.com"
)
weight_sensor = WeightSensor()
light = StatusLight()
button = TareButton()
camera = Camera()
depth_camera = DepthCamera()

def cleanup():
  console.log('Cleaning up.')
  weight_sensor.cleanup()
  light.cleanup()
  button.cleanup()
  GPIO.cleanup()
  camera.cleanup()
  depth_camera.cleanup()
  console.log('Done.')

def get_date_string():
  now = datetime.now()
  return "{}-{}-{}__{}-{}-{}".format(
    now.year,
    now.month,
    now.day,
    now.hour,
    now.minute,
    now.second)

def get_image_name():
  return f"waste_{get_date_string()}"

def generate_image_path(name):
  base_dir = "archive_check_focus_images" if args.dry else "archive_detection_images"
  if not os.path.exists(base_dir):
    os.makedirs(base_dir)
  fname = f"pre_detection_{name}.jpg"
  return os.path.normpath(
    os.path.join(dirname, "..", base_dir, fname)
  )

async def main():
  console.log('Starting food waste detection.')
  GPIO.setup_io()

  # setup
  console.debug("Setting up devices.")
  weight_sensor.setup()
  light.setup()
  button.setup()
  camera.setup()
  depth_camera.setup()

  light.standby()

  try:
    while True:
      try:
        status = button.wait_and_get_status()
        if status == TareButtonStatus.POWER_OFF:
          console.log("Shutoff request detected. Exiting.")
          break
        else:
          console.log("Activation button pressed. Taring scale.")
          light.taring()
          weight_sensor.tare()

          await asyncio.sleep(2)

          console.log("Waiting for object to be placed on scale.")
          light.active()
          if (not weight_sensor.wait_object_detected()):
            console.log("No object detected. Returning to standby.")
            light.standby()
            continue

          console.log("Object detected. Gathering data.")
          light.object_detected()
          object_weight = weight_sensor.measure()
          image_name = get_image_name()
          image_path = generate_image_path(image_name)
          camera.save(image_path)
          depth_path = generate_image_path(f"{image_name}_depth")
          depth_camera.save(depth_path, depth_camera.capture_map())

          console.log("Photo taken. Uploading to server.")
          light.dirty()
          if not args.dry:
            # Uploads to the server in the background
            loop = asyncio.get_event_loop()
            loop.create_task(image_api.post_image(
              image_path=image_path,
              image_name=image_name,
              depth_image_path=depth_path,
              weight=object_weight
            ))

          await asyncio.sleep(2)

          console.log("Waiting for object to be removed.")
          weight_sensor.wait_for_removal()

          console.log("Object removed. Returning to standby.")
          light.standby()
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
