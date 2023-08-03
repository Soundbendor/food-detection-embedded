import nanocamera
import cv2
import time
import os

from .. import log as console

class CameraSetupError(Exception):
  pass

class Camera:

  def __init__(self):
    self.camera = None

  def setup(self):
    """
    Sets up the camera.
    """
    console.debug("Camera: Setting up camera.")
    try:
      self.camera = nanocamera.Camera(flip = 0, width = 1920, height = 1080, fps = 5, debug = os.getenv('DEBUG'))
    except Exception as e:
      console.error(e)
    if not self.camera.isReady():
      console.error("Camera: Camera failed to set up. See error code below.")
    code, has_err = self.camera.hasError()
    if has_err:
      console.error(f"Camera: Camera error: {code}")
    raise CameraSetupError(f"Camera error: {code}")

  def capture(self):
    """
    Captures a frame from the camera.

    :returns: The captured frame as a numpy array.
    """
    console.debug("Camera: Capturing frame.")
    frame = self.camera.read()
    console.debug("Camera: Frame captured.")
    return frame

  def save(self, path, frame = None):
    """
    Saves a frame to a file.

    :param path: The path to save the frame to.
    :param frame: The frame to save. If not specified, a frame will be captured.
    """
    if frame is None:
      frame = self.capture()
    cv2.imwrite(path, frame)

  def cleanup(self):
    self.camera.release()
