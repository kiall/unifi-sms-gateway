#!/usr/bin/with-contenv bashio

set -euo pipefail

export UNIFI_IP="$(bashio::config 'unifi_ip')"
export UNIFI_USER="$(bashio::config 'unifi_user')"
export UNIFI_PASSWORD="$(bashio::config 'unifi_password')"
export SMS_AUTH="$(bashio::config 'api_key')"

# Prepare discovery payload
declare discovery_config
discovery_config=$(\
    bashio::var.json \
        host "$(hostname)" \
        port "^8585" \
        password "${SMS_AUTH}" \
)

bashio::log.info "Sending discovery information to Home Assistant..."
if bashio::discovery "unifi_sms_gateway" "${discovery_config}" > /dev/null; then
    bashio::log.info "Successfully send discovery information to Home Assistant."
else
    bashio::log.error "Discovery message to Home Assistant failed!"
fi

exec python3 /app/sms.py
