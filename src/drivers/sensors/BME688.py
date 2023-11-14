""""
Will Richards, Oregon State University, 2023

Abstraction layer for the BME688 gas sensor
"""

import bme680

import logging
from time import sleep, time


from drivers.DriverBase import DriverBase
from multiprocessing import Event, Value

class BME688(DriverBase):
    """
    Basic constructor for the BME688
    """
    def __init__(self, i2c_address = 0x77):
        super().__init__("BME688")
        self.sensor = bme680.BME680(i2c_address)
        
        
        # List of events that the sensor can raise
        self.events = {
            "CAPTURE": Event()
        }


    """
    Initialize the NAU7802 to begin taking sensor readings
    """
    def initialize(self):
        # Set oversampling amounts
        self.sensor.set_humidity_oversample(bme680.OS_2X)
        self.sensor.set_pressure_oversample(bme680.OS_4X)
        self.sensor.set_temperature_oversample(bme680.OS_8X)

        # Set IIR Filter size and whether or not we should be measuring gas
        self.sensor.set_filter(bme680.FILTER_SIZE_3)
        self.sensor.set_gas_status(bme680.ENABLE_GAS_MEAS)

        # Set heater temperature and duration and finally select the profile
        self.sensor.set_gas_heater_temperature(320)
        self.sensor.set_gas_heater_duration(150)
        self.sensor.select_gas_heater_profile(0)
        logging.info("Initialization complete!")
       

    """
    Measure and return the weight read from the load cell
    """
    def measure(self):
        # Confirm that there is no new data to read
        if(self.getEvent("CAPTURE").is_set()):
            try:
                if(self.sensor.get_sensor_data()):
                    self.data["temperature(c)"].value = self.sensor.data.temperature
                    # Convert hectopascals to kilopascals
                    self.data["pressure(kpa)"].value = self.sensor.data.pressure * 0.1
                    self.data["humidity(%rh)"].value = self.sensor.data.humidity

                    # Only measure the gas if the measurement is ready
                    if(self.sensor.data.heat_stable):
                        self.data["gas_resistance(ohms)"].value = self.sensor.data.gas_resistance
                    else:
                        self.data["gas_resistance(ohms)"].value = -1
                        logging.warning("Gas data was not ready to collect at this time -1 will be returned in place of a value")
            except Exception as e:
                logging.error(f"The following error occured while attempting to read data: {e}")
            self.getEvent("CAPTURE").clear()
        
        
    
    """
    Create a dictionary of the data that this sensor will output
    """
    def createDataDict(self):
        self.data = {
            "temperature(c)": Value('d', 0.0),
            "pressure(kpa)": Value('d', 0.0),
            "humidity(%rh)": Value('d', 0.0),
            "gas_resistance(ohms)": Value('d', 0.0)
        }
        return self.data
    
    """
    Shutdown the proccess
    """
    def kill(self):
        self.sensor._i2c.close()
        
