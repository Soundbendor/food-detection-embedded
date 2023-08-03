import nanocamera
import cv2
import time

from .. import log as console

class Camera:

  def __init__(self):
    self.camera = None

  def setup(self):
    """
    Sets up the camera.
    """
    console.debug("Camera: Setting up camera.")
    self.camera = nanocamera.Camera(flip = 0, width = 1920, height = 1080, fps = 5)
    console.debug("Camera: Waiting for camera to be ready.")
    for i in range(30):
      if self.camera.isReady():
        console.debug("Camera: Camera is ready.")
        return
      time.sleep(0.5)
    console.error("Camera: Camera failed to become ready in time. Continuing anyway.")

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
