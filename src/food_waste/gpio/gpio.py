from . import mode as GPIO_MODE
import Jetson.GPIO as GPIO

def setup_io(mode = GPIO_MODE.BCM):
  """
  Sets up the GPIO for use. By default, sets the mode to BCM.

  :param mode: The mode to set the GPIO to. See :py:const:`GPIO_MODE`.
  """
  GPIO.setmode(mode)

def setmode(mode):
  """
  Sets the mode of the GPIO.

  :param mode: The mode to set the GPIO to. See :py:const:`GPIO_MODE`.
  """
  GPIO.setmode(mode)

def setup(pin, direction):
  """
  Sets up a GPIO pin for use as an input or output.

  :param pin: The pin to set up.
  :param direction: The direction to set the pin to. See :py:const:`GPIO_DIRECTION`.
  """
  GPIO.setup(pin, direction)

def cleanup():
  """
  Cleans up the GPIO.
  """
  GPIO.cleanup()

def input(pin):
  """
  Reads the value of a GPIO pin.

  :param pin: The pin to read from.
  :returns: The value of the pin. See :py:const:`GPIO_VALUE`.
  """
  return GPIO.input(pin)

def output(pin, value):
  """
  Writes a value to a GPIO pin.

  :param pin: The pin to write to.
  :param value: The value to write to the pin. See :py:const:`GPIO_VALUE`.
  """
  GPIO.output(pin, value)
