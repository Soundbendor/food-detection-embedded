from bluez_peripheral.gatt.service import Service
from bluez_peripheral.gatt.characteristic import characteristic, CharacteristicFlags as CharFlags
from bluez_peripheral.util import *
from bluez_peripheral.advert import Advertisement
from bluez_peripheral.agent import NoIoAgent

import asyncio
import subprocess
import json
import requests
import signal
import sys
import traceback

uuid = "92f3fd29-7d60-167d-973b-fba35e49d4ea"
loop = asyncio.get_event_loop()

def run_cmd(cmd):
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process.returncode, process

def connect_to_wifi(ssid, password):
    code, _ = run_cmd(["nmcli", "device", "wifi", "connect", ssid, "password", password])
    if code == 0:
        response = {
            "message": "Wi-Fi configuration successful",
            "success": True
        }
    else:
        response = {
            "message": "Wi-Fi configuration failed",
            "success": False
        }
    return response

def check_wifi_status():
    code, process = run_cmd(["iwgetid", "-r"])
    if code == 0:
        # Try making a request
        try:
            requests.get("https://soundbendor.org", timeout=5, verify=False)
            internet_connection = True
        except Exception:
            internet_connection = False
        response = {
            "message": f"Connected to {process.stdout.decode('utf-8').strip()}",
            "success": True,
            "internet_access": internet_connection
        }
    else:
        response = {
            "message": "Not connected to Wi-Fi",
            "success": False
        }
    return response

def disconnect_from_wifi():
    _, process = run_cmd(["iwgetid", "-r"])
    wifi = process.stdout.decode('utf-8').strip()
    code, _ = run_cmd(["nmcli", "con", "down", "id", wifi])
    return {
        "message": "Disconnected",
        "success": code == 0
    }

class WifiSetupService(Service):
    def __init__(self):
        # Base 16 service UUID, This should be a primary service.
        super().__init__("1849", True)
        self.update_wifi_last_result = {"success": False, "message": ""}

    def update_wifi_status(self):
        results = check_wifi_status()
        print("Updated WiFi Status")
        data = json.dumps(results).encode("utf-8")
        self.wifi_connection_measurement.changed(data)
        return data

    @characteristic("2AF9", CharFlags.NOTIFY | CharFlags.ENCRYPT_READ)
    def wifi_connection_measurement(self, _):
        print("WiFi Connection Read")
        return self.update_wifi_status()

    @characteristic("2AB5", CharFlags.ENCRYPT_WRITE | CharFlags.NOTIFY | CharFlags.ENCRYPT_READ)
    def set_wifi_args(self, _):
        print("WiFi Set Return Read")
        return json.dumps(self.update_wifi_last_result).encode("utf-8")

    @set_wifi_args.setter
    def set_wifi_args(self, value, _):
        print("WiFi Set Write")
        ssid = None
        password = None
        try:
            data = json.loads(value.decode("utf-8"))
            ssid = data.get("ssid")
            password = data.get("password")
        except:
            pass
        self.update_wifi_last_result = connect_to_wifi(ssid, password)

async def main():
    bus = await get_message_bus()
    service = WifiSetupService()
    await service.register(bus)
    print("Registered service")

    agent = NoIoAgent()
    await agent.register(bus)
    print("Registered agent")

    adapter = await Adapter.get_first(bus)
    await adapter.set_alias("Jetson Compost Bin")
    advert = Advertisement(
        "B.AI.CB#12345678901",
        [uuid],
        0x0,
        30
    )
    try:
        await advert.register(bus, adapter)
        print("Advertised!")
    except:
        pass

    def cleanup(signum, frame):
        print("exiting")
        loop.create_task(service.unregister())
        sys.exit(0)
    signal.signal(signal.SIGINT, cleanup)

    async def unregister(advert, bus: MessageBus, adapter = None, path: str = "/com/spacecheese/bluez_peripheral/advert0"):
        if not adapter:
            adapter = await Adapter.get_first(bus)
        interface = adapter._proxy.get_interface(advert._MANAGER_INTERFACE)
        try:
            await interface.call_unregister_advertisement(path)
        except:
            pass
        bus.unexport(path, advert._INTERFACE)

    try:
        while True:
            await asyncio.sleep(30)
            try:
                print("Un-registering")
                try:
                    await unregister(advert, bus, adapter)
                except:
                    print("Unregistration failed")
                    traceback.print_exc()
                await asyncio.sleep(1)
                print("Re-advertising")
                await advert.register(bus, adapter)
                print("Advertisement registered")
            except:
                print("Re-advertising failed (likely previously connected to device)")
                print("Restart bin to restart advertising")
                try:
                    await unregister(advert, bus, adapter)
                except:
                    pass
    except:
        pass

    await bus.wait_for_disconnect()

if __name__ == "__main__":
    loop.run_until_complete(main())
