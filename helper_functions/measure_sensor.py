import time

#----- Functions for measuring data from sensors: -----

# Manually reads the pmw from the ultrasonic sensor. More consistent than the adafruit library using the pulseio library.
def measure_distance(GPIO, gpio_trigger, gpio_echo):
    # set Trigger to HIGH
    GPIO.output(gpio_trigger, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(gpio_trigger, False)
 
    start_time = time.time()
    stop_time = time.time()
 
    # save start_time
    while GPIO.input(gpio_echo) == 0:
        start_time = time.time()
 
    # save time of arrival
    while GPIO.input(gpio_echo) == 1:
        stop_time = time.time()
 
    # time difference between start and arrival
    TimeElapsed = stop_time - start_time
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance

# Grabs the weight from the load cell using the hx711 library.
def measure_weight(GPIO, hx):
    weight = 0
    try:
        weight = hx.get_weight()
        hx.power_down()
        hx.power_up()
    except (KeyboardInterrupt, SystemExit):
        GPIO.cleanup()
    return weight
