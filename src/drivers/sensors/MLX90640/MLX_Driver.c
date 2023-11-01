#include <stdio.h>
#include <linux/i2c-dev.h>
#include <unistd.h> 
#include <sys/ioctl.h>
#include <fcntl.h>

#include "MLX90640_API.h"
#include "MLX90640_I2C_Driver.h"

/* Redefine I2C calls to use with library */
void MLX90640_I2CInit(void);
int MLX90640_I2CGeneralReset(void);
int MLX90640_I2CRead(uint8_t slaveAddr,uint16_t startAddress, uint16_t nMemAddressRead, uint16_t *data);
int MLX90640_I2CWrite(uint8_t slaveAddr,uint16_t writeAddress, uint16_t data);
void MLX90640_I2CFreqSet(int freq);

// The I2C file-handler we are writing to
int bus;

/**
 * Initialize the I2C bus
*/
void MLX90640_I2CInit(void){
    if((bus = open("/dev/i2c-1", O_RDWR)) < 0){
        bus = -1;
    }

    // 0x33 in binary
    int addr = 0b00100001;
    if(ioctl(bus, I2C_SLAVE, addr) < 0){
        bus = -1;
    }
}

/**
 * Issue an I2C bus reset
*/
int MLX90640_I2CGeneralReset(void){
    return 0;
}

/**
 * Read data from a given address on the I2C device
*/
int MLX90640_I2CRead(uint8_t slaveAddr,uint16_t startAddress, uint16_t nMemAddressRead, uint16_t *data){
    return 123;
}

/**
 * Write data to a given register on the I2C device
*/
int MLX90640_I2CWrite(uint8_t slaveAddr,uint16_t writeAddress, uint16_t data){
    return 0;
}

/* 
    Set the I2C bus frequency 
    Do nothing currently
*/
void MLX90640_I2CFreqSet(int freq){}

int main(){
    /* Attempt to initialize the bus*/
    MLX90640_I2CInit();
    if(bus > 0){
        printf("Succsessfully opened communication with MLX90640: %i\n", bus);
    }
    
    return 0;
}