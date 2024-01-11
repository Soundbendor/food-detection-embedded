/*
 * Copyright (C) 2017 Robert Bosch. All Rights Reserved. 
 *
 * Disclaimer
 *
 * Common:
 * Bosch Sensortec products are developed for the consumer goods industry. They may only be used
 * within the parameters of the respective valid product data sheet.  Bosch Sensortec products are
 * provided with the express understanding that there is no warranty of fitness for a particular purpose.
 * They are not fit for use in life-sustaining, safety or security sensitive systems or any system or device
 * that may lead to bodily harm or property damage if the system or device malfunctions. In addition,
 * Bosch Sensortec products are not fit for use in products which interact with motor vehicle systems.
 * The resale and/or use of products are at the purchasers own risk and his own responsibility. The
 * examination of fitness for the intended use is the sole responsibility of the Purchaser.
 *
 * The purchaser shall indemnify Bosch Sensortec from all third party claims, including any claims for
 * incidental, or consequential damages, arising from any product use not covered by the parameters of
 * the respective valid product data sheet or not approved by Bosch Sensortec and reimburse Bosch
 * Sensortec for all costs in connection with such claims.
 *
 * The purchaser must monitor the market for the purchased products, particularly with regard to
 * product safety and inform Bosch Sensortec without delay of all security relevant incidents.
 *
 * Engineering Samples are marked with an asterisk (*) or (e). Samples may vary from the valid
 * technical specifications of the product series. They are therefore not intended or fit for resale to third
 * parties or for use in end products. Their sole purpose is internal client testing. The testing of an
 * engineering sample may in no way replace the testing of a product series. Bosch Sensortec
 * assumes no liability for the use of engineering samples. By accepting the engineering samples, the
 * Purchaser agrees to indemnify Bosch Sensortec from all claims arising from the use of engineering
 * samples.
 *
 * Special:
 * This software module (hereinafter called "Software") and any information on application-sheets
 * (hereinafter called "Information") is provided free of charge for the sole purpose to support your
 * application work. The Software and Information is subject to the following terms and conditions:
 *
 * The Software is specifically designed for the exclusive use for Bosch Sensortec products by
 * personnel who have special experience and training. Do not use this Software if you do not have the
 * proper experience or training.
 *
 * This Software package is provided `` as is `` and without any expressed or implied warranties,
 * including without limitation, the implied warranties of merchantability and fitness for a particular
 * purpose.
 *
 * Bosch Sensortec and their representatives and agents deny any liability for the functional impairment
 * of this Software in terms of fitness, performance and safety. Bosch Sensortec and their
 * representatives and agents shall not be liable for any direct or indirect damages or injury, except as
 * otherwise stipulated in mandatory applicable law.
 *
 * The Information provided is believed to be accurate and reliable. Bosch Sensortec assumes no
 * responsibility for the consequences of use of such Information nor for any infringement of patents or
 * other rights of third parties which may result from its use. No license is granted by implication or
 * otherwise under any patent or patent rights of Bosch. Specifications mentioned in the Information are
 * subject to change without notice.
 *
 * It is not allowed to deliver the source code of the Software to any third party without permission of
 * Bosch Sensortec.
 *
 */

/*!
 * @file bsec_integration_backend.h
 *
 * @brief
 * Contains BSEC integration API
 */

/*!
 * @addtogroup bsec_examples BSEC Examples
 * @brief BSEC usage examples
 * @{*/

#ifndef __BSEC_INTEGRATION_H__
#define __BSEC_INTEGRATION_H__

#ifdef __cplusplus
extern "C"
{
#endif

/**********************************************************************************************************************/
/* header files */
/**********************************************************************************************************************/

/* Use the following bme680 driver: https://github.com/BoschSensortec/BME680_driver/releases/tag/bme680_v3.5.1 */
#include "bme680.h"
/* BSEC header files are available in the inc/ folder of the release package */
#include "bsec_interface.h"
#include "bsec_datatypes.h"


/*********************************************************************/
/* macro definitions */
/*! i2c interface communication, 1 - Enable; 0- Disable */
#define BME680_INTERFACE_I2C             0
/*! spi interface communication, 1 - Enable; 0- Disable */
#define BME680_INTERFACE_SPI             1


/**********************************************************************************************************************/
/* type definitions */
/**********************************************************************************************************************/

/* function pointer to the system specific sleep function */
typedef void (*sleep_fct)(uint32_t t_ms);

/* function pointer to the system specific timestamp derivation function */
typedef int64_t (*get_timestamp_us_fct)();

/* function pointer to the function processing obtained BSEC outputs */
typedef void (*output_ready_fct)(int64_t timestamp, float iaq, uint8_t iaq_accuracy, float temperature, float humidity,
     float pressure, float raw_temperature, float raw_humidity, float gas, bsec_library_return_t bsec_status,
     float static_iaq, float co2_equivalent, float breath_voc_equivalent);

/* function pointer to the function loading a previous BSEC state from NVM */
typedef uint32_t (*state_load_fct)(uint8_t *state_buffer, uint32_t n_buffer);

/* function pointer to the function saving BSEC state to NVM */
typedef void (*state_save_fct)(const uint8_t *state_buffer, uint32_t length);

/* function pointer to the function loading the BSEC configuration string from NVM */
typedef uint32_t (*config_load_fct)(uint8_t *state_buffer, uint32_t n_buffer);
    
/* structure definitions */

/* Structure with the return value from bsec_iot_init() */
typedef struct{
	/*! Result of API execution status */
	int8_t bme680_status;
	/*! Result of BSEC library */
	bsec_library_return_t bsec_status;
}return_values_init;
/**********************************************************************************************************************/
/* function declarations */
/**********************************************************************************************************************/
/*!
 * @brief       Initialize the BSEC library to be ran in backend
 *
 * @param[in]   sample_rate         mode to be used (either BSEC_SAMPLE_RATE_ULP or BSEC_SAMPLE_RATE_LP)
 * @param[in]   temperature_offset  device-specific temperature offset (due to self-heating)
 * @param[in]   state_load          pointer to the system-specific state load function
 * @param[in]   config_load          pointer to the system-specific config load function
 *
 * @return      zero if successful, negative otherwise
 */
return_values_init bsec_iot_init_backend(float sample_rate, float temperature_offset, state_load_fct state_load);
	
/*!
 * @brief       Runs BSEC over a log file of raw sensor data input
 *
 * @param[in]   sample_rate         mode to be used (either BSEC_SAMPLE_RATE_ULP or BSEC_SAMPLE_RATE_LP)
 * @param[in]   sleep               pointer to the system-specific sleep function
 * @param[in]   input_log    		file name of the input data log
 * @param[in]   output_ready        pointer to the function processing obtained BSEC outputs (printf in this example)
 * @param[in]   state_save          pointer to the system-specific state save function
 * @param[in]   save_intvl          interval at which BSEC state should be saved (in samples)
 *
 * @return      return_values_init	struct with the result of the API and the BSEC library
 */ 
void bsec_iot_loop_backend(int ts, float temperature, float pressure, float humidity, float gas_resistance ,float output[7], state_save_fct state_save);

#ifdef __cplusplus
}
#endif

#endif /* __BSEC_INTEGRATION_H__ */

/*! @}*/

