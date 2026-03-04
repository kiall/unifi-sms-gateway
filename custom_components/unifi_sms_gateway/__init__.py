"""The unifi_sms_gateway component."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import (
    DeviceEntry,
)

from .client import UnifiSMSGatewayClient
from .const import DOMAIN, PLATFORMS, CONF_HOST, CONF_PORT, CONF_PASSWORD
from .coordinator import UnifiSMSGatewayCoordinator

type UnifiSMSGatewayConfigEntry = ConfigEntry[UnifiSMSGatewayCoordinator]


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry):
    """Setup up a config entry."""

    hass.data.setdefault(DOMAIN, {})

    # Initialize the Client
    api_url = (
        f"http://{config_entry.data.get(CONF_HOST)}:{config_entry.data.get(CONF_PORT)}/"
    )
    client = UnifiSMSGatewayClient(api_url, config_entry.data.get(CONF_PASSWORD))

    # Initialize Coordinator
    coordinator = UnifiSMSGatewayCoordinator(hass, config_entry, client)

    # Store Coordinator in hass.data so e.g. notify.py can access it
    hass.data[DOMAIN][config_entry.entry_id] = {
        "coordinator": coordinator,
    }

    # Forward entry setup to platforms (e.g. load notify.py)
    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    config_entry.async_on_unload(config_entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Handle removal of an entry."""
    return await hass.config_entries.async_unload_platforms(config_entry, PLATFORMS)


async def async_reload_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> None:
    """Reload config entry."""
    await hass.config_entries.async_reload(config_entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant, config_entry: ConfigEntry, device_entry: DeviceEntry
) -> bool:
    """Remove a config entry from a device."""
    return True
