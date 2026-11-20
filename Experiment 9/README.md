# COM-511: Network Security Lab — Experiment 9
## Site-to-Site IPsec VPN in Tunnel Mode using strongSwan (`swanctl`)

---

### 1. Executive Summary
This experiment demonstrates the deployment, verification, and cryptographic traffic analysis of an **IKEv2 Site-to-Site IPsec VPN in Tunnel Mode** between two Linux virtual machines using modern **strongSwan (`charon-systemd` / `swanctl`)**. By separating control-plane key negotiation (IKEv2) from data-plane encapsulation (ESP), the Linux kernel XFRM subsystem successfully encrypted and authenticated inner loopback traffic (`10.10.1.1/32` $\leftrightarrow$ `10.20.1.1/32`) across an untrusted outer subnet (`192.168.159.0/24`).

---

### 2. Network Topology & Addressing Worksheet

```text
+-----------------------------------+                       +-----------------------------------+
|      GATEWAY A (Kali Linux)       |                       |     GATEWAY B (Ubuntu Linux)      |
|                                   |                       |                                   |
|  Inner Loopback (lo):             |                       |  Inner Loopback (lo):             |
|  10.10.1.1/32                     |                       |  10.20.1.1/32                     |
|         |                         |                       |         |                         |
|   [ Linux XFRM ]                  |                       |   [ Linux XFRM ]                  |
|         |                         |                       |         |                         |
|  Outer Interface (eth1):          |   ESP Tunnel (AES-GCM)|  Outer Interface (ens34):         |
|  192.168.159.140/24 ==============|=======================|============== 192.168.159.145/24  |
|  IKE ID: gw-a                     |   UDP 500/4500 & P:50 |  IKE ID: gw-b                     |
+-----------------------------------+                       +-----------------------------------+
```

| Parameter | Gateway A (Initiator) | Gateway B (Responder) |
| :--- | :--- | :--- |
| **Operating System** | Kali Linux (`6.19.14+kali-amd64`) | Ubuntu Desktop |
| **Outer Interface** | `eth1` | `ens34` |
| **Outer Tunnel Endpoint IP** | `192.168.159.140/24` | `192.168.159.145/24` |
| **Inner Protected Endpoint** | `10.10.1.1/32` (`lo`) | `10.20.1.1/32` (`lo`) |
| **IKEv2 Identity (`id`)** | `gw-a` | `gw-b` |
| **Authentication Method** | Pre-Shared Key (Base64 PSK) | Pre-Shared Key (Base64 PSK) |
| **IKE Proposal** | `aes256gcm16-prfsha256-modp3072` | `aes256gcm16-prfsha256-modp3072` |
| **ESP Proposal** | `aes256gcm16` (Tunnel Mode) | `aes256gcm16` (Tunnel Mode) |

---

### 3. Implementation Steps

#### Step 1: Host Preparation & Inner Loopback Setup
Modern strongSwan 6.x relies on the VICI socket interface (`charon-systemd` and `swanctl`) rather than the legacy `ipsec.conf` stroke backend.

```bash
# Install modern strongSwan components and packet capture utility
sudo apt update && sudo apt install -y charon-systemd strongswan-swanctl tcpdump
sudo systemctl enable --now strongswan

# Verify daemon and VICI connectivity
sudo swanctl --version --daemon

# Assign inner simulated LAN IP on Gateway A (Kali)
sudo ip address add 10.10.1.1/32 dev lo
ip -br address show dev lo
```

#### Step 2: Mirrored `swanctl.conf` Configuration (PSK Redacted)
A cryptographically strong random secret was generated using `openssl rand -base64 33` and configured with the `0s` Base64 prefix on both peers.

**Gateway A (`/etc/swanctl/swanctl.conf`):**
```hcl
connections {
  lab-vpn {
    version = 2
    local_addrs = 192.168.159.140
    remote_addrs = 192.168.159.145
    proposals = aes256gcm16-prfsha256-modp3072
    local {
      auth = psk
      id = gw-a
    }
    remote {
      auth = psk
      id = gw-b
    }
    children {
      lab-net {
        local_ts = 10.10.1.1/32
        remote_ts = 10.20.1.1/32
        esp_proposals = aes256gcm16
      }
    }
  }
}

secrets {
  ike-lab {
    secret = 0s[REDACTED_BASE64_PSK]
  }
}
```

#### Step 3: Loading Credentials & Initiating the CHILD SA
```bash
sudo chmod 600 /etc/swanctl/swanctl.conf
sudo swanctl --load-all
sudo swanctl --list-conns

# Start outer-interface capture prior to initiation
sudo tcpdump -ni eth1 -w exp9-ipsec.pcap 'udp port 500 or udp port 4500 or proto 50 or proto 51'

# Initiate CHILD SA from Gateway A
sudo swanctl --initiate --child lab-net
```

---

### 4. Verification & Evidence Analysis

#### A. Security Associations (`swanctl --list-sas`)
* **IKE SA (`lab-vpn`):** `ESTABLISHED` using `IKEv2`, `AES_GCM_16-256/PRF_HMAC_SHA2_256/MODP_3072` between `192.168.159.140[gw-a]` and `192.168.159.145[gw-b]`.
* **CHILD SA (`lab-net`):** `INSTALLED` in `TUNNEL` mode with `ESP:AES_GCM_16-256`.
  * Inbound SPI: `0xc6ec928a` (`672 bytes, 8 packets` after bidirectional ICMP testing)
  * Outbound SPI: `0xc807675e` (`672 bytes, 8 packets` after bidirectional ICMP testing)

#### B. Kernel XFRM State & Policy (`ip xfrm state` / `ip xfrm policy`)
The Linux kernel installed matching AEAD `rfc4106(gcm(aes))` states and selector policies:
* **Outbound Policy:** `src 10.10.1.1/32 dst 10.20.1.1/32 dir out` $\rightarrow$ encapsulated via `tmpl src 192.168.159.140 dst 192.168.159.145 proto esp spi 0xc807675e mode tunnel`.
* **Inbound Policy:** `src 10.20.1.1/32 dst 10.10.1.1/32 dir in` $\rightarrow$ decapsulated via `tmpl src 192.168.159.145 dst 192.168.159.140 mode tunnel`.

#### C. Protected Traffic Test
```bash
ping -I 10.10.1.1 -c 4 10.20.1.1
# Result: 4 packets transmitted, 4 received, 0% packet loss
```
Binding the source interface (`-I 10.10.1.1`) ensures outgoing ICMP packets match the `10.10.1.1/32` traffic selector rather than defaulting to `192.168.159.140`.

#### D. Wireshark Packet Capture Analysis (`exp9-ipsec.pcap`)
Using the display filter `isakmp || esp || ah`:
1. **Frames 1–2 (`IKE_SA_INIT`):** Unencrypted UDP port 500 negotiation establishing cryptographic proposals, nonces, and Diffie-Hellman (`MODP_3072`) shared keying material.
2. **Frames 3–4 (`IKE_AUTH`):** Encrypted authentication exchange verifying identities `gw-a` and `gw-b` via PSK and negotiating the `lab-net` CHILD SA.
3. **Frames 5–20 (`ESP`, IP Protocol 50):** 16 encrypted data frames exchanged between outer IPs `192.168.159.140` and `192.168.159.145` (154 bytes each). Only the outer IP header, SPI (`0xc807675e` / `0xc6ec928a`), and sequence numbers remain visible; the inner IP header (`10.10.1.1` $\leftrightarrow$ `10.20.1.1`) and ICMP Echo Request/Reply payloads are completely unreadable.
4. **AH Filter (`ah`):** 0 frames captured, confirming ESP alone provides both confidentiality and integrity.

---

### 5. Environment Cleanup
```bash
sudo swanctl --terminate --child lab-net
sudo ip address del 10.10.1.1/32 dev lo
```
