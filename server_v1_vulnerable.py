import bluetooth
import subprocess

def scan_wifi():
    """Scan available Wi-Fi networks using nmcli."""
    try:
        result = subprocess.run(
            ["nmcli", "-t", "-f", "SSID,SIGNAL", "dev", "wifi"],
            capture_output=True, text=True, check=True
        )
        networks = result.stdout.strip()
        if not networks:
            return "No Wi-Fi networks found."
        return networks
    except Exception as e:
        return f"Error scanning Wi-Fi: {e}"

def connect_wifi(ssid, password):
    """Connect to Wi-Fi using nmcli."""
    try:
        if password:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid, "password", password]
        else:
            cmd = ["nmcli", "dev", "wifi", "connect", ssid]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            return f"✅ Connected to {ssid}"
        else:
            return f"❌ Failed to connect:\n{result.stderr}"
    except Exception as e:
        return f"Error connecting Wi-Fi: {e}"

# --- Bluetooth setup ---
server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", bluetooth.PORT_ANY))
server_sock.listen(1)

bluetooth.advertise_service(
    server_sock,
    "WiFiControlService",
    service_id="00001101-0000-1000-8000-00805F9B34FB",  # Serial Port UUID
    service_classes=["00001101-0000-1000-8000-00805F9B34FB"],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)

print("📡 Waiting for connection on RFCOMM channel 1...")

client_sock, client_info = server_sock.accept()
print(f"✅ Connected from {client_info}")

try:
    while True:
        data = client_sock.recv(1024).decode().strip()
        if not data:
            continue

        print(f"📨 Received: {data}")
        if data.upper() == "SCAN":
            response = scan_wifi()
        elif data.upper().startswith("CONNECT"):
            try:
                _, ssid, password = data.split(" ", 2)
            except ValueError:
                response = "Usage: CONNECT <SSID> <password>"
            else:
                response = connect_wifi(ssid, password)
        elif data.lower() == "quit":
            response = "Goodbye!"
            client_sock.send(response.encode())
            break
        else:
            response = "Unknown command. Use SCAN or CONNECT <SSID> <password>"

        client_sock.send(response.encode())

except OSError:
    print("❌ Connection lost.")

finally:
    print("🔌 Closing Bluetooth sockets...")
    client_sock.close()
    server_sock.close()
    print("✅ Done.")
