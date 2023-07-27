from food_waste.events.emitter import EventEmitter
import food_waste.gpio as GPIO
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
    self.loop_thread.join()
    GPIO.cleanup()

  def loop(self):
    while not self.stopped:
      if self.listener_count > 0:
        button_status = GPIO.input(self.pin)
        if button_status == GPIO.HIGH and self.old_status != GPIO.HIGH:
          self.emit(ButtonEvents.BUTTON_PRESSED)
        elif button_status == GPIO.LOW and self.old_status != GPIO.LOW:
          self.emit(ButtonEvents.BUTTON_RELEASED)
        self.old_status = button_status
      time.sleep(0.25)

  def measure(self):
    return GPIO.input(self.pin) == GPIO.HIGH

  def on(self, event, callback):
    super().on(event, callback)
    self.listener_count += 1

  def off(self, event, callback):
    super().off(event, callback)
    self.listener_count -= 1
