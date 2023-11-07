from flask import Flask, request, jsonify
import subprocess
import os
import signal

app = Flask(__name__)

@app.route('/configure_wifi', methods=['POST'])
def configure_wifi():
    data = request.get_json()
    ssid = data['ssid']
    password = data['password']

    # Run a command to connect to the Wi-Fi network using NetworkManager
    cmd = f"nmcli device wifi connect {ssid} password {password}"
    process = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    if process.returncode == 0:
        # Send a response to indicate successful Wi-Fi configuration
        response = {"message": "Wi-Fi configuration successful"}
        # Gracefully shut down the server
        shutdown_server()
    else:
        response = {"message": "Wi-Fi configuration failed"}

    return jsonify(response)

def shutdown_server():
    print("Shutting down the server...")
    os.kill(os.getpid(), signal.SIGINT)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
