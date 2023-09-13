sysgpio = None

def use_gpio(gpio):
  """
  Sets the GPIO to use.
  ---
  GPIO must have the following methods:
  - setmode(mode)
  - setup(pin, direction, pull = None, initial = None)
  - cleanup()
  - input(pin)
  - output(pin, value)
  ---
  GPIO must have the following constants:
  - IN, OUT
  - BCM, BOARD
  - HIGH, LOW
  ---

  :param gpio: The GPIO to use.
  """
  global sysgpio
  sysgpio = gpio

def get_gpio():
  """
  Gets the GPIO being used.

  :returns: The GPIO being used.
  """
  if sysgpio is None:
    raise Exception("GPIO has not been set. Use use_gpio() to set the GPIO at the start of the program.")
  return sysgpio
