#!/usr/bin/env bash

export UNIFI_IP="$(bashio::config 'unifi_ip')"
export UNIFI_USER="$(bashio::config 'unifi_user')"
export UNIFI_PASSWORD="$(bashio::config 'unifi_password')"
export SMS_AUTH="$(bashio::config 'api_key')"

exec python3 /app/sms.py
