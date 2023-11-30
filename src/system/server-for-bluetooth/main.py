import bluetooth
import subprocess
import json
import time
import select

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

server.bind(("", bluetooth.PORT_ANY))

print("Listening for connections on Bluetooth!")

server.listen(5)

uuid = "92f3fd29-7d60-167d-973b-fba35e49d4ea"
bluetooth.advertise_service(
  server,
  "B.AI.CB#12345678901",
  service_id=uuid,
  service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
  profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

def connect_to_wifi(ssid, password):
    cmd = ["nmcli", "device", "wifi", "connect", ssid, "password", password]
    process = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if process.returncode == 0:
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
    cmd = ["nmcli", "device", "wifi"]
    process = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if process.returncode == 0:
        response = {
            "message": "Connected to Wi-Fi",
            "success": True
        }
    else:
        response = {
            "message": "Not connected to Wi-Fi",
            "success": False
        }
    return response

def handle_data(data, sock):
    if isinstance(data, dict):
        msg_type = data.get("type")
        if msg_type == "wifi_connect":
            ssid = data.get("ssid")
            password = data.get("password")
            response = connect_to_wifi(ssid, password)
            sock.send(json.dumps(response).encode("utf-8"))
        elif msg_type == "wifi_status":
            response = check_wifi_status()
            sock.send(json.dumps(response).encode("utf-8"))

socks = set()
socks.add(server)
bufffers = {}

while True:
    ready_to_read, _, _ = select.select(socks, [], [])
    for sock in ready_to_read:
        try:
            if sock is server:
                client, addr = server.accept()
                socks.add(client)
                print(f"Received connection from {addr}")
            else:
                data = sock.recv(1024)
                if not data:
                    socks.remove(sock)
                    sock.close()
                    if sock in bufffers:
                        del bufffers[sock]
                else:
                    if sock not in bufffers:
                        bufffers[sock] = b""
                    bufffers[sock] += data
                    # Try to parse the data
                    try:
                        data = json.loads(bufffers[sock])
                        handle_data(data, sock)
                        bufffers[sock] = b""
                    except:
                        pass
        except:
            pass

server.close()
