sudo touch /etc/systemd/system/bluetooth-server.service
echo "[Unit]
Description='Bluetooth Config Service'

[Service]
ExecStart=${dir_absolute}/run.sh
Type=simple
User=root

[Install]
WantedBy=multi-user.target
" | sudo tee /etc/systemd/system/bluetooth-server.service > /dev/null

sudo systemctl daemon-reload
sudo systemctl enable bluetooth-server-config.service
