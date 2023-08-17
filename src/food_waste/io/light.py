from .. import gpio as GPIO
from .. import log as console
import threading
import time

class LightStatus:
  STANDBY = "standby"                 # Device is ready to be used
  ACTIVE = "active"                   # Device is actively waiting for an object to be detected
  OBJECT_DETECTED = "object_detected" # Device has detected an object
  TARING = "taring"                   # Device is taring the scale
  DIRTY = "dirty"                     # Data has been gathered. User may remove object
  SHUTDOWN = "shutdown"               # Device is shutting down
  POWER_OFF = "power_off"             # Device is powered off

class Light:

  def __init__(self, pin):
    self.pin = pin
    self.status = LightStatus.POWER_OFF
    self.loop_thread = None
    self.stopped = False

  def loop(self):
    while not self.stopped:
      if self.status == LightStatus.POWER_OFF:
        time.sleep(0.5)
      else:
        self.activate_light()
    console.debug("Light: Loop thread stopped.")

  def activate_light(self):
    if self.status == LightStatus.STANDBY: # Slow blink
      console.debug(f"Light: Standby mode.")
      self.blink(1, 1)
    elif self.status == LightStatus.ACTIVE: # Medium-speed blink
      console.debug(f"Light: Active mode.")
      self.blink(1, 0.5)
    elif self.status == LightStatus.OBJECT_DETECTED: # Always on
      console.debug(f"Light: Object detected mode.")
      self.power_on()
      time.sleep(0.25)
    elif self.status == LightStatus.TARING: # Fast blink
      console.debug(f"Light: Taring mode.")
      self.blink(1, 0.25)
    elif self.status == LightStatus.DIRTY: # 1 Slow blink, 1 fast blink
      console.debug(f"Light: Dirty mode.")
      self.blink(1, 0.5)
      self.blink(1, 0.25)
    elif self.status == LightStatus.SHUTDOWN: # Two fast blinks, one slow blink
      console.debug(f"Light: Shut down mode.")
      self.blink(2, 0.1)
      self.power_on()
      time.sleep(0.5)
      self.power_off()
      time.sleep(0.1)
    else: # Always off
      console.debug(f"Light: Unknown status or off status - sleeping.")
      time.sleep(0.25)

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
    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    self.stopped = True
    if self.loop_thread is not None:
      self.loop_thread.join()
    self.set_status(LightStatus.POWER_OFF)

  def set_status(self, status):
    """
    Sets the status of the light.
    The status determines the pattern of the light.
    """
    self.status = status
    if status == LightStatus.POWER_OFF:
      self.power_off()
