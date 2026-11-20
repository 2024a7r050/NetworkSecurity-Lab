# Experiment 10: Perimeter Firewall & Snort IDS Deployment with pfSense

## Overview
This lab implements a layered network defense architecture using **pfSense** as a stateful packet-filtering firewall and **Snort** as a signature-based Intrusion Detection System (IDS). Using an isolated virtual lab (`192.168.1.0/24`), offensive traffic generated from **Kali Linux** against **Metasploitable 2** is inspected to validate rule enforcement and real-time threat detection.

---

## Lab Architecture

```text
+-----------------------+          +-----------------------------------+          +-------------------------+
|   Attacker Node       |          |     Gateway Firewall & IDS        |          |     Target Server       |
|   Kali Linux          |          |     pfSense 2.8.1 + Snort         |          |     Metasploitable 2    |
|   IP: 192.168.1.10    |--------->|     WAN (em0): NAT / DHCP         |--------->|     IP: 192.168.1.20    |
|                       |          |     LAN (em1): 192.168.1.1/24     |          |                         |
+-----------------------+          +-----------------------------------+          +-------------------------+
```

| Node Role | Operating System / Platform | Network Interface | IP Address |
| :--- | :--- | :--- | :--- |
| **Perimeter Firewall / IDS** | pfSense Community Edition (`FreeBSD`) | `em0` (WAN) / `em1` (LAN) | `10.0.2.15` (WAN) / `192.168.1.1/24` (LAN) |
| **Offensive Workstation** | Kali Linux | Internal Network (`LAN`) | `192.168.1.10/24` |
| **Vulnerable Target** | Metasploitable 2 | Internal Network (`LAN`) | `192.168.1.20/24` |

---

## Configuration & Execution

### 1. pfSense Interface & DHCP Provisioning
* Assigned `em0` to **WAN** (NAT) and `em1` to **LAN** (`192.168.1.1/24`) via the pfSense console menu.
* Enabled the DHCP server on the LAN interface (`192.168.1.100` – `192.168.1.200`) and verified web console access at `https://192.168.1.1`.

### 2. Top-Down LAN Firewall Rule Policy
Configured under **Firewall $\rightarrow$ Rules $\rightarrow$ LAN** (evaluated sequentially from top to bottom):

| Priority | Action | Protocol | Source | Destination | Port | Description |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| 1 | **Pass** | Any | Any | LAN Address | 80, 443 | Default Anti-Lockout Rule |
| 2 | **Pass** | TCP | `LAN net` | `any` | `80 (HTTP)` | Allow outbound/internal HTTP |
| 3 | **Pass** | TCP | `LAN net` | `any` | `443 (HTTPS)` | Allow encrypted HTTPS traffic |
| 4 | **Pass** | UDP | `LAN net` | `any` | `53 (DNS)` | Allow DNS name resolution |
| 5 | **Block** | Any | `LAN net` | `any` | `any` | Default deny all other LAN traffic |

### 3. Snort IDS Integration
* Installed **Snort** via **System $\rightarrow$ Package Manager $\rightarrow$ Available Packages**.
* Bound a new Snort instance to the **LAN (`em1`)** interface under **Services $\rightarrow$ Snort**, enabled Emerging Threats / Community rulesets, and started the detection engine.

---

## Attack Simulation & Verification

### Firewall Filtering Validation
From Kali Linux (`192.168.1.10`), tested permitted versus restricted services on Metasploitable 2 (`192.168.1.20`):
```bash
# Permitted HTTP traffic (matches Rule #2)
curl -I http://192.168.1.20
# Output: HTTP/1.1 200 OK

# Blocked Telnet traffic (hits Rule #5 Block All)
telnet 192.168.1.20 23
# Output: Connection timed out (logged in Status -> System Logs -> Firewall)
```

### Intrusion Detection Simulation
Executed three attack vectors from Kali Linux to verify Snort signature matching:
```bash
# 1. TCP SYN/Port Reconnaissance
nmap -p 1-1000 192.168.1.20

# 2. FTP Credential Brute-Force
hydra -l msfadmin -P /usr/share/wordlists/rockyou.txt ftp://192.168.1.20

# 3. High-Rate ICMP Flood (short burst)
ping -f 192.168.1.20
```

### Key Observations
* **Firewall Logs:** Confirmed blocked connection attempts on restricted ports (e.g., TCP port 23) with source IP `192.168.1.10` and destination `192.168.1.20`.
* **Snort Alerts (`Services -> Snort -> Alerts`):** Recorded real-time alerts including `[ET SCAN]` for Nmap port scanning, `[ET POLICY]` for FTP brute-force attempts, and high-frequency ICMP flood alerts with full SID, timestamp, and IP metadata.
