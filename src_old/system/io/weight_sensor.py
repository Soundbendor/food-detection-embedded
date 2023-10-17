from food_waste.io.hx711_sensor import HX711WeightSensorComponent, HX711WeightSensorComponentEvents
from food_waste import log as console
from . import PIN
import time

class WeightSensor(HX711WeightSensorComponent):

  def __init__(self, clk_pin=PIN.WEIGHT_CLK_PIN, dat_pin=PIN.WEIGHT_DAT_PIN):
    super().__init__(clk_pin, dat_pin, threshold=60)

  def wait_object_detected(self):
    now = time.time()
    self.wait(HX711WeightSensorComponentEvents.OBJECT_DETECTED, timeout=60)
    console.debug(f"WeightSensor: Object detected after {time.time() - now} seconds.")
    return time.time() - now < 60

  def wait_for_removal(self):
    self.wait(HX711WeightSensorComponentEvents.OBJECT_REMOVED)
