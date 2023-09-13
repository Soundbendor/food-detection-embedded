from .. import log as console
from adafruit_htu21d import HTU21D, HUMIDITY, TEMPERATURE
import threading
import time

class HTU21DSensorComponent:

  def __init__(self):
    self.i2c = None
    self.sensor = None

  def setup(self):
    self.i2c = board.I2C()
    self.sensor = HTU21D(self.i2c)

  def measure_temperature(self):
    """
    Measures the temperature.
    """
    console.debug("HTU21D Sensor: Measuring temperature.")
    self.sensor.measurement([TEMPERATURE])
    conosle.debug(f"HTU21D Sensor: Temperature is {self.sensor.temperature}.")
    return self.sensor.temperature

  def measure_humidity(self):
    """
    Measures the humidity.
    """
    console.debug("HTU21D Sensor: Measuring humidity.")
    self.sensor.measurement([HUMIDITY])
    console.debug(f"HTU21D Sensor: Humidity is {self.sensor.relative_humidity}.")
    return self.sensor.relative_humidity
