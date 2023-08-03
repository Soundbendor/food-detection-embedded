import logging
import os

# Adapted from https://stackoverflow.com/a/56944256
class Formatter(logging.Formatter):

  grey = "\x1b[38;20m"
  yellow = "\x1b[33;20m"
  red = "\x1b[31;20m"
  reset = "\x1b[0m"
  format = "%(asctime)s %(levelname)s %(message)s"

  FORMATS = {
    logging.DEBUG: grey + format + reset,
    logging.INFO: reset + format + reset,
    logging.WARNING: yellow + format + reset,
    logging.ERROR: red + format + reset,
  }

  def format(self, record):
    log_fmt = self.FORMATS.get(record.levelno)
    formatter = logging.Formatter(log_fmt)
    return formatter.format(record)

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(Formatter())
logger.addHandler(ch)

def debug(*args):
  """Log a debug message."""
  if os.getenv('DEBUG'):
    log(*args, level='debug')

def info(*args):
  """Log an info message."""
  log(*args, level='info')

def warning(*args):
  """Log a warning message."""
  log(*args, level='warning')

def error(*args):
  """Log an error message."""
  log(*args, level='error')

def log(*args, level='info'):
  """Log a message."""
  for i in range(len(args)):
    message = str(args[i])
    if level == 'debug':
      logger.debug(message)
    elif level == 'warning':
      logger.warning(message)
    elif level == 'error':
      logger.error(message)
    else:
      logger.info(message)
