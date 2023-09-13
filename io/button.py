from ..events import EventEmitter
from .. import gpio as GPIO
from .. import log as console
import threading
import time

class ButtonComponentEvents:
  BUTTON_PRESSED = 'button_pressed'
  BUTTON_RELEASED = 'button_released'

class ButtonComponent(EventEmitter):

  def __init__(self, pin):
    super().__init__()
    self.pin = pin
    self.listener_count = 0
    self.stopped = False
    self.old_status = GPIO.LOW
    self.loop_thread = None

  def setup(self):
    GPIO.setup(self.pin, GPIO.IN, pull=GPIO.PULL_DOWN)
    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    self.stopped = True
    if self.loop_thread is not None:
      console.debug("Button: Waiting for loop thread to stop.")
      self.loop_thread.join()

  def loop(self):
    while not self.stopped:
      if self.listener_count > 0:
        button_status = self.measure()
        if button_status == GPIO.HIGH and self.old_status != GPIO.HIGH:
          console.debug("Button: Button pressed.")
          self.emit(ButtonComponentEvents.BUTTON_PRESSED)
        elif button_status == GPIO.LOW and self.old_status != GPIO.LOW:
          console.debug("Button: Button released.")
          self.emit(ButtonComponentEvents.BUTTON_RELEASED)
        self.old_status = button_status
      else:
        self.old_status = GPIO.LOW
      time.sleep(0.5)
    console.debug("Button: Loop thread stopped.")

  def measure(self):
    """
    Returns the status of the button.
    """
    console.debug("Button: Measuring button status.")
    val = GPIO.input(self.pin) == GPIO.HIGH
    console.debug(f"Button: Button status is {val}.")
    return val

  def on(self, event, callback):
    super().on(event, callback)
    self.listener_count += 1

  def off(self, event, callback):
    super().off(event, callback)
    self.listener_count -= 1
