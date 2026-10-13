# ROS 2 over Home WiFi: Raspberry Pi 4 ↔ WSL2 Laptop

How the Pi and the laptop ended up talking over DDS, including the three faults that had to be fixed along the way.

## Setup

| | Pi | Laptop |
|---|---|---|
| OS | Ubuntu 24.04 | Windows 11 + WSL2 (mirrored networking), Ubuntu 24.04 |
| ROS 2 | Jazzy | Jazzy |
| Middleware | Cyclone DDS (`rmw_cyclonedds_cpp`) | Cyclone DDS (`rmw_cyclonedds_cpp`) |
| Network | Home WiFi | Home WiFi |

Both machines have DHCP reservations on the router, because their addresses are written into both DDS configs.

## Final configuration

### Cyclone DDS

Each machine keeps its config at `~/cyclonedds/cyclonedds.xml` and points ROS 2 at it from its shell environment (for example, in `~/.bashrc`):

```bash
export RMW_IMPLEMENTATION=rmw_cyclonedds_cpp
export CYCLONEDDS_URI=file://$HOME/cyclonedds/cyclonedds.xml
```

The Pi's config, with placeholders where the real addresses go:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CycloneDDS xmlns="https://cdds.io/config">
  <Domain>
    <General>
      <Interfaces>
        <NetworkInterface name="wlan0"/>
      </Interfaces>
      <AllowMulticast>false</AllowMulticast>
    </General>
    <Discovery>
      <ParticipantIndex>auto</ParticipantIndex>
      <MaxAutoParticipantIndex>30</MaxAutoParticipantIndex>
      <Peers>
        <Peer address="PI_IP"/>
        <Peer address="LAPTOP_IP"/>
      </Peers>
    </Discovery>
  </Domain>
</CycloneDDS>
```

The laptop's config is identical except for the interface line: `<NetworkInterface address="LAPTOP_IP"/>`.

- **Unicast peers, multicast off.** Multicast doesn't get between the two machines on this network, so each config lists both addresses. Listing the other machine lets them find each other; listing itself lets nodes on the same machine still find each other with multicast off.
- **`ParticipantIndex auto`** gives each ROS process a predictable port, so peers know where to send.
- **Interface binding.** The Pi binds by name (`wlan0`), which keeps working if its address changes. The laptop binds by address, because WSL's mirrored interface names (`eth0`, `eth1`, and so on) aren't a stable anchor.

### Windows firewall

In mirrored mode, Windows' Hyper-V firewall filters traffic into WSL and blocks unsolicited inbound traffic by default. One rule opens DDS's ports for ROS domain 0, and the default stays at Block. In an administrator PowerShell window:

```powershell
New-NetFirewallHyperVRule -Name "ROS2-DDS" -DisplayName "ROS 2 DDS (WSL)" -Direction Inbound -VMCreatorId '{40E0AC32-46A5-438A-A0B2-2B479E8F2E90}' -Protocol UDP -LocalPorts 7400-7500
```

The GUID is the ID Windows uses for WSL. The port range shifts if `ROS_DOMAIN_ID` changes.

## The debugging story

**Symptom:** the talker on the Pi published, and the listener on the laptop printed nothing.

Three independent faults were stacked between them, and any one alone was enough to keep the listener silent. Tests ran bottom-up, one layer at a time:

1. IP reachability (ping, SSH)
2. Multicast with no DDS involved (`ros2 multicast send` / `ros2 multicast receive`)
3. Raw inbound UDP with no DDS involved (`nc`)
4. ROS itself (`demo_nodes_cpp` talker and listener)

### The three faults

1. **A stale address in the laptop's Cyclone config.** The config still tied Cyclone to the laptop's address on a previous network. Run directly with `ros2 run`, Cyclone refused to start with `does not match an available interface`.
2. **Multicast didn't get between the machines,** in either direction. The root cause (router or Windows side) wasn't isolated; switching discovery to unicast peers made it irrelevant.
3. **The Hyper-V firewall blocked anything the Pi initiated.** Every earlier test passed because the laptop started the conversation: SSH, ping, and iperf3, even in reverse mode, where the laptop opens the connection and the Pi sends on it. A stateful firewall lets replies through, but DDS discovery traffic from the Pi isn't a reply. Netcat confirmed it: UDP from the Pi reached WSL only once the firewall allowed it.

### Red herrings

- **`ros2` command hangs on the laptop.** `ros2 topic echo` hung, and `ros2 daemon stop` hung until it timed out, yet no daemon was running. The most likely cause: in WSL's mirrored mode, connecting to a closed localhost port timed out instead of being refused, and the ros2 command-line tool only handles "refused." Plain `ros2 run` never uses the daemon, and `--no-daemon` works for `ros2 node list` and `ros2 topic list`.
- **A brownout.** Mid-session, SSH froze and the Pi dropped off the network. The Pi's red power LED was dark: the battery pack had sagged, and WiFi failed before the CPU did.

## WiFi measurements

Measured with iperf3 and ping between the laptop and the Pi. The Pi was running Raspberry Pi OS at the time, on the same radio and network the ROS card uses.

| Measurement | Result | Notes |
|---|---|---|
| TCP, Pi → laptop | ~110 Mbit/s | The camera direction (`iperf3 -R`) |
| TCP, laptop → Pi | ~95 Mbit/s | The `cmd_vel` direction |
| Round trip, idle | ~8 ms | |
| First reply after idle, power save on | 158 ms | The radio dozes, and the router holds packets until it wakes |
| First reply after idle, power save off | ~7 ms | `sudo iw dev wlan0 set power_save off` |

Notes:

- The Pi 4's radio is a single-antenna 802.11ac design with a 433 Mbit/s link rate at best, so the Pi, not the router, sets the throughput ceiling.
- Internet speed tests (like Fast.com) measure the path to the internet, which the robot's video never takes. iperf3 between the two machines measures the path that matters.
- Power save adds a wake-up delay to the first packet after the radio has been idle, not a constant delay on every packet. The delayed packets are the ones going *to* the Pi, which is the `cmd_vel` direction, so power save stays off on this robot.

## Lessons

- **Same symptom, different causes.** A silent listener had three separate faults behind it; only layer-by-layer tests told them apart.
- **"Connection refused" and "timed out" mean different things.** Refused means the packets arrived and nothing was listening. A timeout means the packets never got there, or nothing answered.
- **Ask which side started the conversation.** Tests the laptop initiates can pass while traffic the Pi initiates is blocked.

## Open items

- Make WiFi power save off persistent on the Ubuntu card (the `iw` setting resets at reboot).
- Restrict the firewall rule to the Pi's address.
- Compare the camera stream's bandwidth with the measured throughput to choose the image transport (next phase).
