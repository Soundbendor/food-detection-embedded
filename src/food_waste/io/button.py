from ..events import emitter as EventEmitter
from .. import gpio as GPIO
from .. import log as console
import threading
import time

class ButtonEvents:
  BUTTON_PRESSED = 'button_pressed'
  BUTTON_RELEASED = 'button_released'

class Button(EventEmitter):

  def __init__(self, pin):
    super().__init__()
    self.pin = pin
    self.listener_count = 0
    self.stopped = False
    self.old_status = None

  def setup(self):
    GPIO.setup(self.pin, GPIO.IN)
    self.loop_thread = threading.Thread(target=self.loop)
    self.loop_thread.start()

  def cleanup(self):
    self.stopped = True
    console.debug("Button: Waiting for loop thread to stop.")
    self.loop_thread.join()
    console.debug("Button: Cleaning up GPIO.")
    GPIO.cleanup()

  def loop(self):
    while not self.stopped:
      if self.listener_count > 0:
        button_status = self.measure()
        if button_status == GPIO.HIGH and self.old_status != GPIO.HIGH:
          console.debug("Button: Button pressed.")
          self.emit(ButtonEvents.BUTTON_PRESSED)
        elif button_status == GPIO.LOW and self.old_status != GPIO.LOW:
          console.debug("Button: Button released.")
          self.emit(ButtonEvents.BUTTON_RELEASED)
        self.old_status = button_status
      time.sleep(0.25)
    console.debug("Button: Loop thread stopped.")

  def measure(self):
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
