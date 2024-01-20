#!../venv/bin/python

"""
Tool for calibrating camera parameters for rectification

Will Richards, Oregon State University, 2024
"""
import cv2
from glob import glob
import os
import shutil
from stereovision.calibration import StereoCalibrator
from stereovision.calibration import ChessboardNotFoundError

# Row X Column
CHESSBOARD_PATTERN = (6, 9)
SQUARE_SIZE = 1.76 #cm
IMAGE_SIZE = (640, 480)

OUTPUT_DIR = "stereo_calibration_parameter"

def main():
    
    calibrator = StereoCalibrator(CHESSBOARD_PATTERN[0],CHESSBOARD_PATTERN[1], SQUARE_SIZE, IMAGE_SIZE)
    leftImages = glob("images/leftCalibrationImages/*.jpg")
    rightImages = glob("images/rightCalibrationImages/*.jpg")
    print("Images collected")
    if len(leftImages) != len(rightImages):
        print("Directories have different numbers of images!")
        return
    
    # Loop over number of images in glob and read them in and add them to the calibrator
    for i in range(len(leftImages)):
        print(f"Collecting image {i+1} of {len(leftImages)}")
        leftImage = cv2.imread(leftImages[i])
        rightImage = cv2.imread(rightImages[i])
        try:
            calibrator.add_corners((leftImage, rightImage))
        except ChessboardNotFoundError:
            print(f"No cheesboard detected in image {i+1}, you will have to run this script again now that all of these have been removed from the calibration data")
            os.remove(rightImages[i])
            os.remove(leftImages[i])
        

    print("Images collected calibrating....")
    calibration = calibrator.calibrate_cameras()
    print("Calibration complete! Checking calibration error...")

    avg_error = calibrator.check_calibration(calibration)
    print(f"Avg. Error: {avg_error}")

    input("Exporting new calibration data will overwrite previous are you sure you would like to continue? (press enter)")
    if(os.path.isdir(OUTPUT_DIR)):
        shutil.rmtree(OUTPUT_DIR)
        os.mkdir(OUTPUT_DIR)
    else:
        os.mkdir(OUTPUT_DIR)
    calibration.export(OUTPUT_DIR)
    print("Export complete! Exiting...")
    
if __name__ == "__main__":
    main()