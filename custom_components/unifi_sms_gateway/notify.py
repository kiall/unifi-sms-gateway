"""Support for Fully Kiosk Browser notifications."""

from __future__ import annotations
from collections.abc import Mapping

from homeassistant.components.notify import NotifyEntity, NotifyEntityDescription
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UnifiSMSGatewayConfigEntry
from .coordinator import UnifiSMSGatewayCoordinator
from .entity import UnifiSMSGatewayEntity
from .const import LOGGER, DOMAIN, CONF_DESTINATION_NUMBERS

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UnifiSMSGatewayConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Unifi SMS Gateway notify entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        UnifiSMSGatewayNotifyEntity(coordinator, NotifyEntityDescription(
            key="notify",
            translation_key="notify",
        ), destination_number) for destination_number in config_entry.data.get(CONF_DESTINATION_NUMBERS, [])
    )


class UnifiSMSGatewayNotifyEntity(UnifiSMSGatewayEntity, NotifyEntity):
    """Implement the notify entity for Unifi SMS Gateway."""
    entity_description: NotifyEntityDescription

    destination_number: str | None = None

    def __init__(self, coordinator: UnifiSMSGatewayCoordinator, entity_description: NotifyEntityDescription, destination_number: str) -> None:
        """Initialize the entity."""

        self._attr_unique_id = "notify-%s" % destination_number
        self.destination_number = destination_number
        self.translation_placeholders: Mapping[str, str] = {"destination_number": destination_number}

        UnifiSMSGatewayEntity.__init__(self, coordinator, entity_description)
        NotifyEntity.__init__(self)

        LOGGER.debug("Initialized notify entity for destination number: %s", self.destination_number)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_available = True
        self.async_write_ha_state()

    def send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""
        LOGGER.info("Sending message: %s", message)

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send a message."""
        LOGGER.info("Sending message: %s", message)
