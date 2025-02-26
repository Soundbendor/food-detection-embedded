#!/bin/bash
sudo sed -i "s/^ExecStart=\/usr\/libexec\/bluetooth\/bluetoothd/ExecStart=\/usr\/libexec\/bluetooth\/bluetoothd -P battery/" /etc/systemd/system/bluetooth.target.wants/bluetooth.service
