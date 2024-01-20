#!../venv/bin/python

import cv2
import numpy as np
from time import sleep
import importlib
import visionConfig

from stereovision.calibration import StereoCalibration

def createPipeline(id):
    return f"nvarguscamerasrc sensor-id={id} sensor-mode=3 ! video/x-raw(memory:NVMM), width=(int)1640, height=(int)1232, format=(string)NV12, framerate=(fraction)20/1 ! nvvidconv flip-method=2 ! video/x-raw, width=(int)640, height=(int)480, format=(string)BGRx ! videoconvert ! video/x-raw, format=(string)BGR ! appsink"

def main():
    # Create left and right video caputres
    leftCap = cv2.VideoCapture(createPipeline(0), cv2.CAP_GSTREAMER)
    rightCap = cv2.VideoCapture(createPipeline(1), cv2.CAP_GSTREAMER)

    activeCalibration = StereoCalibration(input_folder="./stereo_calibration_parameter")

   

    downsample = 2
    resize = (int(640 / downsample), int(480 / downsample))

    #matcher = cv2.StereoSGBM.create(-9,256,11,0,0,1,63,10,100,32, cv2.StereoSGBM_MODE_SGBM)
    matcher = cv2.StereoSGBM.create(
        visionConfig.min_disparity,
        visionConfig.num_disparities,
        visionConfig.block_size,
        visionConfig.disp_12_max_diff,
        visionConfig.pre_filter_cap,
        visionConfig.uniqueness_ratio,
        visionConfig.speckle_window,
        visionConfig.speckle_range,
        mode=cv2.STEREO_SGBM_MODE_SGBM
    )
    while True:
        try:

            # Grab the frames so they are more in sync then retrieve them
            lSuccsess = leftCap.grab()
            rSuccsess = rightCap.grab()

            if lSuccsess and rSuccsess:
                lRetrieve, leftFrame = leftCap.retrieve()
                rRetrieve, rightFrame = rightCap.retrieve()

                if lRetrieve and rRetrieve:
                    rectified_pair = activeCalibration.rectify((leftFrame, rightFrame))
                    cv2.imwrite("left.jpg", rectified_pair[0])
                    cv2.imwrite("right.jpg", rectified_pair[1])
                    # leftFrame = cv2.resize(rectified_pair[0], resize)
                    # rightFrame = cv2.resize(rectified_pair[1], resize)

                    height, width, channels = leftFrame.shape

                    leftFrame = cv2.cvtColor(rectified_pair[0], cv2.COLOR_BGR2GRAY)
                    rightFrame = cv2.cvtColor(rectified_pair[1], cv2.COLOR_BGR2GRAY)
                    importlib.reload(visionConfig)
                    matcher.setMinDisparity(visionConfig.min_disparity)
                    matcher.setNumDisparities(visionConfig.num_disparities)
                    matcher.setBlockSize(visionConfig.block_size)
                    matcher.setP1(8*channels*visionConfig.block_size*visionConfig.block_size)
                    matcher.setP2(32*channels*visionConfig.block_size*visionConfig.block_size)
                    matcher.setDisp12MaxDiff(visionConfig.disp_12_max_diff)
                    matcher.setPreFilterCap(visionConfig.pre_filter_cap)
                    matcher.setUniquenessRatio(visionConfig.uniqueness_ratio)
                    matcher.setSpeckleWindowSize(visionConfig.speckle_window)
                    matcher.setSpeckleRange(visionConfig.speckle_range)

                    disparity = matcher.compute(rightFrame, leftFrame)

                    disparity = cv2.resize(disparity, (640, 480))

                    disparity_normal = cv2.normalize(disparity, None, 0, 255, cv2.NORM_MINMAX)
                    image = np.array(disparity_normal, dtype = np.uint8)


                    cv2.imwrite("disparity.jpg", image)
            sleep(1/30)
        except KeyboardInterrupt:
            leftCap.release()
            rightCap.release()
            break

if __name__ == "__main__":
    main()