from .. import gpio as GPIO
from .. import log as console
import threading
import time

class LightStatus:
  STANDBY = "standby"                 # Device is ready to be used
  ACTIVE = "active"                   # Device is actively waiting for an object to be detected
  OBJECT_DETECTED = "object_detected" # Device has detected an object, user may remove object
  TARING = "taring"                   # Device is taring the scale
  DIRTY = "dirty"                     # TODO: Confirm whether this status is needed
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
        time.sleep(0.25)
      else:
        self.activate_light()
    console.debug("Light: Loop thread stopped.")

  def activate_light(self):
    match self.status:
      case LightStatus.STANDBY: # Slow blink
        console.debug(f"Light: Standby mode.")
        power_on()
        time.sleep(1)
        power_off()
        time.sleep(1)
      case LightStatus.ACTIVE: # Medium-speed blink
        console.debug(f"Light: Active mode.")
        power_on()
        time.sleep(0.5)
        power_off()
        time.sleep(0.5)
      case LightStatus.OBJECT_DETECTED: # Always on
        console.debug(f"Light: Object detected mode.")
        power_on()
        time.sleep(0.25)
      case LightStatus.TARING: # Fast blink
        console.debug(f"Light: Taring mode.")
        power_on()
        time.sleep(0.25)
        power_off()
        time.sleep(0.25)
      case LightStatus.DIRTY: # Slow blink
        console.debug(f"Light: Dirty mode.")
        power_on()
        time.sleep(1)
        power_off()
        time.sleep(1)
      case LightStatus.SHUTDOWN: # Two fast blinks, one slow blink
        console.debug(f"Light: Shut down mode.")
        power_on()
        time.sleep(0.1)
        power_off()
        time.sleep(0.1)
        power_on()
        time.sleep(0.5)
      case _: # Always off
        console.debug(f"Light: Unknown status or off status - sleeping.")
        time.sleep(0.25)

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
      power_off()
