"""
mock_server.py — Multi-device Cisco REST API mock for classroom use
--------------------------------------------------------------------
Simulates 8 Cisco routers on different IP addresses.
Each device has a unique hostname, interfaces, and status.

Run with:
    python mock_server.py

Listens on http://localhost:8080
Leave running in Terminal 1, use Terminal 2 for the scripts.
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

DEVICES = {
    "192.168.1.1": {
        "hostname": "HQ-RTR-01",
        "location": "Headquarters - Server Room A",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN Uplink - ISP1"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "LAN Segment A"},
            {"name": "GigabitEthernet0/2", "enabled": True,  "oper-status": "up",   "description": "LAN Segment B"},
            {"name": "GigabitEthernet0/3", "enabled": False, "oper-status": "down", "description": "Unused"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "192.168.1.2": {
        "hostname": "HQ-RTR-02",
        "location": "Headquarters - Server Room A",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN Uplink - ISP2"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "LAN Segment C"},
            {"name": "GigabitEthernet0/2", "enabled": True,  "oper-status": "down", "description": "Failover Link - DOWN"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.1.1": {
        "hostname": "BRANCH-NYC-01",
        "location": "New York Branch Office",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN to HQ"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "Office LAN"},
            {"name": "GigabitEthernet0/2", "enabled": False, "oper-status": "down", "description": "Not configured"},
            {"name": "Serial0/0/0",        "enabled": True,  "oper-status": "up",   "description": "Backup WAN"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.2.1": {
        "hostname": "BRANCH-LAX-01",
        "location": "Los Angeles Branch Office",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN to HQ"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "Office LAN"},
            {"name": "GigabitEthernet0/2", "enabled": True,  "oper-status": "down", "description": "VoIP Segment - DOWN"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.3.1": {
        "hostname": "BRANCH-CHI-01",
        "location": "Chicago Branch Office",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN to HQ"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "Office LAN"},
            {"name": "Serial0/0/0",        "enabled": True,  "oper-status": "up",   "description": "MPLS Link"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.4.1": {
        "hostname": "BRANCH-MIA-01",
        "location": "Miami Branch Office",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "WAN to HQ"},
            {"name": "GigabitEthernet0/1", "enabled": False, "oper-status": "down", "description": "LAN - NEEDS REPAIR"},
            {"name": "GigabitEthernet0/2", "enabled": False, "oper-status": "down", "description": "Not configured"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.5.1": {
        "hostname": "DC-CORE-01",
        "location": "Data Center - Rack 12",
        "interfaces": [
            {"name": "GigabitEthernet0/0",    "enabled": True, "oper-status": "up",   "description": "Core Uplink 1"},
            {"name": "GigabitEthernet0/1",    "enabled": True, "oper-status": "up",   "description": "Core Uplink 2"},
            {"name": "GigabitEthernet0/2",    "enabled": True, "oper-status": "up",   "description": "Server Farm A"},
            {"name": "GigabitEthernet0/3",    "enabled": True, "oper-status": "up",   "description": "Server Farm B"},
            {"name": "TenGigabitEthernet1/0", "enabled": True, "oper-status": "up",   "description": "10G Backbone"},
            {"name": "Loopback0",             "enabled": True, "oper-status": "up",   "description": "Mgmt"},
        ]
    },
    "10.0.6.1": {
        "hostname": "REMOTE-VPN-01",
        "location": "Remote VPN Concentrator",
        "interfaces": [
            {"name": "GigabitEthernet0/0", "enabled": True,  "oper-status": "up",   "description": "Public Internet"},
            {"name": "GigabitEthernet0/1", "enabled": True,  "oper-status": "up",   "description": "Internal Network"},
            {"name": "Tunnel0",            "enabled": True,  "oper-status": "up",   "description": "VPN Tunnel HQ"},
            {"name": "Tunnel1",            "enabled": True,  "oper-status": "down", "description": "VPN Tunnel Backup - DOWN"},
            {"name": "Loopback0",          "enabled": True,  "oper-status": "up",   "description": "Mgmt"},
        ]
    },
}

def build_routes():
    routes = {}
    for ip, device in DEVICES.items():
        routes[f"/device/{ip}/restconf/data/Cisco-IOS-XE-native:native/hostname"] = {
            "Cisco-IOS-XE-native:hostname": device["hostname"]
        }
        routes[f"/device/{ip}/restconf/data/ietf-interfaces:interfaces/interface"] = {
            "ietf-interfaces:interface": [
                {"name": i["name"], "ietf-interfaces:enabled": i["enabled"], "description": i["description"]}
                for i in device["interfaces"]
            ]
        }
        routes[f"/device/{ip}/restconf/data/ietf-interfaces:interfaces-state/interface"] = {
            "ietf-interfaces:interface": [
                {"name": i["name"], "oper-status": i["oper-status"]}
                for i in device["interfaces"]
            ]
        }
    return routes

ALL_ROUTES = build_routes()

class CiscoMockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?")[0]
        if path in ALL_ROUTES:
            self.send_response(200)
            self.send_header("Content-Type", "application/yang-data+json")
            self.end_headers()
            self.wfile.write(json.dumps(ALL_ROUTES[path]).encode())
            print(f"  200  GET {path}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "endpoint not found"}')

    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8080
    server = HTTPServer((HOST, PORT), CiscoMockHandler)

    print(f"""
╔══════════════════════════════════════════════════════════╗
║         Cisco Mock API Server — 8 devices ready          ║
╠══════════════════════════════════════════════════════════╣""")
    for ip, device in DEVICES.items():
        up = sum(1 for i in device["interfaces"] if i["oper-status"] == "up")
        total = len(device["interfaces"])
        print(f"║  {device['hostname']:<20} {ip:<16} {up}/{total} up  ║")
    print(f"""╠══════════════════════════════════════════════════════════╣
║  Running at: http://{HOST}:{PORT}                       ║
║  Leave this terminal open.                               ║
║  Open a NEW terminal and run: python health_card.py      ║
║  Press Ctrl+C to stop.                                   ║
╚══════════════════════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
