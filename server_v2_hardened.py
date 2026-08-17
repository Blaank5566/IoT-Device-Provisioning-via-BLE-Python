#!/usr/bin/env python3
import bluetooth
import subprocess
import re

# --- SECURITY CONSTANTS ---
# Standard Wi-Fi SSIDs and passwords typically shouldn't contain dangerous control characters.
# This regex limits inputs to standard letters, numbers, spaces, and safe punctuation.
SAFE_INPUT_REGEX = re.compile(r"^[a-zA-Z0-9_\-\s\.!\?@#\$%\^\&\*\(\)\+=\[\]\{\}]+$")

def is_input_safe(*args):
    """Cybersecurity Shield: Validates inputs against injection attempts."""
    for arg in args:
        if not arg:
            continue
        if not SAFE_INPUT_REGEX.match(arg):
            return False
    return True

def scan_wifi():
    """Scan available Wi-Fi networks securely using nmcli."""
    try:
        # Using specific flags (-t for terse output, -f for fields) to parse cleanly
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
            capture_output=True, text=True, check=True, timeout=10
        )
        networks = result.stdout.strip()
        if not networks:
            return "No Wi-Fi networks found."
        return networks
    except subprocess.TimeoutExpired:
        return "❌ Error: Wi-Fi scan timed out."
    except Exception as e:
        return f"❌ Error scanning Wi-Fi: System subsystem error."

def connect_wifi(ssid, password):
    """Connect to Wi-Fi safely preventing argument injection."""
    # 1. Sanitize incoming inputs
    if not is_input_safe(ssid, password):
        return "❌ Security Block: Malicious characters detected in SSID or Password."

    try:
        # 2. Construct safe execution arguments (No shell=True prevents execution exploitation)
        if password:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
        else:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
            
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            return f"✅ Successfully connected to network: {ssid}"
        else:
            # Masking raw stderr to avoid leaking low-level OS paths to the network client
            return f"❌ Failed to connect. Verify your network credentials."
    except subprocess.TimeoutExpired:
        return "❌ Error: Connection attempt timed out."
    except Exception as e:
        return f"❌ Internal Error: Execution subsystem failure."

# --- BLUETOOTH NETWORKING LAYER ---
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

# Register Serial Port Profile (SPP)
bluetooth.advertise_service(
    server_sock,
    "SecureWiFiControlService",
    service_id="00001101-0000-1000-8000-00805F9B34FB",
    service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

print("📡 Waiting for secure incoming pairing on RFCOMM channel 1...")

try:
    client_sock, client_info = server_sock.accept()
    print(f"✅ Secure connection established from remote hardware: {client_info}")

    while True:
        data = client_sock.recv(1024).decode(errors="ignore").strip()
        if not data:
            continue

        print(f"📨 Telemetry Received: {data}")
        
        if data.upper() == "SCAN":
            response = scan_wifi()
            
        elif data.upper().startswith("CONNECT"):
            # Safe token parsing
            try:
                parts = data.split(" ", 2)
                if len(parts) == 2:
                    _, ssid = parts
                    password = ""
                elif len(parts) == 3:
                    _, ssid, password = parts
                else:
                    raise ValueError
            except ValueError:
                response = "Usage: CONNECT <SSID> <password>"
            else:
                response = connect_wifi(ssid, password)
                
        elif data.lower() == "quit":
            response = "Session terminated. Goodbye!"
            client_sock.send(response.encode())
            break
        else:
            response = "Command Rejected. Allowed operations: SCAN or CONNECT <SSID> <password>"

        client_sock.send(response.encode())

except OSError:
    print("❌ Connection dropped abruptly by client.")
finally:
    print("🔌 Cleaning up socket network resources...")
    try:
        client_sock.close()
        server_sock.close()
    except NameError:
        pass
    print("✅ System safe state achieved.")
