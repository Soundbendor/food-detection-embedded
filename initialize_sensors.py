import time

#----- Functions to set up sensors: -----

def setup_gpio(GPIO, gpio_trigger, gpio_echo):
    #GPIO Mode (BOARD / BCM)
    GPIO.setmode(GPIO.BCM)

    #set GPIO direction (IN / OUT)
    GPIO.setup(gpio_trigger, GPIO.OUT)
    GPIO.setup(gpio_echo, GPIO.IN)


def setup_button(board, digitalio):
    # Button to recalibrate the sensors
    cali_button = board.D21
    calibrateButton = digitalio.DigitalInOut(cali_button)
    calibrateButton.direction = digitalio.Direction.INPUT
    calibrateButton.pull = digitalio.Pull.UP
    return calibrateButton


def calibrate_sensors(pixels, hx, camera, measure_distance_func, GPIO, gpio_trigger, gpio_echo):
    
    # Yellow for Calibration Phase
    pixels.fill((255,200,0))
    print('Calibration in Progress: Ultrasonic Sensor')

    # Ultrasonic Sensor Calibration: 5 point average with a 0.125 sec delay between to try to eliminate outliers.
    dist1 = 0 
    sumDist = measure_distance_func(GPIO, gpio_trigger, gpio_echo)
    for i in range(4):
        dist1 = measure_distance_func(GPIO, gpio_trigger, gpio_echo)
        sumDist = dist1 + sumDist
        time.sleep(0.125)
    initDist = sumDist / 5
    
    # Load Cell Calibration. Uses a lot of the HX711 library.
    print('Calibration in Progress: Loadcell Sensor')
    hx.set_reading_format("MSB", "MSB")
    hx.set_reference_unit(87)
    hx.reset()
    hx.tare(times = 5)
    
    # Camera calibration image. Lights up and takes an image and waits a bit.
    print('Calibration in Progress: Camera')
    pixels.fill((255,255,100))
    camera.capture('/home/pi/Desktop/FoodWaste/Images/calibrationimage.jpg')
    time.sleep(0.5)
    
    # Sensors ready, set color to blue.
    print('Calibration Complete!')
    pixels.fill((0,0,200))
    time.sleep(0.75)
    
    # No lights until something is detected under the camera.
    #pixels.fill((0,0,0))
    
    return initDist
