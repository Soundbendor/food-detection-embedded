import cv2
import time
import math
from .camera import Camera

class DepthCamera():

  def __init__(self):
    self.left_camera = Camera()
    self.right_camera = Camera()

  def setup(self):
    self.left_camera.setup(0)
    self.right_camera.setup(1)

  def cleanup(self):
    self.left_camera.cleanup()
    self.right_camera.cleanup()

  def capture_frames(self):
    left_frame = self.left_camera.capture()
    right_frame = self.right_camera.capture()
    return left_frame, right_frame

  def create_depth_map(self, frame1, frame2):
    tmp_path = f"/tmp/food_waste.io.depth_camera_{math.floor(time.time())}"
    self.left_camera.save(
      f"{tmp_path}_one.jpg",
      frame1
    )
    self.right_camera.save(
      f"{tmp_path}_two.jpg",
      frame2
    )

    # Load images
    image1 = cv2.imread(f"{tmp_path}_one.jpg", 0)
    image2 = cv2.imread(f"{tmp_path}_two.jpg", 0)

    stereo = cv2.StereoSGBM_create(numDisparities=64, blockSize=15)
    disparity = stereo.compute(image1, image2)
    return disparity

  def capture_map(self):
    frame1, frame2 = self.capture_frames()
    return self.create_depth_map(frame1, frame2)

  def save(path, image):
    self.left_camera.save(path, image)
