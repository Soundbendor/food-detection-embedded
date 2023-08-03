from ..events import EventEmitter
from ..hx711 import HX711
from .. import log as console
import threading
import time

class WeightSensorEvents:
  WEIGHT_MEASURE = 'weight_measure'
  WEIGHT_CHANGE = 'weight_change'
  OBJECT_DETECTED = 'object_detected'
  OBJECT_REMOVED = 'object_removed'

class WeightSensor(EventEmitter):

  def __init__(self, clk_pin, dat_pin, threshold=60):
    super().__init__()
    self.clk_pin = clk_pin
    self.dat_pin = dat_pin
    self.listener_count = 0
    self.old_weight = 0
    self.stopped = False
    self.object_detected = False
    self.threshold = threshold
    self.loop_thread = None
    self.hx = None

  def setup(self):
    self.hx = HX711(self.dat_pin, self.clk_pin)

    console.debug("Weight Sensor: Setting up HX711.")
    self.hx.set_reading_format("MSB", "MSB")
    self.hx.set_reference_unit(94) # Copied from original code
    self.hx.reset()
    self.hx.tare(times = 5)

    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    self.stopped = True
    if self.loop_thread is not None:
      console.debug("Weight Sensor: Waiting for loop thread to stop.")
      self.loop_thread.join()

  def loop(self):
    while not self.stopped:
      if self.listener_count > 0:
        weight = self.measure()
        self.emit(WeightSensorEvents.WEIGHT_MEASURE, weight)

        if weight > self.threshold and self.old_weight > self.threshold:
          console.debug("Weight Sensor: Object detected.")
          self.object_detected = True
          self.emit(WeightSensorEvents.OBJECT_DETECTED)
        elif weight <= self.threshold and self.old_weight < self.threshold and self.object_detected:
          console.debug("Weight Sensor: Object removed.")
          self.object_detected = False
          self.emit(WeightSensorEvents.OBJECT_REMOVED)

        if self.old_weight != weight:
          console.debug(f"Weight Sensor: Weight changed from {self.old_weight} to {weight}.")
          self.emit(WeightSensorEvents.WEIGHT_CHANGE, weight)
          self.old_weight = weight

      time.sleep(0.25)
    console.debug("Weight Sensor: Loop thread stopped.")

  def measure(self):
    """
    Returns the weight measured by the sensor.
    """
    weight = 0
    try:
      console.debug("Weight Sensor: Measuring weight.")
      weight = self.hx.get_weight()
      console.debug(f"Weight Sensor: Weight measured: {weight}g.")
      self.hx.power_down()
      self.hx.power_up()
    except (KeyboardInterrupt, SystemExit):
      GPIO.cleanup()
    return weight

  def tare(self):
    """
    Tares the sensor.
    """
    console.debug("Weight Sensor: Taring.")
    self.hx.tare()

  def on(self, event, callback):
    super().on(event, callback)
    self.listener_count += 1

  def off(self, event, callback):
    super().off(event, callback)
    self.listener_count -= 1
