# Changelog

## 1.1.2

- Added a `debug_memory` option (debug builds): when enabled, the gateway runs
  garbage collection plus `FreeOSMemory` once an hour instead of every 200 ms,
  to measure the memory/CPU trade-off of the leak fix. Keep `disable_gc_fix`
  off so the periodic GC stays active.

## 1.1.1

- Fixed the web UI showing a false "restart request failed" message after
  saving. The restart stops the add-on (and the page connection), so that is
  the expected success path — the UI now reports success and reconnects.

## 1.1.0

- Added a web UI (Home Assistant Ingress) to edit the gateway settings and copy
  the device MAC address — the id used to register the device in Corvid Cloud.
- Settings changed in the UI are saved through the Supervisor API and applied by
  restarting the add-on, identical to the native configuration screen.

## 1.0.0

- Initial public release of the Corvid Cloud Gateway add-on.
- Builds locally on the user's Home Assistant Supervisor (amd64, aarch64, armv7).
- Options: `api_host`, `relay_host`, `buffer_limit`, `debug`.
- Runs with `host_network: true` for ONVIF/RTSP discovery on the LAN.
