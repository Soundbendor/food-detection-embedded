from food_waste.events.emitter import EventEmitter
from food_waste.hx711 import HX711
import food_waste.log as console
import threading
import time

class WeightSensorEvents:
  WEIGHT_MEASURE = 'weight_measure'
  WEIGHT_CHANGE = 'weight_change'
  OBJECT_DETECTED = 'object_detected'

class WeightSensor(EventEmitter):

  def __init__(self, out_pin, in_pin, threshold=60):
    super().__init__()
    self.out_pin = out_pin
    self.in_pin = in_pin
    self.listener_count = 0
    self.old_weight = None
    self.stopped = False
    self.threshold = threshold

  def setup(self):
    self.hx = HX711(out_pin, in_pin)

    console.debug("Weight Sensor: Setting up HX711.")
    self.hx.set_reading_format("MSB", "MSB")
    self.hx.set_reference_unit(94) # Copied from original code
    self.hx.reset()
    self.hx.tare(times = 5)

    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    self.stopped = True
    console.debug("Weight Sensor: Waiting for loop thread to stop.")
    self.loop_thread.join()
    console.debug("Weight Sensor: Cleaning up HX711.")
    self.hx.cleanup()

  def loop(self):
    while not self.stopped:
      if self.listener_count > 0:
        weight = self.measure()
        self.emit(WeightSensorEvents.WEIGHT_MEASURE, weight)

        if weight > self.threshold and self.old_weight > self.threshold:
          console.debug("Weight Sensor: Object detected.")
          self.emit(WeightSensorEvents.OBJECT_DETECTED)

        if self.old_weight != weight:
          console.debug(f"Weight Sensor: Weight changed from {self.old_weight} to {weight}.")
          self.emit(WeightSensorEvents.WEIGHT_CHANGE, weight)
          self.old_weight = weight

      time.sleep(0.25)
    console.debug("Weight Sensor: Loop thread stopped.")

  def measure(self):
    weight = 0
    try:
      console.debug("Weight Sensor: Measuring weight.")
      weight = self.hx.get_weight()
      console.debug(f"Weight Sensor: Weight measured: {weight}g.")
      hx.power_down()
      hx.power_up()
    except (KeyboardInterrupt, SystemExit):
      GPIO.cleanup()
    return weight

  def tare(self):
    console.debug("Weight Sensor: Taring.")
    self.hx.tare()

  def on(self, event, callback):
    super().on(event, callback)
    self.listener_count += 1

  def off(self, event, callback):
    super().off(event, callback)
    self.listener_count -= 1
