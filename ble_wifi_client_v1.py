import bluetooth

print("🔍 Scanning for Bluetooth devices...")
devices = bluetooth.discover_devices(duration=8, lookup_names=True)
for i, (addr, name) in enumerate(devices):
    print(f"{i}: {name} [{addr}]")

idx = int(input("Select device: "))
addr = devices[idx][0]

sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
sock.connect((addr, 1))
print("✅ Connected!")

while True:
    cmd = input("Command (SCAN / CONNECT <ssid> <password> / quit): ").strip()
    if cmd.lower() == "quit":
        break
    sock.send(cmd.encode())
    data = sock.recv(4096).decode(errors="ignore")
    print("📡 Response:\n", data)

sock.close()