"""
Will Richards, Daniel Lau, Oregon State University, 2023

WiFi/Bluetooh driver for handling device-to-device communication with the bucket
"""
from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.util import get_message_bus, Adapter
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent

import subprocess
import logging
from time import time, sleep
import asyncio
import json

from helpers import RequestHandler


"""
Provides interaction between our device and the network we are connected or attempting to connect to
"""
class WiFiManager():
    def __init__(self):
        self.requests = RequestHandler()
        self.lastConnectionResult = {"success": False, "message": "", "timestamp": 0}
        self.lastWiFiScan = {}
        self.scanNetworks()

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
    Given the result from nmcli we want to pull out the network name and the signal strength and return them as dict of the two SSID: Signal Strength
    """
    def _parseNetworkList(self, cmdOutput: str):
        resultNetworks = {}
        output = cmdOutput.split("\n")

        # For each network that we discovered during our scan we want to split and remove all duplicates so we have a list of network names mapped to signal strengths
        for network in output:
            network = network.strip()
            splitNetworkName = network.split(":")
            if len(splitNetworkName[0]) > 0 and (splitNetworkName[0] not in resultNetworks):
                resultNetworks[splitNetworkName[0]] = {"strength": int(splitNetworkName[1]), "security": splitNetworkName[2]}

        return resultNetworks
    
    """
    Scan for available networks
    """
    def scanNetworks(self):
        returnCode, process = self._runCommand("nmcli -g SSID,SIGNAL,SECURITY device wifi list")
        if returnCode == 0:
            # Create a dict of network names to signals to avoid duplicate networks
            discoveredNetworks = self._parseNetworkList(process.stdout.decode('utf-8'))
            self.lastWiFiScan = discoveredNetworks
            return True
        else:
            logging.error("Failed to scan WiFi networks!")
            return False

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

            self.lastConnectionResult = {
                "message": "Wi-Fi configuration successful",
                "success": True,
                "timestamp": time()
            }
            return
        else:
            logging.error(f"Failed to connect to network: {ssid}")
            self.lastConnectionResult = {
                "message": "Wi-Fi configuration failed",
                "log": process.stderr.decode("utf-8"),
                "success": False,
                "timestamp": time()
            }
            return False
        
    """
    Check if we are actually connected to the internet by sending a heartbeat request to our API
    """
    def checkConnection(self):
        returnCode, process = self._runCommand(f"nmcli -t -f NAME c show --active")

        # If we got a 0 return code attempt to parse out the active network name
        if(returnCode == 0):
            activeNetwork = process.stdout.decode('utf-8').split("\n")[0].strip()

            # If we do show up as being connected to an actual network we want to send a heartbeat to see if we have an actual internet connection
            hasInternet = self.requests.sendHeartbeat()
            return {
                "message": f"Connected to {activeNetwork}",
                "success": True,
                "internet_access": hasInternet
            }
        else:
            return {
                "message": "Not connected to Wi-Fi",
                "success": False
            }

"""
Provides interfaces for communicating with bluetooth devices such as phones or laptops
"""
class BluetoothDriver():
    
   
    """
    Provides bluetooth service descriptor for the WiFi setup procedure
    """
    class WiFiSetupSerivce(Service):

        # Start the bluetooth service with the unique indentifier from the hardware address
        def __init__(self):
            super().__init__("BEEF", True)
            self.wifi = WiFiManager()

        @characteristic("BEF0", CharFlags.ENCRYPT_READ)
        def getConnectionStatus(self, options):
            return json.dumps(self.wifi.checkConnection()).encode('utf-8')
        
        @characteristic("BEF1", CharFlags.ENCRYPT_WRITE | CharFlags.ENCRYPT_READ | CharFlags.WRITE_WITHOUT_RESPONSE)
        def setWIFiArgs(self, options):
            return json.dumps(self.wifi.lastConnectionResult).encode('utf-8')
        
        @setWIFiArgs.setter
        def setWIFIArgs(self, value, options):
            ssid = ""
            password = ""

            try:
                data = json.loads(value.decode('utf-8'))
                ssid = data["ssid"]
                password = data["password"]

                print(f"SSID: {ssid}, Password: {password}")
            except Exception as e:
                logging.error(f"An error occurred when setting WiFi credentials: {e}")

            self.wifi.lastConnectionResult = self.wifi.connectToNetwork(ssid, password)
            return json.dumps(self.wifi.lastConnectionResult).encode('utf-8')
        
        @characteristic("BEF2", CharFlags.NOTIFY | CharFlags.ENCRYPT_READ)
        def getScannedNetworks(self, options):
            return json.dumps(self.wifi.lastWiFiScan).encode('utf-8')
    
    """
    Construct a new instance of the bluetooth driver
    """
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.run_until_complete(self.setupBus())
        while True:
            try:
                sleep(0.1)
            except KeyboardInterrupt:
                break
    
    async def setupBus(self):
        bus = await get_message_bus()
        service = self.WiFiSetupSerivce()
        await service.register(bus)

        agent = NoIoAgent()
        await agent.register(bus)

        adapter = await Adapter.get_first(bus)
        await adapter.set_alias("Binsight Compost Bin")
        advert = Advertisement(
            "B.AI.CB#12345678901",
            ["BEEF"],
            0x0,
            30
        )

        try:
            await advert.register(bus, adapter)
            print("Advertised!")
        except:
            pass
