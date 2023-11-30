import bluetooth
import subprocess
import json
import select
import requests

server = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

server.bind(("", bluetooth.PORT_ANY))

print("Listening for connections on Bluetooth!")

server.listen(5)

uuid = "92f3fd29-7d60-167d-973b-fba35e49d4ea"
bluetooth.advertise_service(
  server,
  "B.AI.CB#12345678901", # TODO: Dynamically generate this id
  service_id=uuid,
  service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
  profiles=[bluetooth.SERIAL_PORT_PROFILE]
)

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
        elif msg_type == "wifi_disconnect":
            response = disconnect_from_wifi()
            sock.send(json.dumps(response).encode("utf-8"))
        else:
            sock.send(
                json.dumps({
                    "message": "Unknown command",
                    "success": False
                })
            )

socks = set()
socks.add(server)
bufffers = {}

MAX_BUF_SIZE = 1048576

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
                        if len(bufffers[sock]) >= MAX_BUF_SIZE:
                            bufffers[sock] = b""
        except:
            pass
