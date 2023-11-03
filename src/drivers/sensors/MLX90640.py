""""
Will Richards, Oregon State University, 2023

Abstraction layer for the MLX90640 
"""

from mlx90640 import MLX90640 as mlx90640
from drivers.DriverBase import DriverBase
import logging

import sys
import cv2
import numpy as np
from scipy import ndimage
import time
from enum import Enum
import cmapy

from multiprocessing import Event

class CameraRefreshRate(Enum):
    RATE_05 = 0x00,
    RATE_1 = 0x01,
    RATE_2 = 0x02,
    RATE_4 = 0x03,
    RATE_8 = 0x04,
    RATE_16 = 0x05,
    RATE_32 = 0x06,
    RATE_64 = 0x07



"""
Class used to convert the data from the IR matrix into a thermal camera of sorts
"""
class ThermalCam():
    
    # Heatmap generation parameters 
    _colormap_list=['jet','bwr','seismic','coolwarm','PiYG_r','tab10','tab20','gnuplot2','brg']
    _interpolation_list =[cv2.INTER_NEAREST,cv2.INTER_LINEAR,cv2.INTER_AREA,cv2.INTER_CUBIC,cv2.INTER_LANCZOS4,5,6]
    _interpolation_list_name = ['Nearest','Inter Linear','Inter Area','Inter Cubic','Inter Lanczos4','Pure Scipy', 'Scipy/CV2 Mixed']
    def __init__(self, width=1200, height=900, refreshRate=CameraRefreshRate.RATE_4):
        self.imageHeight = height
        self.imageWidth = width
        self._colormap_index = 0

        # Setup the camera
        self.mlx = mlx90640()
        self.mlx.i2c_init("/dev/i2c-1")
        self.mlx.set_refresh_rate(refreshRate.value[0])

    """
    Scale temperature values to create an accurate heatmap
    """
    def _rescaleTemps(self, f, Tmin, Tmax):
        f = np.nan_to_num(f)
        norm = np.uint8(((f - Tmin) / (Tmax-Tmin))*255)
        norm.shape = (24,32)
        return norm

    def _captureRaw(self):
        emissivity = 0.95
        ta = 23.15

        # Read the matrix out
        self.mlx.dump_eeprom()
        self.mlx.extract_parameters()
        self.mlx.get_frame_data()
        ta = self.mlx.get_ta() - 8.0
        heats = self.mlx.calculate_to(emissivity, ta)
        heats = np.array(heats)

        # Normalize values
        self._tempMin = np.min(heats)
        self._tempMax = np.max(heats)
        heats = self._rescaleTemps(heats, self._tempMin, self._tempMax)
        return heats

    def _createHeatmap(self, raw_data):

        # Scale the image so that we have a higher resolution and apply colormap
        image = ndimage.zoom(raw_data, 10)
        image = cv2.applyColorMap(image, cmapy.cmap(self._colormap_list[self._colormap_index]))
        image = cv2.resize(image, (800,600), interpolation=cv2.INTER_CUBIC)

        # Flip image and filter to get smooth upright image
        image = cv2.flip(image, 0)
        image = cv2.bilateralFilter(image,15,80,80)
        return image
    
    """
    Take several captures before the actual one so the sensor has data to average
    """
    def _preloadImage(self):
        for i in range(5):
            self._captureRaw()

    """
    Capture the data and generate a heatmap from the data
    """
    def capture(self):
        self._preloadImage()
        heats = self._captureRaw()
        heatmap = self._createHeatmap(heats)
        cv2.imwrite("heatmap.jpg", heatmap)
        logging.info("Succsessfully captured heatmap")

    """
    Close the current I2C communication channel
    """
    def close(self):
        self.mlx.i2c_tear_down()
        

class MLX90640(DriverBase):

    """
    Construct a new instance of the camera
    """
    def __init__(self):
        super().__init__("MLX90640", 1)
        self.mlx = ThermalCam()
        self.events = {
            "Capture": Event()
        }

    def initialize(self):

        # Capture 5 raw packets to warm up the sensor so the first image is a full heatmap
        for i in range(5):
            self.mlx._captureRaw()
    
    def measure(self) -> None:
        if(self.getEvent("Capture").is_set()):
            self.mlx.capture()
            self.getEvent("Capture").clear()

    def kill(self):
        self.mlx.close()

    def createDataDict(self):
        self.data = {
        }
        return self.data

        