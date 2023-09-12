from .component import ButtonComponent, ButtonComponentEvents
from . import PIN
from .. import log as console
import time

class TareButtonStatus():
  TARE = "TARE"
  POWER_OFF = "POWER_OFF"

class TareButton(ButtonComponent):
  def __init__(self, pin=PIN.BUTTON):
    super().__init__(pin)

  def wait_and_get_status(self):
    console.debug("Tare Button: Waiting for button press.")
    self.wait(ButtonComponentEvents.BUTTON_PRESSED)
    now = time.time()
    self.wait(ButtonComponentEvents.BUTTON_RELEASED, timeout=6)
    console.debug(f"Button pressed for {time.time() - now} seconds.")
    if time.time() - now > 5:
      return TareButtonStatus.POWER_OFF
    else:
      return TareButtonStatus.TARE
