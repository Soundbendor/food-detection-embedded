#!/bin/bash

# Setup script for installing required drivers and setting user permissions to run the detection loop
# Author: Will Richards, 2023

echo "Creating virtual python environment..."

# Create a venv using python 3.6
sudo apt-get install python3-venv
python3.6 -m venv venv

echo "Installing dependencies"

# Update pip
./venv/bin/pip install --upgrade pip

# Install the python libraries from requirements.txt
./venv/bin/pip install -r requirements.txt

echo "Extracting precompiled OpenCV"

# Unzip opencv and move into correct directory
unzip ./dependencies/opencv-gstream-enabled.zip -d ./dependencies/opencv
mv ./dependencies/opencv/cv2 ./venv/lib/python3.6/site-packages/cv2
rm -rf ./dependencies/opencv

echo "Updating GPIO user permisions..."

# Add our user to the gpio group
sudo groupadd -f -r gpio
sudo usermod -a -G gpio $(whoami)

# Add GPIO rules and update the current ones once the new one has been added
sudo cp venv/lib/python3.6/site-packages/Jetson/GPIO/99-gpio.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger


echo "Setup complete!"