from .use_gpio import get_gpio
GPIO = get_gpio()

PULL_UP = GPIO.PUD_UP
PULL_DOWN = GPIO.PUD_DOWN
PULL_OFF = GPIO.PUD_OFF
