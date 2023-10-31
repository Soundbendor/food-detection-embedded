#!/bin/bash

# Create a venv using python 3.6
sudo apt-get install python3-venv
python3.6 -m venv venv

# Update pip
./venv/bin/pip install --upgrade pip

# Install the python libraries from requirements.txt
./venv/bin/pip install -r requirements.txt