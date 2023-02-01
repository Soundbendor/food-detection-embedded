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
from hx711 import HX711
from datetime import datetime
import requests
from PIL import Image
import os
from dotenv import load_dotenv

load_dotenv()

def WasteDetectionCalibration():
    
    # Yellow for Calibration Phase
    pixels.fill((255,200,0))
    print('Calibration in Progress: Ultrasonic Sensor')

    # Ultrasonic Sensor Calibration: 5 point average with a 0.125 sec delay between to try to eliminate outliers.
    dist1 = 0 
    sumDist = distance()
    for i in range(4):
        dist1 = distance()
        sumDist = dist1 + sumDist
        time.sleep(0.125)
    initDist = sumDist / 5
    
    # Load Cell Calibration. Uses a lot of the HX711 library.
    print('Calibration in Progress: Loadcell Sensor')
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(87)
    hx.reset()
    hx.tare(times = 5)
    
    # Camera calibration image. Lights up and takes an image and waits a bit
    print('Calibration in Progress: Camera')
    pixels.fill((255,255,100))
    camera.capture('/home/pi/Desktop/FoodWaste/Images/calibrationimage.jpg')
    time.sleep(0.5)
    
    # Green! Ready to go!
    print('Calibration Complete!')
    pixels.fill((0,255,0))
    time.sleep(0.75)
    
    # No lights until something is detected under the camera.
    #pixels.fill((0,0,0))
    
    return initDist
 
# Manually reads the pmw from the ultrasonic sensor. More consistent than the adafruit library using the pulseio library.
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

# Grabs the weight from the load cell using the hx711 library.
def weight():
    weight = 0
    try:
        weight = hx.get_weight()
        hx.power_down()
        hx.power_up()
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
    return weight
    
# Main Detection function. accepts 
def WasteDetection(initDistance = 0):
    # Distance delta and weight delta
    dist = initDistance - distance()
    weightgram = weight()
        
    # Ambient light to know that the system is on.
    pixels.fill((25,25,10))
    print('Weight: {:0.2f}kg   Distance Change: {:0.1f}cm'.format(abs(weightgram/1000), abs(dist)))
    
    # Main detection Conditions. dist = distance delta in cm, weightgram = weight delta in grams
    if dist >= 0.5 and weightgram >= 200:
        # Print and light up the scene / tray.
        print('Object detected')
        pixels.fill((255,255,50))
        time.sleep(0.25)
        # Gets Current Time
        now = "{};{};{}".format(datetime.now().time().hour,
                                datetime.now().time().minute,
                                datetime.now().time().second)
        
        # Makes the name of the file and the location for capture and displaying.
        ImageName = 'waste{}.jpg'.format(now)
        ImageLocation = '/home/pi/Desktop/FoodWasteImages/waste{}.jpg'.format(now)
        
        # Annotates the text with distance, time, weight and captures the image.
        # camera.annotate_text = "Captured: {} \n Weight: {:0.2f} Distance: {:0.2f}".format(now, weightgram, dist) 

        camera.capture(ImageLocation)
        
        imageCapture = ImageLocation
        
        print('Picture Taken {:0.1f} {:0.1f}'.format(dist,weightgram))
        
        # Sent off image and wait for return
        try:
            ApiReturnFile = postImage(imageFile = imageCapture, imagename = ImageName)
            #Opens the new image 
            #im = Image.open(ApiReturnFile)
            #im.show()
        except Exception as e:
            print(e)
            print('PostImage Failed. Likely exceeded retries.')
            #im = Image.open(ImageLocation)
            #im.show()
            pass
        time.sleep(1)
        
        pixels.fill((0,255,0))
        time.sleep(0.5)
        
        # Re-polls weight and distance to determine if the tray is still there
        while (initDistance - distance()) >= 0.5 and weight() >= 200:
            print('Tray is still there Dist: {:0.1f} Weight: {:0.1f}'.format(distance(),weight()))
            time.sleep(1)
        return
      
      
def postImage(imageFile = 'Images/calibrationimage.jpg', imagename = 'calibrationimage.jpg'):    
    files = {'img_file': (imageFile, open(imageFile, 'rb'), 'image/jpg')}
    
    #request = requests.post('https://127.0.0.1:8001/api/model/detect_v1', data = {'img_name': imagename}, files = files)    
    
    apikey = os.getenv("API_KEY")
    authorization = os.getenv("PROXY_LOGIN")
    request = requests.post(f'{ngrok_url}/api/model/detect', data = {'img_name': imagename},
                            headers={'token': apikey, 'Authorization':authorization}, files = files)    
    
    
    #request = requests.post('https://10.217.116.7:8000/api/model/detect_v1', data = {'img_name': imagename}, files = files)    
                         
    # Appends the file to know which is the returned image
    apiFile = imageFile + 'apiReturn'
    
    # Create the file and write the request content to it.
    FileReturn = open(apiFile, 'wb')
    FileReturn.write(request.content)
    FileReturn.close()
    return apiFile
    
#GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)
 
#set GPIO Pins
GPIO_TRIGGER = 12
GPIO_ECHO = 16
 
#set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)

# Neopixel Led pins
pixelsPin = board.D18

#----- Startup procedure / calibration -----
# Setup Camera object and neopixel object
camera = picamera.PiCamera()
pixels = neopixel.NeoPixel(pixelsPin, 16)
hx = HX711(5, 6)

# Button to recalibrate the sensors
caliButton = board.D21
calibrateButton = digitalio.DigitalInOut(caliButton)
calibrateButton.direction = digitalio.Direction.INPUT
calibrateButton.pull = digitalio.Pull.UP

print('Getting ngrok link')
response = requests.get(os.getenv("PROXY_ID_NUM")) 
ngrok_url = f"https://{response.text.strip()}.ngrok.io"
print('Ngrok link:', response.status_code, ngrok_url)

initdist = WasteDetectionCalibration()

#----- Main Loop -----
try:
    while True:
        try:
            WasteDetection(initDistance = initdist)
            time.sleep(1)
            if calibrateButton.value == False:
                initdist = WasteDetectionCalibration()
            
        except RuntimeError:
            print('Timed Out RuntimeError')
            #GPIO.cleanup()
            time.sleep(1.5)
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
        

