"""
health_card.py
--------------
Pulls device information from a Cisco-style REST API
and prints a formatted health card.

By default this talks to the local mock server (mock_server.py).
To switch to a real Cisco DevNet sandbox, see the commented
settings below.
"""

import requests

# ── Connection settings ───────────────────────────────────────────────────────
# Pointing at our local mock server running in this Codespace.
# No external internet needed - it runs right here alongside your code.

HOST    = "localhost:8080"
BASE    = f"http://{HOST}/restconf/data"
HEADERS = {
    "Accept": "application/yang-data+json",
    "Content-Type": "application/yang-data+json"
}

# ── To switch to the real Cisco DevNet Always-On sandbox instead: ─────────────
# HOST = "sandbox-iosxe-latest-1.cisco.com"
# USER = "developer"
# PASS = "C1sco12345"
# BASE = f"https://{HOST}/restconf/data"
# Then add auth=(USER, PASS), verify=False to each requests.get() call


def get(endpoint):
    """Call a REST API endpoint and return the JSON response as a dict."""
    url = f"{BASE}/{endpoint}"
    response = requests.get(url, headers=HEADERS)
    response.raise_for_status()
    return response.json()


# ── Build the health card ─────────────────────────────────────────────────────

print("\n" + "="*45)
print("       CISCO DEVICE HEALTH CARD")
print("="*45)

# Device hostname
try:
    data = get("Cisco-IOS-XE-native:native/hostname")
    hostname = data.get("Cisco-IOS-XE-native:hostname", "Unknown")
    print(f"  Hostname   : {hostname}")
except:
    print(f"  Hostname   : (unavailable)")

# Interface summary
try:
    data = get("ietf-interfaces:interfaces/interface")
    interfaces = data.get("ietf-interfaces:interface", [])
    enabled = [i for i in interfaces if i.get("ietf-interfaces:enabled") == True]
    print(f"  Interfaces : {len(interfaces)} total, {len(enabled)} enabled")
except:
    print(f"  Interfaces : (unavailable)")

# Interface status list
try:
    data = get("ietf-interfaces:interfaces-state/interface")
    ifaces = data.get("ietf-interfaces:interface", [])
    print(f"\n  {'Interface':<24} {'Status'}")
    print(f"  {'-'*24} {'-'*8}")
    for iface in ifaces:
        name  = iface.get("name", "?")[:24]
        state = iface.get("oper-status", "?")
        icon  = "UP" if state == "up" else "down"
        print(f"  {name:<24} {icon}")
except:
    print(f"  Interface list: (unavailable)")

print("\n" + "="*45)
print("  Source : local mock server (mock_server.py)")
print("="*45 + "\n")
