#!../venv/bin/python
import cv2
import numpy as np
import time

from drivers.sensors.IMX219 import IMX219

CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080

CROPPED_WIDTH = 1440

def main():
    cam = IMX219()
    cam.initialize()
    i = 0
    while(True):
        try:
            cam._poll()
            leftFrame, rightFrame, _ = cam.capture()
            leftFrame = leftFrame[:,int((CAMERA_WIDTH-CROPPED_WIDTH)/2):int(CROPPED_WIDTH+(CAMERA_WIDTH-CROPPED_WIDTH)/2)]
            rightFrame = rightFrame[:,int((CAMERA_WIDTH-CROPPED_WIDTH)/2):int(CROPPED_WIDTH+(CAMERA_WIDTH-CROPPED_WIDTH)/2)]
            cv2.imwrite(f"leftCalibration/leftCalibration_{i}.jpg", leftFrame)
            cv2.imwrite(f"rightCalibration/rightCalibration_{i}.jpg", rightFrame)
            time.sleep(1/30)
            i+=1
        except KeyboardInterrupt:
            cam.kill()
            break

if __name__ == "__main__":
    main()