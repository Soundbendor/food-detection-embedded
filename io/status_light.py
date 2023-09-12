from .component import LightComponent
from . import PIN
from .. import log as console
import threading
import time

class StatusLightStatus:
  STANDBY = "standby"                 # Device is ready to be used
  ACTIVE = "active"                   # Device is actively waiting for an object to be detected
  OBJECT_DETECTED = "object_detected" # Device has detected an object
  TARING = "taring"                   # Device is taring the scale
  DIRTY = "dirty"                     # Data has been gathered. User may remove object
  SHUTDOWN = "shutdown"               # Device is shutting down
  POWER_OFF = "power_off"             # Device is powered off

class StatusLight(LightComponent):

  def __init__(self, pin=PIN.LIGHT):
    super().__init__(pin)
    self.loop_thread = None
    self.stopped = False
    self.status = StatusLightStatus.POWER_OFF

  def loop(self):
    while not self.stopped:
      if self.status == StatusLightStatus.POWER_OFF:
        time.sleep(0.5)
      else:
        self.activate_light()
    console.debug("StatusLight: Loop thread stopped.")

  def setup(self):
    super().setup()
    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    super().cleanup()
    self.stopped = True
    if self.loop_thread is not None:
      self.loop_thread.join()
    self.set_status(StatusLightStatus.POWER_OFF)

  def activate_light(self):
    if self.status == StatusLightStatus.STANDBY: # Slow blink
      console.debug(f"StatusLight: Standby mode.")
      self.blink(1, 1)
    elif self.status == StatusLightStatus.ACTIVE: # Medium-speed blink
      console.debug(f"StatusLight: Active mode.")
      self.blink(1, 0.5)
    elif self.status == StatusLightStatus.OBJECT_DETECTED: # Always on
      console.debug(f"StatusLight: Object detected mode.")
      self.power_on()
      time.sleep(0.25)
    elif self.status == StatusLightStatus.TARING: # Fast blink
      console.debug(f"StatusLight: Taring mode.")
      self.blink(1, 0.25)
    elif self.status == StatusLightStatus.DIRTY: # 1 Slow blink, 1 fast blink
      console.debug(f"StatusLight: Dirty mode.")
      self.blink(1, 0.5)
      self.blink(1, 0.25)
    elif self.status == StatusLightStatus.SHUTDOWN: # Two fast blinks, one slow blink
      console.debug(f"StatusLight: Shut down mode.")
      self.blink(2, 0.1)
      self.power_on()
      time.sleep(0.5)
      self.power_off()
      time.sleep(0.1)
    else: # Always off
      console.debug(f"StatusLight: Unknown status or off status - sleeping.")
      time.sleep(0.25)

  def set_status(self, status):
    """
    Sets the status of the light.
    The status determines the pattern of the light.
    """
    self.status = status
    if status == StatusLightStatus.POWER_OFF:
      self.power_off()

  def standby(self):
    self.set_status(StatusLightStatus.STANDBY)

  def taring(self):
    self.set_status(StatusLightStatus.TARING)

  def active(self):
    self.set_status(StatusLightStatus.ACTIVE)

  def object_detected(self):
    self.set_status(StatusLightStatus.OBJECT_DETECTED)

  def dirty(self):
    self.set_status(StatusLightStatus.DIRTY)
