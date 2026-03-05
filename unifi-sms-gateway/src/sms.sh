#!/usr/bin/with-contenv bashio

set -euo pipefail

export ULTE_SSH_IP="$(bashio::config 'ulte_ssh_ip')"
export ULTE_SSH_USER="$(bashio::config 'ulte_ssh_user')"
export ULTE_SSH_PASSWORD="$(bashio::config 'ulte_ssh_password')"
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
    bashio::log.info "Successfully sent discovery information to Home Assistant."
else
    bashio::log.error "Discovery message to Home Assistant failed!"
fi

exec python3 /app/sms.py
