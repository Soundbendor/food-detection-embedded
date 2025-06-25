#!/bin/bash
if [ ! -f "fixlock.txt" ]; then
	sudo sed -i "s/^ExecStart=\/usr\/libexec\/bluetooth\/bluetoothd/ExecStart=\/usr\/libexec\/bluetooth\/bluetoothd -P battery/" /usr/lib/systemd/system/bluetooth.service
	touch fixlock.txt
fi
