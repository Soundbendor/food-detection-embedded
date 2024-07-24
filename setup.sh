#!/bin/bash

# Setup script for installing required drivers and setting user permissions to run the detection loop
# Author: Will Richards, 2023

echo "Updating system..."

sudo apt-get update -y

echo "Creating virtual python environment..."

# Create a venv using python 3.7
sudo apt-get -y install python3.11
sudo apt-get -y install python3.11-dev
sudo apt-get -y install python3.11-venv
python3.11 -m venv venv

echo "Installing dependencies..."

sudo apt-get -y install portaudio19-dev

# Update pip
./venv/bin/pip install --upgrade pip

# Install the python libraries from requirements.txt
./venv/bin/pip install -r requirements.txt

sudo apt-get -y install python3-pyaudio
sudo apt-get -y install ffmpeg

# Move cronjobs to correct directories
sudo cp diagnostics/autoUpdate.sh /etc/cron.daily/autoUpdate.sh
sudo cp diagnostics/getLogs.sh /etc/cron.hourly/getLogs.sh

echo "ur mom"
echo "Setup complete!"
