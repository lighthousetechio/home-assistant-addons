# Corvid Cloud Gateway — Home Assistant Add-on

Corvid Cloud is an IP video surveillance platform with remote access, recording, and license plate recognition (LPR).

This add-on runs the **Cloud Gateway** agent on your Home Assistant host. The gateway auto-discovers RTSP/ONVIF cameras on your LAN and bridges them to Corvid Cloud through an outbound encrypted connection — no router configuration, no port forwarding, no VPN. Manage your cameras, watch live streams, and review recordings from the Corvid Cloud web app.

## Installation

> **Note:** This is a native Supervisor add-on. Install it from the built-in **Add-on Store**, not from HACS.

1. In Home Assistant: **Settings → Add-ons → Add-on Store**.
2. Open the **⋮** menu (top-right) → **Repositories**.
3. Add `https://github.com/lighthousetechio/home-assistant-addons`.
4. Find **Corvid Cloud Gateway** in the store and click **Install**.
5. Click **Start**.

## Configuration

| Option | Default | Description |
|--------|---------|-------------|
| `api_host` | `stream-api.corvidcloud.com` | Corvid Cloud API endpoint. Port defaults to 443 if omitted. |
| `relay_host` | *(empty)* | Optional relay override. Port defaults to 8888 if omitted. Leave empty to let the API assign one. |
| `buffer_limit` | `0` | Stream buffer limit. `0` uses the binary default. |
| `debug` | `false` | Enable verbose logging. |

## Requirements

- **Home Assistant OS** or **Home Assistant Supervised** — the Supervisor is required to install add-ons.
- Architectures: `amd64`, `aarch64`, `armv7` (covers Raspberry Pi 3/4/5, mini-PCs, most NAS).
- Network: the add-on runs with `host_network: true` so the gateway can discover ONVIF cameras (multicast SSDP) and reach RTSP streams on your LAN.

## How it works

The add-on builds locally on your Supervisor. At build time, the Dockerfile downloads the matching architecture binary. At runtime the gateway:

1. Contacts the Corvid Cloud API and is assigned a relay server.
2. Opens an outbound, encrypted, sticky connection to that relay using the host MAC as identity.
3. Discovers cameras on your LAN (ONVIF/SSDP) and exposes their streams and metadata through the relay.

Your cameras then appear in the Corvid Cloud web app for configuration, viewing, and recording. Nothing on your network is exposed inbound.

## Support

For help or to report a problem, email **support@lighthousetech.io**.
