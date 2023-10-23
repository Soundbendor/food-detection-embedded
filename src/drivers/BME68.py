""""
Will Richards, Oregon State University, 2023

Abstraction layer for the BME68 gas sensor
"""

from smbus2 import SMBus
import logging
import time

from .DriverBase import DriverBase
from multiprocessing import Event

class BME68(DriverBase):


    """
    Basic constructor for the BME68
    """
    def __init__(self, i2c_address = 0x76):
        super().__init__("BME68")
        self.i2c_address = i2c_address
        self.collectedData = [0.0] * 4
        self.i2c_bus = SMBus(1)
        
        # List of events that the sensor can raise
        self.events = {
           "ExampleEvent": Event()
        }

        # Temperature calculation
        self.t_fine = 0

    """
    Read 20 bits out of the register and format it into a full number, used for reading temp/humidty/etc.
    """
    def _read20bits(self, xlsb, lsb, msb):
        temp_msb = self.i2c_bus.read_byte_data(self.i2c_address, msb)
        temp_lsb = self.i2c_bus.read_byte_data(self.i2c_address, lsb)
        temp_xlsb = self.i2c_bus.read_byte_data(self.i2c_address, xlsb)
        adc = (temp_msb << 12) | (temp_lsb << 4) | (temp_xlsb >> 4)

        return adc
    """
    Calculate heat resistance coefficient based on section 3.3.5 of the BME680 datasheet
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf
    """
    def _calcResHeat(self) -> int:
        par_g1 = self.i2c_bus.read_byte_data(self.i2c_address, 0xED)
        # Read the word (2-bytes) from the address
        par_g2 = self.i2c_bus.read_word_data(self.i2c_address, 0xEB)
        par_g3 = self.i2c_bus.read_byte_data(self.i2c_address, 0xEE)
        # Pull out the 4th and 5th bit of register 0x02 and clearing the rest of the data to just have the number
        res_heat_range = self.i2c_bus.read_byte_data(self.i2c_address, 0x02)
        res_heat_range = res_heat_range << 2
        res_heat_rnage = res_heat_range >> 6
        res_heat_val = self.i2c_bus.read_byte_data(self.i2c_address, 0x00)

        # Average indoor temp
        amb_temp = int(21)
        target_temp = int(300)

        # Integers calculations per section 3.3.5 of the data sheet
        var1 =  int((amb_temp * par_g3) / 10) << 8
        var2 = int((par_g1 + 784) * (((((par_g2 + 154009) * target_temp * 5) / 100 ) + 3276800) / 10))
        var3 = var1 + (var2 >> 1)
        var4 = int((var3 / (res_heat_range + 4)))
        var5 = (131 * res_heat_val) + 65536
        res_heat_x100 = int((((var4 / var5) - 250) * 34))
        res_heat_x = int(((res_heat_x100 + 50) / 100))

        return res_heat_x

    """
    Configure the startup registers of the BME280 to the spec of section 3.2.1 of the data sheet
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf
    """
    def _configureRegisters(self) -> None:
        # Read the value out of the ctrl_hum register
        reg_value = self.i2c_bus.read_byte_data(self.i2c_address, 0x72)
        data = 0b10111001 & reg_value

        # Configure humidity oversampling to 1x
        self.i2c_bus.write_byte_data(self.i2c_address, 0x72, data)

        # Configure temperature oversampling to 2x and pressure oversampling to 16x
        data = 0b01010100
        self.i2c_bus.write_byte_data(self.i2c_address, 0x74, data)

        # Set gas_wait_0 to 0x59 for a 100ms warmup
        data = 0b01011001
        self.i2c_bus.write_byte_data(self.i2c_address, 0x64, data)

        # Calculate the res_heat_0 value and store it in the matching register
        data = self._calcResHeat()
        self.i2c_bus.write_byte_data(self.i2c_address, 0x5A, data)

        # Select the heater settings and enable gas collection
        reg_value = self.i2c_bus.read_byte_data(self.i2c_address, 0x71)
        # Change Bit 4 to a 1 and bits 3-0 into 0's
        data = reg_value & 0b11110000
        data = reg_value | 0b00010000

        # Enable gas collection
        self.i2c_bus.write_byte_data(self.i2c_address, 0x71, data)

        logging.debug("Registers configured for data sampling")

    """
    Switch the sensor into measure mode to take a measurement
    """
    def _triggerMeasure(self) -> None:
        # Set the 1st bit of the ctrL_meas bus to 1 to trigger a measurement
        reg_value = self.i2c_bus.read_byte_data(self.i2c_address, 0x74)
        data = reg_value | 0b00000001
        self.i2c_bus.write_byte_data(self.i2c_address, 0x74, data)
        logging.debug("Measure requested")

    """
    Calculate the current temperature coresponding to section 3.3.1 of the datasheet
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme680-ds001.pdf
    """
    def _calculateTemperature(self) -> float:
        # Read in calibration details
        par_t1 = self.i2c_bus.read_word_data(self.i2c_address, 0xE9)
        par_t2 = self.i2c_bus.read_word_data(self.i2c_address, 0x8A)
        par_t3 = self.i2c_bus.read_byte_data(self.i2c_address, 0x8C)

        # Read out the 20 bit temperature, and then shift it into an actual number
        temp_adc = self._read20bits(0x24, 0x23, 0x22)
        var1 = ((float(temp_adc) / 16384.0) - (float(par_t1) / 1024.0)) * float(par_t2)

        # This is actually wild.... wtf
        var2 = (((float(temp_adc) / 131072.0) - (float(par_t1) / 8192.0)) * ((float(temp_adc) / 131072.0) - (float(par_t1) / 8192.0))) * (float(par_t3) * 16.0)

        self.t_fine = var1 + var2
        temp_comp = self.t_fine / 5120.0
        return temp_comp

    """
    Calculate the pressure reading coresponding to section 3.3.2 of the datasheet
    """
    def _calculatePressure(self) -> float:
        # Read in calibration details and adc from the sensor
        par_p1 = self.i2c_bus.read_word_data(self.i2c_address, 0x8E)
        par_p2 = self.i2c_bus.read_word_data(self.i2c_address, 0x90)
        par_p3 = self.i2c_bus.read_byte_data(self.i2c_address, 0x92)
        par_p4 = self.i2c_bus.read_word_data(self.i2c_address, 0x94)
        par_p5 = self.i2c_bus.read_word_data(self.i2c_address, 0x96)
        par_p6 = self.i2c_bus.read_byte_data(self.i2c_address, 0x99)
        par_p7 = self.i2c_bus.read_byte_data(self.i2c_address, 0x98)
        par_p8 = self.i2c_bus.read_word_data(self.i2c_address, 0x9C)
        par_p9 = self.i2c_bus.read_word_data(self.i2c_address, 0x9E)
        par_p10 = self.i2c_bus.read_byte_data(self.i2c_address, 0xA0)
        press_adc = self._read20bits(0x21, 0x20, 0x1F)

        # This is an actual nightmare
        var1 = (float(self.t_fine) / 2.0) - 64000.0
        var2 = var1 * var1 * (float(par_p6) / 131072.0)
        var2 = var2 + (var1 * (float(par_p5) * 2.0))
        var2 = (var2 / 4.0) + (float(par_p4) * 65536.0)
        var1 = (((float(par_p3) * var1 * var1) / 16384.0) + (float(par_p2) * var1)) / 524288.0
        var1 = (1.0 + (var1 / 32768.0)) * float(par_p1)
        press_comp = 1048576.0 - float(press_adc)
        press_comp =  ((press_comp - (var2 / 4096.0)) * 6250.0) / var1
        var1 = (float(par_p9) * press_comp * press_comp) / 2147483648.0
        var2 = press_comp * (float(par_p8) / 32768.0)
        var3 = (press_comp / 256.0) * (press_comp / 256.0) * (press_comp / 256.0) * (float(par_p10) / 131072.0)
        press_comp = press_comp + (var1 + var2 + var3 + (float(par_p7) * 128.0)) / 16.0

        return press_comp
        


    """
    Initialize the NAU7802 to begin taking sensor readings
    """
    def initialize(self):
        self._configureRegisters()
        logging.info("Initialization complete!")
       

    """
    Measure and return the weight read from the load cell
    """
    def measure(self):
        self._triggerMeasure()
        self.collectedData[0] = self._calculateTemperature()
        return self.collectedData


    """
    Calibrate the load cell with a known weight
    """
    def calibrate(self):
       pass
  
    """
    Return the dictionary of events
    """
    def getEvents(self) -> dict:
        return self.events
    
    """
    Get a an event from the driver
    """
    def getEvent(self, event) -> Event:
        return self.events[event][0]
    
    def kill(self):
        self.i2c_bus.close()
        