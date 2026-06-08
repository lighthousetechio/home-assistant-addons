#!/usr/bin/env python3
"""Configuration web UI for the Corvid Cloud Gateway add-on.

Served through Home Assistant Ingress. Reads and writes the add-on options
via the Supervisor API (so changes persist exactly like the native config
screen) and exposes the MAC address of the default-route interface — the
value the Corvid backend uses as the camera/cloud id.
"""

import json
import os
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

PORT = 8099
WEB_DIR = os.path.dirname(os.path.abspath(__file__))
OPTIONS_FILE = "/data/options.json"
SUPERVISOR = "http://supervisor"
TOKEN = os.environ.get("SUPERVISOR_TOKEN", "")

DEFAULTS = {
    "api_host": "stream-api.corvidcloud.com",
    "relay_host": "",
    "buffer_limit": 0,
    "debug": False,
    "disable_gc_fix": False,
}


def read_options():
    cfg = dict(DEFAULTS)
    try:
        with open(OPTIONS_FILE) as f:
            cfg.update(json.load(f))
    except Exception:
        pass
    return cfg


def get_mac():
    """MAC of the interface holding the default route (internet-facing)."""
    try:
        iface = None
        with open("/proc/net/route") as f:
            for line in f.read().splitlines()[1:]:
                parts = line.split()
                if len(parts) > 1 and parts[1] == "00000000":
                    iface = parts[0]
                    break
        if iface:
            with open("/sys/class/net/%s/address" % iface) as f:
                return f.read().strip()
    except Exception:
        pass
    return ""


def supervisor_post(path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else b""
    req = urllib.request.Request(SUPERVISOR + path, data=data, method="POST")
    req.add_header("Authorization", "Bearer " + TOKEN)
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.status, resp.read().decode()


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *args):
        pass

    def _send(self, status, body, content_type="application/json"):
        if isinstance(body, str):
            body = body.encode()
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_json(self, status, obj):
        self._send(status, json.dumps(obj), "application/json")

    def _route(self):
        path = self.path.split("?", 1)[0].rstrip("/")
        return path or "/"

    def do_GET(self):
        route = self._route()
        if route == "/" or route.endswith("/index.html"):
            try:
                with open(os.path.join(WEB_DIR, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except Exception as e:
                self._send(500, str(e), "text/plain")
            return
        if route == "/config":
            cfg = read_options()
            cfg["mac"] = get_mac()
            self._send_json(200, cfg)
            return
        self._send(404, "Not found", "text/plain")

    def do_POST(self):
        route = self._route()
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw = self.rfile.read(length) if length else b"{}"

        if route == "/config":
            try:
                body = json.loads(raw or b"{}")
            except Exception:
                self._send_json(400, {"error": "Invalid JSON body"})
                return

            api_host = str(body.get("api_host", "")).strip()
            if not api_host:
                self._send_json(400, {"error": "api_host is required"})
                return

            relay_host = str(body.get("relay_host", "")).strip()

            try:
                buffer_limit = int(body.get("buffer_limit", 0) or 0)
            except (TypeError, ValueError):
                self._send_json(400, {"error": "buffer_limit must be a number"})
                return
            if buffer_limit < 0:
                buffer_limit = 0

            options = {
                "api_host": api_host,
                "relay_host": relay_host,
                "buffer_limit": buffer_limit,
                "debug": bool(body.get("debug", False)),
                "disable_gc_fix": bool(body.get("disable_gc_fix", False)),
            }

            try:
                supervisor_post("/addons/self/options", {"options": options})
            except Exception as e:
                self._send_json(502, {"error": "Failed to save options: %s" % e})
                return
            self._send_json(200, {"ok": True})
            return

        if route == "/restart":
            try:
                supervisor_post("/addons/self/restart")
            except Exception as e:
                self._send_json(502, {"error": "Restart failed: %s" % e})
                return
            self._send_json(200, {"ok": True})
            return

        self._send(404, "Not found", "text/plain")


def main():
    server = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    print("Config web UI listening on :%d" % PORT, flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
