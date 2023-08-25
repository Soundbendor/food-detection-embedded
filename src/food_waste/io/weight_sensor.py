from .component import WeightSensorComponent, WeightSensorComponentEvents
from . import PIN
from .. import log as console
import time

class WeightSensor(WeightSensorComponent):

  def __init__(self):
    super().__init__(PIN.WEIGHT_CLK_PIN, PIN.WEIGHT_DAT_PIN, threshold=60)

  def wait_object_detected(self):
    now = time.time()
    self.wait(WeightSensorComponentEvents.OBJECT_DETECTED, timeout=60)
    console.debug(f"WeightSensor: Object detected after {time.time() - now} seconds.")
    return time.time() - now < 60

  def wait_for_removal(self):
    self.wait(WeightSensorComponentEvents.OBJECT_REMOVED)
