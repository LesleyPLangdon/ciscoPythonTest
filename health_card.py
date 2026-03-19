"""
health_card.py
--------------
Queries Cisco devices and prints a network health report.

TWO MODES — change the setting below:

  MODE = "mock"   — talks to mock_server.py running locally (no real devices needed)
  MODE = "real"   — talks to real Cisco devices over RESTCONF

For real mode, edit the REAL_DEVICES list with your actual
device IPs and credentials.
"""

import requests
requests.packages.urllib3.disable_warnings()

# ── MODE SWITCH ───────────────────────────────────────────────────────────────
# Change this to "real" to talk to actual Cisco devices

MODE = "mock"

# ── MOCK MODE SETTINGS ────────────────────────────────────────────────────────
# Talks to mock_server.py running on localhost
# Make sure mock_server.py is running in Terminal 1 first

MOCK_BASE    = "http://localhost:8080"
MOCK_DEVICES = [
    "192.168.1.1",
    "192.168.1.2",
    "10.0.1.1",
    "10.0.2.1",
    "10.0.3.1",
    "10.0.4.1",
    "10.0.5.1",
    "10.0.6.1",
]

# ── REAL MODE SETTINGS ────────────────────────────────────────────────────────
# Add your real device IPs and credentials here
# RESTCONF must be enabled on each device:
#   ip http secure-server
#   restconf

REAL_DEVICES = [
    {"ip": "192.168.1.1", "username": "admin", "password": "admin"},
    {"ip": "192.168.1.2", "username": "admin", "password": "admin"},
    # add more devices here
]

# ── API CALL FUNCTIONS ────────────────────────────────────────────────────────

def get_mock(ip, endpoint):
    url = f"{MOCK_BASE}/device/{ip}/restconf/data/{endpoint}"
    r = requests.get(url, headers={"Accept": "application/yang-data+json"})
    r.raise_for_status()
    return r.json()

def get_real(ip, username, password, endpoint):
    url = f"https://{ip}/restconf/data/{endpoint}"
    r = requests.get(
        url,
        auth=(username, password),
        headers={"Accept": "application/yang-data+json"},
        verify=False,
        timeout=10
    )
    r.raise_for_status()
    return r.json()

# ── QUERY ONE DEVICE ──────────────────────────────────────────────────────────

def check_device(ip, username=None, password=None):
    """Query a single device and return its health data."""

    def get(endpoint):
        if MODE == "mock":
            return get_mock(ip, endpoint)
        else:
            return get_real(ip, username, password, endpoint)

    hostname = get("Cisco-IOS-XE-native:native/hostname")\
        .get("Cisco-IOS-XE-native:hostname", "Unknown")

    interfaces = get("ietf-interfaces:interfaces/interface")\
        .get("ietf-interfaces:interface", [])

    iface_states = get("ietf-interfaces:interfaces-state/interface")\
        .get("ietf-interfaces:interface", [])

    total = len(interfaces)
    up    = sum(1 for i in iface_states if i.get("oper-status") == "up")
    down  = [i["name"] for i in iface_states if i.get("oper-status") != "up"]

    return {
        "hostname":   hostname,
        "ip":         ip,
        "total":      total,
        "up":         up,
        "down":       down,
        "status":     "WARN" if down else "OK  "
    }

# ── MAIN REPORT ───────────────────────────────────────────────────────────────

source = "local mock server" if MODE == "mock" else "real devices"

print(f"\n{'='*65}")
print(f"   NETWORK-WIDE DEVICE HEALTH REPORT")
print(f"   Source: {source}")
print(f"   Checking all devices...")
print(f"{'='*65}")

issues = []

if MODE == "mock":
    targets = [{"ip": ip} for ip in MOCK_DEVICES]
else:
    targets = REAL_DEVICES

for target in targets:
    ip = target["ip"]
    try:
        d = check_device(
            ip,
            username=target.get("username"),
            password=target.get("password")
        )
        print(f"\n  [{d['status']}]  {d['hostname']:<20} {d['ip']:<16}")
        print(f"         Interfaces: {d['total']} total  |  {d['up']} up  |  {len(d['down'])} down")
        for name in d["down"]:
            print(f"         DOWN: {name}")
        if d["down"]:
            issues.append(d)

    except requests.exceptions.ConnectionError:
        print(f"\n  [ERR ]  {ip:<16}  (connection refused — is mock_server.py running?)")
    except requests.exceptions.Timeout:
        print(f"\n  [ERR ]  {ip:<16}  (timed out)")
    except Exception as e:
        print(f"\n  [ERR ]  {ip:<16}  ({e})")

print(f"\n{'='*65}")
print(f"  {len(targets)} device(s) checked")
if issues:
    print(f"  {len(issues)} device(s) need attention:")
    for d in issues:
        print(f"    - {d['hostname']} ({d['ip']}): {len(d['down'])} interface(s) down")
else:
    print("  All devices healthy")
print(f"{'='*65}\n")
