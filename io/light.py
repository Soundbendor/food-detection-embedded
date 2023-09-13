from .. import gpio as GPIO
from .. import log as console
import time

class LightComponent:

  def __init__(self, pin):
    self.pin = pin

  def blink(self, count, duration):
    """
    Blinks the light a specified number of times with a specified duration.

    :param count: The number of times to blink the light.
    :param duration: The duration of each blink.
    """
    for _ in range(count):
      self.power_on()
      time.sleep(duration)
      self.power_off()
      time.sleep(duration)

  def power_on(self):
    """
    Turns the light on.
    """
    GPIO.output(self.pin, GPIO.HIGH)

  def power_off(self):
    """
    Turns the light off.
    """
    GPIO.output(self.pin, GPIO.LOW)

  def setup(self):
    GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

  def cleanup(self):
    pass
