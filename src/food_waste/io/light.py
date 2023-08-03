from .. import gpio as GPIO
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

  def setup(self):
    GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)

  def cleanup(self):
    GPIO.cleanup()

  def set_status(self, status):
    self.status = status
    # TODO: Set the light based on the status
