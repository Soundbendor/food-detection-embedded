""""
Will Richards, Oregon State University, 2023

Abstraction layer for the BME688 gas sensor
"""

from smbus2 import SMBus
import logging
from time import sleep

from drivers.DriverBase import DriverBase
from multiprocessing import Event, Value

class BME688(DriverBase):
    """
    Basic constructor for the BME68
    """
    def __init__(self, i2c_address = 0x77):
        super().__init__("BME68")
        self.i2c_address = i2c_address
        self.collectedData = [1.0] * 4
        self.i2c_bus = SMBus(1)
        
        # List of events that the sensor can raise
        self.events = {}

        # Temperature calculation
        self.t_fine = 0
        self.temp_comp = 0

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
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
    """
    def _calcResHeat(self, target_temp) -> int:
        # Read calibration paramter g1
        par_g1 = self.i2c_bus.read_byte_data(self.i2c_address, 0xED)
        par_g1 = float(par_g1)

        # Read 16-bit par_g2 
        par_g2 = self.i2c_bus.read_byte_data(self.i2c_address, 0xEC)
        par_g2 = par_g2 << 8
        par_g2 |= self.i2c_bus.read_byte_data(self.i2c_address, 0xEB)
        par_g2 = float(par_g2)

        par_g3 = self.i2c_bus.read_byte_data(self.i2c_address, 0xEE)
        par_g3 = float(par_g3)

        # Pull out the 4th and 5th bit of register 0x02 and clearing the rest of the data to just have the number
        res_heat_range = self.i2c_bus.read_byte_data(self.i2c_address, 0x02)
        res_heat_range = res_heat_range & 0b00110000
        res_heat_range = res_heat_range >> 4
        res_heat_range = float(res_heat_range)
        res_heat_val = self.i2c_bus.read_byte_data(self.i2c_address, 0x00)
        res_heat_val = float(res_heat_val)

        # Average indoor temp
        amb_temp = float(21)
        target_temp = float(target_temp)

        var_1 = (par_g1 / 16.0) + 49.0
        var_2 = ((par_g2 / 32768.0) * 0.0005) + 0.00235
        var_3 = par_g3 / 1024.0
        var_4 = var_1 * (1.0 + (var_2 * target_temp))
        var_5 = var_4 + (var_3 * (amb_temp))
        res_heat = int((3.4 * ((var_5 * (4.0 / (4.0 + res_heat_range)) * (1.0/(1.0 + (res_heat_val * 0.002)))) -25)))

        return res_heat

    """
    Configure the startup registers of the BME280 to the spec of section 3.2.1 of the data sheet
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
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
        data = 0b10011001
        self.i2c_bus.write_byte_data(self.i2c_address, 0x64, data)

        # Calculate the res_heat_0 value and store it in the matching register
        data = self._calcResHeat(300)
        self.i2c_bus.write_byte_data(self.i2c_address, 0x5A, data)

        # Select the heater settings and enable gas collection
        reg_value = self.i2c_bus.read_byte_data(self.i2c_address, 0x71)

        # Change Bit  to a 1 and bits 3-0 into 0's
        data = reg_value & 0b11110000
        data = reg_value | 0b00100000

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
    https://www.bosch-sensortec.com/media/boschsensortec/downloads/datasheets/bst-bme688-ds000.pdf
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
        self.temp_comp = self.t_fine / 5120.0
        return self.temp_comp

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

        # Avoid possible divide by 0
        if(var2 != 0):
            press_comp =  ((press_comp - (var2 / 4096.0)) * 6250.0) / var1
            var1 = (float(par_p9) * press_comp * press_comp) / 2147483648.0
            var2 = press_comp * (float(par_p8) / 32768.0)
            var3 = (press_comp / 256.0) * (press_comp / 256.0) * (press_comp / 256.0) * (float(par_p10) / 131072.0)
            press_comp = press_comp + (var1 + var2 + var3 + (float(par_p7) * 128.0)) / 16.0
        else:
            press_comp = 0

        return press_comp
    
    """
    Calculate the humidity value from the sensor following section 3.3.3 of the datasheet
    """
    def _calcHumidity(self) -> float:
        # Create par_h1 out of the 8 bits of 0xE3 and the first 4 bits of 0xE2
        par_h1 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE3) << 4
        par_h1_temp = self.i2c_bus.read_byte_data(self.i2c_address, 0xE2) & 0b00001111
        par_h1 = par_h1 | par_h1_temp

        # Create par_h2 out of the 8 bits of 0xE1 and the last 4 bits of 0xE2
        par_h2 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE1) << 4
        par_h2_temp = self.i2c_bus.read_byte_data(self.i2c_address, 0xE2) >> 4 
        par_h1 = par_h2 | par_h2_temp

        par_h3 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE4)
        par_h4 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE5)
        par_h5 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE6)
        par_h6 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE7)
        par_h7 = self.i2c_bus.read_byte_data(self.i2c_address, 0xE8)

        # Read MSB and shift 8 and then OR with the LSB to get the whole 16 bit number
        hum_adc = self.i2c_bus.read_byte_data(self.i2c_address, 0x25) << 8
        hum_adc_temp = self.i2c_bus.read_byte_data(self.i2c_address, 0x26)
        hum_adc = hum_adc | hum_adc_temp

        var1 = hum_adc - ((float(par_h1) * 16.0) + ((float(par_h3) / 2.0) * self.temp_comp))
        var2 = var1 * ((float(par_h2) / 262144.0) * (1.0 + ((float(par_h4) / 16384.0) * self.temp_comp) + ((float(par_h5) / 1048576.0) * self.temp_comp * self.temp_comp)))
        var3 = float(par_h6) / 16384.0
        var4 = float(par_h7) / 2097152.0
        hum_comp = var2 + ((var3 + (var4 * self.temp_comp)) * var2 * var2)
        
        return hum_comp
    
    """
    Calculate the reading from the gas sensor according to section 3.4.1
    """
    def _calcGasResistance(self) -> float:
        # Get 10 bit gas_adc value
        gas_adc = self.i2c_bus.read_byte_data(self.i2c_address, 0x2C) << 2
        gas_adc_temp = self.i2c_bus.read_byte_data(self.i2c_address, 0x2D) >> 6
        gas_adc = gas_adc | gas_adc_temp

        # Read first 4 bits of 0x2B to get the gas range value
        gas_range = self.i2c_bus.read_byte_data(self.i2c_address, 0x2D) & 0b00001111
        
        # Preformed fucked calculation
        var1 = 262144 >> gas_range
        var2 = gas_adc - 512
        var2 *= 3
        var2 = 4096 + var2
        gas_res = 1000000.0 * float(var1) / float(var2)

        return gas_res

    """
    Return Ture or False based on if we have recievied new data or not
    """
    def _dataReady(self) -> bool:
        meas_status_0 = self.i2c_bus.read_byte_data(self.i2c_address, 0x1D)
        meas_status_0 = meas_status_0 >> 7
        return bool(meas_status_0)

    """
    Return True or False based on wether or not the gas_valid bit was set and the heat_stab bit was set
    """
    def _gasReady(self) -> bool:
        gas_r_lsb = self.i2c_bus.read_byte_data(self.i2c_address, 0x2B)
        gas_valid_r = (gas_r_lsb & 0b00100000) >> 5
        if(bool(gas_valid_r)):
            logging.info("Ready to collect gas measurement!")
        
        heat_stab_r = (gas_r_lsb & 0b00010000) >> 4
        if(bool(heat_stab_r) != True):
            logging.error("Insufficient heating time / target temperature too high")

        # If both the gas measurement valid is true and the heater made it to the correct 
        return (bool(gas_valid_r) and bool(heat_stab_r))

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

        # Trigger a measurement from the device
        self._triggerMeasure()
        # Wait 1 second before reading measurements
        sleep(1)

        # Confirm that there is no new data to read
        if(self._dataReady()):
            self.data["temperature"].value = self._calculateTemperature()
            self.data["pressure"].value = self._calculatePressure()
            self.data["humidity"].value = self._calcHumidity()

            # Only measure the gas if the measurement is ready
            if(self._gasReady()):
                 self.data["gas_resistance"].value = self._calcGasResistance()
            else:
                logging.warning("Gas data was not ready to collect at this time -1 will be returned in place of a value")
        else:
            logging.warning("No new data ready to collect at this time, previous values will be returned for now")
    
    """
    Create a dictionary of the data that this sensor will output
    """
    def createDataDict(self):
        self.data = {
            "temperature": Value('d', 0.0),
            "pressure": Value('d', 0.0),
            "humidity": Value('d', 0.0),
            "gas_resistance": Value('d', 0.0)
        }
        return self.data
    
    """
    Shutdown the proccess
    """
    def kill(self):
        self.i2c_bus.close()
        
