import gpiod
import time
LED_PIN = 17
chip = gpiod.Chip('gpiochip4')
led_line = chip.get_line(LED_PIN)
led_line.request(consumer="Button", type=gpiod.LINE_REQ_DIR_IN)
try:
   while True:
       print(led_line.get_value())
       time.sleep(1)
finally:
   led_line.release()
