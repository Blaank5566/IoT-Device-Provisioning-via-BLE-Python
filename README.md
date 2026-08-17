# IoT Device Provisioning via Bluetooth Serial (RFCOMM)

An automated network orchestration toolchain written in Python 3. This system allows developers to safely scan for local Wi-Fi architectures and inject network configurations into a headless Raspberry Pi (Linux) using a remote Bluetooth client terminal. 

This project bridges the gap between hardware device automation, low-level network sockets, and input sanitization practices taught in the **IBM Cybersecurity Analyst** curriculum.

---

## 🗺️ Architectural Topology

```text
[ Client (Laptop/Phone) ]
       │
       │  (RFCOMM Channel 1 / UUID 1101)
       ▼
[ Server (Raspberry Pi Socket Layer) ]
       │
       │─── 1. Receives raw command stream
       │─── 2. Decodes & Strips Whitespace
       │─── 3. Input Sanitization Filter (RegEx Verification)
       ▼
[ Command Router (Python Logic) ]
       │
       ├─── IF "SCAN" ───► Executes native 'nmcli' system call
       │                   ▲
       └─── IF "CONNECT" ─► Sanitizes SSID & Password arguments
                           │
                           ▼
                 [ Secure Subprocess Execution ]
                           │
                           ▼
                 [ Linux NetworkManager (nmcli) ]
                           │
                           ▼
                 [ Local Hardware Wi-Fi Driver ]
```

---

## 🛠️ Tech Stack & Dependencies

*   **Language:** Python 3.x
*   **Networking Protocol:** Bluetooth Classic RFCOMM (Serial Port Profile - UUID `1101`)
*   **Operating System OS:** Raspberry Pi OS / Linux Debian Environment
*   **Core Native Modules:** `bluetooth` (PyBluez), `subprocess`, `re`, `dbus`

---

## 📂 Repository Structure

*   `client.py`: The lightweight administrative control script deployed on the user's remote endpoint.
*   `server_v1_vulnerable.py`: The primitive proof-of-concept build focusing solely on basic network orchestration functionality.
*   `server_v2_hardened.py`: The secure, production-hardened iteration featuring strict argument filters to defend against interface exploitation.
*   `bt_advertise.py`: D-Bus abstraction layout interacting with the BlueZ Bluetooth management stack.

---

## 🔒 Cybersecurity & Hardening Analysis

During structural evaluation, multiple vectors were addressed to harden the runtime lifecycle of the application against standard network threats.

### 1. Command Injection Mitigation
*   **The Hazard:** Direct concatenation of user-supplied variables inside system execution shells risks systemic exploit injections (e.g., passing string terminators and destructive scripts inside password variables).
*   **The Remedy:** Implemented a robust Regular Expression matching filter (`SAFE_INPUT_REGEX`) restricting character arrays to harmless safe punctuation. The backend script runs calls directly as list arguments without invoking `shell=True`.

### 2. Error & Stack Masking
*   **The Hazard:** Standard execution failures leaking low-level OS paths, file attributes, or runtime environments over a raw public socket.
*   **The Remedy:** Wrapped subprocess routines inside comprehensive `try-except` blocks. Generic, user-safe error flags are returned over the air to enforce defensive data parsing boundaries.

### 3. Future Hardening Horizons (Next Development Phase)
*   **Data-in-Transit Encryption:** Integrating an asymmetric cryptography handshake (Diffie-Hellman/RSA) to protect the Wi-Fi credentials from over-the-air sniffer capture tools.
*   **Access Authentication Whitelisting:** Forcing core pairing loops using Linux BlueZ authentication agents with Secure Simple Pairing (SSP) Passkey verification rules.

---

## 🚀 Deployment Guide

### Hardware Provisioning Prerequisites (Raspberry Pi)
Install required system packages and ensure the Bluetooth subsystem is fully initialized:
```bash
sudo apt-get update
sudo apt-get install bluez bluetooth libbluetooth-dev python3-pip -y
pip3 install pybluez
```

### Initializing the Orchestration Environment
1. Clone the repository into your workspace.
2. Spin up the security-hardened server instance on the **Raspberry Pi**:
   ```bash
   python3 server_v2_hardened.py
   ```
3. Initialize the corresponding telemetry interface on the **Client machine**:
   ```bash
   python3 client.py
   ```
4. Pick the designated hardware index and issue network instructions (`SCAN` / `CONNECT <SSID> <password>`).
