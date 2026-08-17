# ble_wifi_client.py
# Classic Bluetooth client for connecting to Raspberry Pi and controlling Wi-Fi
# Works on Windows 10/11 with pybluez2

import sys
import time

try:
    import bluetooth  # Requires: pip install pybluez2
except ModuleNotFoundError:
    print("❌ The 'bluetooth' module is missing.\n")
    print("👉 Install it with:\n   pip install pybluez2\n")
    sys.exit(1)


def discover_devices():
    print("🔍 Scanning for Bluetooth devices (8s)...")
    try:
        devices = bluetooth.discover_devices(duration=8, lookup_names=True)
    except OSError as e:
        print(f"⚠️ Bluetooth scan failed: {e}")
        return []
    if not devices:
        print("❌ No devices found.")
    return devices


def connect_to_server():
    devices = discover_devices()
    if not devices:
        return None

    for i, (addr, name) in enumerate(devices):
        print(f"{i}: {name or 'Unknown'} [{addr}]")

    try:
        idx = int(input("\nSelect your device number: "))
        addr = devices[idx][0]
    except (ValueError, IndexError):
        print("⚠️ Invalid selection.")
        return None

    print(f"🔗 Connecting to {addr}...")
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

    for attempt in range(3):
        try:
            sock.connect((addr, 1))
            print("✅ Connected successfully!\n")
            return sock
        except OSError as e:
            print(f"⚠️ Connection attempt {attempt+1} failed: {e}")
            time.sleep(2)

    print("❌ Could not connect to device.")
    return None


def send_command(sock, cmd):
    try:
        sock.send(cmd.encode())
        data = sock.recv(4096).decode(errors="ignore")
        return data
    except OSError as e:
        print(f"⚠️ Communication error: {e}")
        return ""


def main():
    sock = connect_to_server()
    if not sock:
        print("🚫 No connection established. Exiting.")
        return

    while True:
        cmd = input("Command (SCAN / CONNECT / quit): ").strip().lower()

        if cmd == "quit":
            break

        elif cmd == "scan":
            print("📶 Scanning Wi-Fi networks...\n")
            response = send_command(sock, "SCAN")
            if not response:
                print("❌ No response from Raspberry Pi.")
                continue

            networks = [line.strip() for line in response.splitlines() if line.strip()]
            if not networks:
                print("❌ No networks found.")
                continue

            print("📋 Available networks:")
            for i, net in enumerate(networks):
                print(f"{i}: {net}")

            try:
                choice = int(input("\nSelect network number: "))
                ssid_line = networks[choice]
                ssid = ssid_line.split(":")[0].strip()
                password = input("Enter Wi-Fi password (leave empty if open): ").strip()

                print("🔐 Sending connect command...")
                result = send_command(sock, f"CONNECT {ssid} {password}")
                print(f"\n📡 Result: {result}\n")

            except (ValueError, IndexError):
                print("⚠️ Invalid selection.")

        else:
            print("⚠️ Unknown command. Use SCAN, CONNECT, or quit.")

    sock.close()
    print("🔚 Disconnected.")


if __name__ == "__main__":
    main()
