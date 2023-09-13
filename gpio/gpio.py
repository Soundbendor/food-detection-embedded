from . import mode as GPIO_MODE
from . import direction as GPIO_DIRECTION
from . import pull as GPIO_PULL
from . import value as GPIO_VALUE
from .. import log as console
from .use_gpio import get_gpio
GPIO = get_gpio()

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
  console.debug(f"GPIO: Setting GPIO mode to {mode}.")
  GPIO.setmode(mode)

def setup(pin, direction, pull = GPIO_PULL.PULL_OFF, initial = None):
  """
  Sets up a GPIO pin for use as an input or output.

  :param pin: The pin to set up.
  :param direction: The direction to set the pin to. See :py:const:`GPIO_DIRECTION`.
  :param pull: The pull-up or pull-down resistor to use. See :py:const:`GPIO_PULL`. Only used if the pin is set to an input.
  :param initial: The initial value of the pin. See :py:const:`GPIO_VALUE`. Only used if the pin is set to an output.
  """
  console.debug(f"GPIO: Setting up pin {pin} as {direction}.")
  GPIO.setup(pin, direction, initial = initial)

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
