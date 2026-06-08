#!/usr/bin/with-contenv bashio
set -e

API_HOST=$(bashio::config 'api_host')
RELAY_HOST=$(bashio::config 'relay_host')
BUFFER_LIMIT=$(bashio::config 'buffer_limit')
DEBUG=$(bashio::config 'debug')
DISABLE_GC_FIX=$(bashio::config 'disable_gc_fix')

# Append default port if user did not specify one.
case "${API_HOST}" in
    *:*) API_PARAM="${API_HOST}" ;;
    *)   API_PARAM="${API_HOST}:443" ;;
esac

ARGS="-api_host=${API_PARAM}"

if [ -n "${RELAY_HOST}" ]; then
    case "${RELAY_HOST}" in
        *:*) RELAY_PARAM="${RELAY_HOST}" ;;
        *)   RELAY_PARAM="${RELAY_HOST}:8888" ;;
    esac
    ARGS="${ARGS} -relay_host=${RELAY_PARAM}"
fi

if [ "${BUFFER_LIMIT}" -gt 0 ] 2>/dev/null; then
    ARGS="${ARGS} -buffer_limit=${BUFFER_LIMIT}"
fi

if bashio::var.true "${DEBUG}"; then
    ARGS="${ARGS} -debug"
fi

if bashio::var.true "${DISABLE_GC_FIX}"; then
    ARGS="${ARGS} -disable_gc_fix"
fi

# Start the configuration web UI (served through Home Assistant Ingress).
bashio::log.info "Starting config web UI on :8099"
python3 /webui/server.py &

bashio::log.info "Launching cloudgateway ${ARGS}"
exec /usr/local/bin/cloudgateway ${ARGS}
