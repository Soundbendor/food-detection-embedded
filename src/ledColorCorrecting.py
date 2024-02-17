import time

DELAY = 5
NUM_PIXELS = 16

import neopixel_spi as neopixel
import adafruit_fancyled.adafruit_fancyled as fancy
import board
spi = board.SPI()


pixels = neopixel.NeoPixel_SPI(
    spi, NUM_PIXELS, brightness=0.1, auto_write=True, pixel_order=neopixel.GRBW, bit0=0b10000000
)

while True:
    try:
        pixels.fill((0,0,0,255))
        time.sleep(DELAY)
        pixels.fill((252,186,3,0))
        time.sleep(DELAY)
        pixels.fill((0,255,0,0))
        time.sleep(DELAY)
        pixels.fill((255,0,0,0))
        time.sleep(DELAY)
        pixels.fill((0,0,0,0))
        time.sleep(DELAY)
    except KeyboardInterrupt:
        pixels.fill((0,0,0,0))
        break

print("End of test")