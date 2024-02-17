#!/bin/bash

docker run --rm --privileged \
    --device /dev/i2c-1:/dev/i2c-1 \
    --device /dev/spidev0.0:/dev/spidev0.0 \
    --name binsight-firmware \
    -it binsight-firmware
