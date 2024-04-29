"""
Will Richards, Daniel Lau, Oregon State University, 2024

WiFi/Bluetooh driver for handling device-to-device communication with the bucket
"""
from bluez_peripheral.gatt.service import Service, ServiceCollection
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.util import get_message_bus, Adapter
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent

import subprocess
import logging
from time import time, sleep
import asyncio
import json
import uuid

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
    Get the results from the last WiFi scan
    """
    def getLastScanResults(self):
        return self.lastWiFiScan
    
    """
    Get the results from the last attempted connection
    """
    def getLastConnectionResults(self):
        return self.lastConnectionResult
    
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
                "log": process.stderr.decode("utf-8").strip(),
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

        """
        Start the bluetooth service with the unique indentifier 
        """
        def __init__(self):
            super().__init__(str(31415924535897932384626433832790), True)
            self.wifi = WiFiManager()

        """
        Return the current status of our connection, are we connected to a network and if so are we also connected to the internet
        """
        @characteristic(str(31415924535897932384626433832790+1), CharFlags.READ)
        def getConnectionStatus(self, options):
            return json.dumps(self.wifi.checkConnection()).encode('utf-8')
        
        """
        Returns the result of the last Wi-Fi connection attempt
        """
        @characteristic(str(31415924535897932384626433832790+2), CharFlags.WRITE | CharFlags.READ | CharFlags.WRITE_WITHOUT_RESPONSE)
        def setWIFiArgs(self, options):
            return json.dumps(self.wifi.lastConnectionResult).encode('utf-8')
        
        """
        Takes the Wi-Fi credentials recieved from a remote device and attempts to connect to the network provided in the request
        """
        @setWIFiArgs.setter
        def setWIFIArgs(self, value, options):
            ssid = ""
            password = ""
            decodedValue = str(value.decode('utf-8'))

            try:
                data = json.loads(decodedValue)
                ssid = data["ssid"]
                password = data["password"]

            except Exception as e:
                logging.error(f"An error occurred when setting WiFi credentials: {e}")
                self.lastConnectionResult = {"success": False, "message": e, "timestamp": time()}

            self.wifi.connectToNetwork(ssid, password)
            return json.dumps(self.wifi.lastConnectionResult).encode('utf-8')
        
        """
        Returns a JSON document with the list of in range access points, their strength and security type
        """
        @characteristic(str(31415924535897932384626433832790+3), CharFlags.NOTIFY | CharFlags.READ)
        def getScannedNetworks(self, options):
            self.wifi.scanNetworks()
            return json.dumps(self.wifi.lastWiFiScan).encode('utf-8')
    
    """
    Handles the transmission and valididation of API keys
    """
    class APISetupService(Service):
        def __init__(self):
            super().__init__("ABC0", True)
            self.requests = RequestHandler()
        
        def checkAPIConnection(self):
            return self.requests.sendSecureHeartbeat()
            
        @characteristic("ABC1", CharFlags.WRITE | CharFlags.READ | CharFlags.WRITE_WITHOUT_RESPONSE)
        def setAPIKey(self, options):
            return str(self.checkAPIConnection()).encode('utf-8')

        @setAPIKey.setter
        def setAPIKey(self, value, options):
            try:
                decodedValue = str(value.decode('utf-8')).strip()
                data = json.loads(decodedValue)
                print("Decoded JSON!")
            except Exception as e:
                print(f"An error occurred: {e}")
                return False
            print(type(data))
            # Formulate new FastAPI credentials based on the incoming data
            creds = {
                "FASTAPI_CREDS": {
                    "apiKey": data["apiKey"],
                    "endpoint": data["endpoint"],
                    "port": int(data["port"])
                }
            }

            jsonString = json.dumps(creds)
            # Write the new credentials to the config.secret file
            with open("config.secret", "w") as file:
                file.write(jsonString)

            # Then have the requests library update the credentials currently loaded into the system
            self.requests.updateAPICreds()
            print("Written to file and updated credentials!")
    
        @characteristic("ABC2", CharFlags.READ)
        def getAPIKey(self, options):
            response = {
                "apiKey": self.requests.getAPIKey(),
                "deviceID": uuid.getnode()
            }
            
            return json.dumps(response).encode('utf-8')

    """
    Handles requests to test specific components 
    """
    class DebugService(Service):
        def __init__(self):
            super().__init__("BEEF", True)
    """
    Construct a new instance of the bluetooth driver
    """
    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.running = True
        self.loop.run_until_complete(self.setupBus())
        self.loop.run_until_complete(self.controlLoop())

    """
    Get the number of connections to the device
    """
    def checkConnections():
        pass

    async def controlLoop(self):
        while self.running:
            await asyncio.sleep(0.5)
    
    async def setupBus(self):
        bus = await get_message_bus()
        wifiService = self.WiFiSetupSerivce()
        apiService = self.APISetupService()

        serviceCollection = ServiceCollection()
        serviceCollection.add_service(wifiService)
        serviceCollection.add_service(apiService)
      
        await serviceCollection.register(bus)
        logging.info("Registered services.")
        
        agent = NoIoAgent()
        await agent.register(bus)

        adapter = await Adapter.get_first(bus)
        bluetoothName = "Binsight Compost Bin"
        await adapter.set_alias(bluetoothName)
        advert = Advertisement(
            bluetoothName,
            [str(31415924535897932384626433832790), "ABC0"],
            0x0,
            360
        )

        try:
            await advert.register(bus, adapter)
            logging.info("Advertising Bluetooth Device")

        except:
            pass

    """
    Run a given command as a complete string like "ping 8.8.8.8"

    :param cmd: The command to run as one contigious string
    """
    def _runCommand(self, cmd: str):
        process = subprocess.run(
            cmd.split(" "),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return process.returncode, process
