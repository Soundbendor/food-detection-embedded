"""
Will Richards, Daniel Lau, Oregon State University, 2023

WiFi/Bluetooh driver for handling device-to-device communication with the bucket
"""
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
# from bluez_peripheral.util import *
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent

import subprocess
import logging

"""
Provides interaction between our device and the network we are connected or attempting to connect to
"""
class WiFiManager():
    def __init__(self) -> None:
        pass

    """
    Run a given command as a complete string like "ping 8.8.8.8"
    """
    def _runCommand(self, cmd: str):
        process = subprocess.run(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process.returncode, process
    
    """
    Scan for available networks
    """
    def scanNetworks(self):
        pass

    """
    Connect to a specified network

    :param ssid: The network name to connect to
    :param password: The password to connect to the network with
    """
    def connectToNetwork(self, ssid, password):
        returnCode, process = self._runCommand(f"nmcli device wifi connect {ssid} password {password}")

        # If we succsessfully exited the program that means we were able to connect to the network
        if returnCode == 0:
            logging.info(f"Successfully connected to network: {ssid}")
            return True
        else:
            logging.error(f"Failed to connect to network: {ssid}")
            return False


"""
Provides interfaces for communicating with bluetooth devices such as phones or laptops
"""
class BluetoothDriver():
    def __init__(self):
        pass
