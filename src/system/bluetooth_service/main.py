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
import time
import re

loop = asyncio.get_event_loop()

def run_cmd(cmd):
    process = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    return process.returncode, process

def connect_to_wifi(ssid, password):
    code, process = run_cmd(["nmcli", "device", "wifi", "connect", ssid, "password", password])
    if code == 0:
        response = {
            "message": "Wi-Fi configuration successful",
            "success": True,
            "timestamp": time.time()
        }
    else:
        response = {
            "message": "Wi-Fi configuration failed",
            "log": process.stderr.decode("utf-8"),
            "success": False,
            "timestamp": time.time()
        }
    print(response)
    print(process.stdout.decode("utf-8"))
    print(process.stderr.decode("utf-8"))
    return response

def get_wifi_locations():
    wifi_points = {}
    _, process = run_cmd(["nmcli", "device", "wifi", "list", "--rescan", "yes"])
    raw_lines = process.stdout.decode("utf-8").splitlines()[1:]
    for line in raw_lines:
        regex = re.compile(
            r"^(\*?)\s+(.+?)\s+(\w+)\s+(\d+)\s+(\d+\s+[\w/]+)\s+(\d+)\s+([^\s]+)\s+(.*?)\s*$"
        )
        match = regex.match(line)
        _conn, ssid, _type, channel, speed, signal, _bars, security = match.groups()
        if ssid not in wifi_points:
            wifi_points[ssid] = {
                "ssid": ssid,
                "security": security,
                "signal": int(signal)
            }
        elif wifi_points[ssid]["signal"] < int(signal):
            wifi_points[ssid]["signal"] = int(signal)
    wifi_list = map(
        lambda x: [x["ssid"], x["security"], x["signal"]],
        list(wifi_points.values())
    )
    # sort by signal strength
    wifi_list = sorted(wifi_list, key=lambda x: x[2], reverse=True)
    while True:
        content = json.dumps(wifi_list).encode("utf-8")
        if len(content) < 512:
            break
        wifi_list.pop()
    return wifi_list

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

base_id = 31415924535897932384626433832790

class WifiSetupService(Service):
    def __init__(self):
        # Base 16 service UUID, This should be a primary service.
        super().__init__(str(base_id), True)
        self.update_wifi_last_result = {"success": False, "message": "", "timestamp": 0}
        self.update_wifi_list_last_result = get_wifi_locations()

    def update_wifi_list(self):
        self.update_wifi_list_last_result = get_wifi_locations()
        print("Updated WiFi List", self.update_wifi_list_last_result)
        self.get_nearby_ssids.changed(
            json.dumps(self.update_wifi_list_last_result).encode("utf-8")
        )

    def update_wifi_status(self):
        results = check_wifi_status()
        print("Updated WiFi Status")
        return json.dumps(results).encode("utf-8")

    @characteristic(str(base_id + 1), CharFlags.ENCRYPT_READ)
    def wifi_connection_measurement(self, _):
        print("WiFi Connection Read")
        return self.update_wifi_status()

    @characteristic(str(base_id + 2), CharFlags.ENCRYPT_WRITE | CharFlags.ENCRYPT_READ | CharFlags.WRITE_WITHOUT_RESPONSE)
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
            print("WIFI SET: Loading credentials from payload")
            print(data)
        except Exception as e:
            print(e)
        self.update_wifi_last_result = connect_to_wifi(ssid, password)
        return json.dumps(self.update_wifi_last_result).encode("utf-8")

    @characteristic(str(base_id + 3), CharFlags.NOTIFY | CharFlags.ENCRYPT_READ)
    def get_nearby_ssids(self, _):
        print("WiFi List Read")
        return json.dumps(self.update_wifi_list_last_result).encode("utf-8")

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
        [str(base_id)],
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

    def check_for_connections():
        _, process = run_cmd(["hcitool", "con"])
        output = process.stdout.decode("utf-8").strip()
        return len(output.split("\n")) > 1

    try:
        reregister_check_time = 30
        register_timer = 0
        wifi_list_timer = 0
        device_is_connected = False
        while True:
            await asyncio.sleep(1)
            register_timer += 1
            wifi_list_timer += 1
            if wifi_list_timer >= 5:
                wifi_list_timer = 0
                if device_is_connected:
                    service.update_wifi_list()
            if register_timer >= reregister_check_time:
                register_timer = 0
                device_is_connected = check_for_connections()
                if device_is_connected:
                    print("Connection exists, waiting")
                    reregister_check_time = 10
                else:
                    reregister_check_time = 30
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
                        print("Re-advertising failed...")
                        try:
                            await unregister(advert, bus, adapter)
                        except:
                            pass
    except:
        pass

    await bus.wait_for_disconnect()

if __name__ == "__main__":
    loop.run_until_complete(main())
