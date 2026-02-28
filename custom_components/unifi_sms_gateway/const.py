import logging

LOGGER = logging.getLogger(__package__)
DOMAIN = "unifi_sms_gateway"
PLATFORMS = ["notify", "sensor"]

CONF_NAME = "name"
DEFAULT_NAME = "UniFi SMS Gateway"

CONF_HOST = "host"
DEFAULT_HOST = "localhost"

CONF_PORT = "port"
DEFAULT_PORT = "8585"

CONF_PASSWORD = "password"

CONF_DESTINATION_NUMBERS = "destination_numbers"
