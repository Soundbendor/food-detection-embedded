#!venv/bin/python
"""
Matthew Morgan, Oregon State University, 2023
Food Waste Project

Brayden Morse, Oregon State University-Cascades, 2022
Food Waste Project

Detects whether or not a tray is in place under the camera using ultrasonic sensor
and load cell sensor. Begins with a calibration of the load cell, ultrasonic sensor, and camera.
Once detected, the neopixel light ring lights up and the camera takes a photo.
Utilizes adafruit-blinka library for neopixel ring, HCSR04, and a github library for hx711 sensor.

Credit to Tatobari for the hx711 library
https://github.com/tatobari/hx711py
"""

import picamera
import time
import board
import digitalio
import neopixel
import RPi.GPIO as GPIO
from datetime import datetime
import requests
from PIL import Image
import os
from dotenv import load_dotenv
import asyncio
import httpx
import sys

# Local code
import helper_functions.api_calls as api_calls
from helper_functions.hx711 import HX711
import helper_functions.initialize_sensors as init_sensors
import helper_functions.measure_sensor as measure_sensor


load_dotenv()

#set GPIO Pins constants
GPIO_TRIGGER = 12
GPIO_ECHO = 16

httpx_client = httpx.AsyncClient()

args = sys.argv
SHOW_IMAGES_ON_PI_DESKTOP = len(args) > 1 and args[1] == 'show'


# Main Detection function.
async def run_waste_detection(remote_url, initDistance = 0):
    # Distance delta and weight delta
    dist = initDistance - measure_sensor.measure_distance(GPIO, GPIO_TRIGGER, GPIO_ECHO)
    weightgram = measure_sensor.measure_weight(GPIO, hx)
        
    # Ambient light to know that the system is on.
    pixels.fill((25,25,10))
    print('Weight: {:0.2f}kg   Distance Change: {:0.1f}cm'.format(abs(weightgram/1000), abs(dist)))
    
    if dist < -500:
        print('Detected stop from ultrasonic sensors, waiting 1 second.')
        await asyncio.sleep(1)
        if dist < -500:
            raise StopIteration

    # Main detection Conditions. dist = distance delta in cm, weightgram = weight delta in grams
    if dist >= 0.4 and weightgram >= 100:
        # Print and light up the scene / tray.
        print('Object detected')
        pixels.fill((200,200,30))
        time.sleep(0.50)
        # Gets Current Time
        curr_datetime_str = "{}-{}-{}__{}-{}-{}".format(
            datetime.now().year,
            datetime.now().month,
            datetime.now().day,
            datetime.now().hour,
            datetime.now().minute,
            datetime.now().second)
        
        # Makes the name of the file and the location for capture and displaying.
        image_name = 'waste_{}.jpg'.format(curr_datetime_str)
        image_location = f'archive_detection_images/pre_detection_{image_name}.jpg'
        
        # Annotates the text with distance, time, weight and captures the image.
        # camera.annotate_text = "Captured: {} \n Weight: {:0.2f} Distance: {:0.2f}".format(curr_datetime_str, weightgram, dist) 

        camera.capture(image_location)
        
        print('Picture Taken {:0.1f} {:0.1f}'.format(dist,weightgram))
        
        if SHOW_IMAGES_ON_PI_DESKTOP:
            # Opens the new image 
            im = Image.open(image_location)
            im.show()

        # Send off image as a background task
        post_detection_image_location = asyncio.create_task(api_calls.post_image_for_detection(remote_url, httpx_client, image_location, image_name))

        await asyncio.sleep(1)
        
        # Show green for the user.
        pixels.fill((0,255,0))
        await asyncio.sleep(0.5)
        
        # Re-polls weight and distance to determine if the tray is still there.
        while (initDistance - measure_sensor.measure_distance(GPIO, GPIO_TRIGGER, GPIO_ECHO)) >= 0.4 and measure_sensor.measure_weight(GPIO, hx) >= 100:
            print('Tray is still there Dist: {:0.1f} Weight: {:0.1f}'.format(measure_sensor.measure_distance(GPIO, GPIO_TRIGGER, GPIO_ECHO), measure_sensor.measure_weight(GPIO, hx)))
            time.sleep(1)
        return
      

#----- Startup procedure / calibration -----

init_sensors.setup_gpio(GPIO, GPIO_TRIGGER, GPIO_ECHO)

# Neopixel Led pins
pixelsPin = board.D18

# Setup Camera object and neopixel object
camera = picamera.PiCamera()
pixels = neopixel.NeoPixel(pixelsPin, 16)
hx = HX711(5, 6)

calibrateButton = init_sensors.setup_button(board, digitalio)


async def main():
    print('Starting food detector!')

    pixels.fill((70,0,0))
    if not api_calls.check_for_secrets():
        return

    ngrok_url_task = asyncio.create_task(api_calls.get_ngrok_link(httpx_client))

    initdist = init_sensors.calibrate_sensors(pixels, hx, camera, measure_sensor.measure_distance, GPIO, GPIO_TRIGGER, GPIO_ECHO)

    await ngrok_url_task
    ngrok_url = ngrok_url_task.result()
    if ngrok_url is None:
        return
    print("ngrok link:", ngrok_url)

    # Set lights green! Ready to go!
    pixels.fill((0,255,0))
    await asyncio.sleep(0.5)

    #----- Main Loop -----
    try:
        while True:
            try:
                await run_waste_detection(ngrok_url, initDistance = initdist)
                await asyncio.sleep(1)
                if calibrateButton.value == False:
                    initdist = calibrate_sensors(pixels, hx, camera, measure_sensor.measure_distance, GPIO, GPIO_TRIGGER, GPIO_ECHO)
                
            except RuntimeError as e:
                if 'Keyboard' in str(e):
                    print('Keyboard interupt, quitting')
                    return
                elif 'StopIteration' in str(e):
                    print('Detected second stop from ultrasonic sensors, quitting.')
                    return

                print('RuntimeError, request likely timed out.')
                #GPIO.cleanup()
                await asyncio.sleep(1.5)
                pass
            except Exception as e:
                print(e)
            
    except Exception as e:
        print(e)
        pass

    finally:
        pixels.fill((0,0,0))
        GPIO.cleanup()
        print('Error Encountered: GPIO cleaned up, all done')

loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(main())
except Exception as e:
    print(e)
    pass

finally:
    pixels.fill((0,0,0))
    GPIO.cleanup()
    print('Error Encountered: GPIO cleaned up, all done')
