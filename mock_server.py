"""
mock_server.py — Fake Cisco REST API for classroom use
-------------------------------------------------------
Mimics the RESTCONF endpoints used in health_card.py.
Returns realistic Cisco IOS-XE style JSON responses.

Run it with:
    python mock_server.py

It listens on http://localhost:8080
Leave it running in one terminal, use a second terminal for health_card.py
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json

# ── Fake device data ──────────────────────────────────────────────────────────
# Edit this to change what students see. Good teaching moment on Day 13 (JSON).

DEVICE = {
    "hostname": "csr1000v-classroom",
    "interfaces": [
        {"name": "GigabitEthernet1", "enabled": True,  "oper-status": "up",   "description": "WAN uplink"},
        {"name": "GigabitEthernet2", "enabled": True,  "oper-status": "up",   "description": "LAN segment A"},
        {"name": "GigabitEthernet3", "enabled": True,  "oper-status": "down", "description": "LAN segment B"},
        {"name": "GigabitEthernet4", "enabled": False, "oper-status": "down", "description": "Not configured"},
        {"name": "Loopback0",        "enabled": True,  "oper-status": "up",   "description": "Management"},
        {"name": "Loopback1",        "enabled": True,  "oper-status": "up",   "description": "OSPF router-id"},
    ]
}

# ── URL routing ───────────────────────────────────────────────────────────────
# Maps URL paths to response data, just like a real REST API would.

ROUTES = {
    "/restconf/data/Cisco-IOS-XE-native:native/hostname": {
        "Cisco-IOS-XE-native:hostname": DEVICE["hostname"]
    },
    "/restconf/data/ietf-interfaces:interfaces/interface": {
        "ietf-interfaces:interface": [
            {
                "name": iface["name"],
                "ietf-interfaces:enabled": iface["enabled"],
                "description": iface["description"]
            }
            for iface in DEVICE["interfaces"]
        ]
    },
    "/restconf/data/ietf-interfaces:interfaces-state/interface": {
        "ietf-interfaces:interface": [
            {
                "name": iface["name"],
                "oper-status": iface["oper-status"]
            }
            for iface in DEVICE["interfaces"]
        ]
    },
}

# ── Request handler ───────────────────────────────────────────────────────────

class CiscoMockHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        # Strip query strings if any
        path = self.path.split("?")[0]

        if path in ROUTES:
            self.send_response(200)
            self.send_header("Content-Type", "application/yang-data+json")
            self.end_headers()
            self.wfile.write(json.dumps(ROUTES[path]).encode())
            print(f"  200  GET {path}")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error": "endpoint not found"}')
            print(f"  404  GET {path}")

    # Suppress the default request log line so output stays clean
    def log_message(self, format, *args):
        pass


# ── Start the server ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    HOST = "localhost"
    PORT = 8080
    server = HTTPServer((HOST, PORT), CiscoMockHandler)
    print(f"""
╔══════════════════════════════════════════════════╗
║       Cisco Mock API Server — classroom use      ║
╠══════════════════════════════════════════════════╣
║  Running at:  http://{HOST}:{PORT}              ║
║  Device:      {DEVICE['hostname']:<28} ║
║  Interfaces:  {len(DEVICE['interfaces'])} configured                       ║
╠══════════════════════════════════════════════════╣
║  Leave this terminal open.                       ║
║  Open a NEW terminal and run:                    ║
║      python health_card.py                       ║
║                                                  ║
║  Press Ctrl+C to stop the server.                ║
╚══════════════════════════════════════════════════╝
""")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
