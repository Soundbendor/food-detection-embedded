#!/bin/bash

# Manually set group of gpiochip1 becaues for some reason the rules file doesn't update it
sudo /bin/sh -c 'chown root:gpio /dev/gpiochip1; chmod 660 /dev/gpiochip1'
sudo /bin/sh -c 'chown root:gpio /dev/gpiochip0; chmod 660 /dev/gpiochip0'