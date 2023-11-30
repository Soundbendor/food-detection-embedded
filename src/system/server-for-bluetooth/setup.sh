#!/usr/bin/env bash

dir="$(dirname "$0")"
dir_absolute="$(readlink -m "$dir")"

cd "$dir"

dpkg-query -W python3.8 > /dev/null
if [ $? -eq 1 ]; then
  echo "Installing Python 3.8"
  sudo apt-get install -y python3.8
  sudo apt-get install -y python3.8-dev
  sudo apt-get install -y python3.8-venv
fi

dpkg-query -W libbluetooth-dev > /dev/null
if [ $? -eq 1 ]; then
  echo "Installing bluetooth dev"
  sudo apt-get install -y libbluetooth-dev
fi

mkdir -p /etc/systemd/system/bluetooth.service.d

if ! [ -f /etc/systemd/system/bluetooth.service.d/override.conf ]; then
  echo "Fixing bluetooth library issues"
echo "[Service]
ExecStart=
ExecStart=/usr/lib/bluetooth/bluetoothd -C
" | sudo tee /etc/systemd/system/bluetooth.service.d/override.conf > /dev/null
  sudo systemctl daemon-reload
  sudo systemctl restart bluetooth
  sudo sdptool add SP
fi

echo "Creating environment and installing dependencies"

python3.8 -m venv venv
./venv/bin/pip install -r requirements.txt
