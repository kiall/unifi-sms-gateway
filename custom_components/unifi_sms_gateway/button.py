"""Support for Fully Kiosk Browser notifications."""

from __future__ import annotations
from dataclasses import dataclass
import asyncio

from homeassistant.components.button import (
    ButtonEntity,
    ButtonEntityDescription,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import UnifiSMSGatewayConfigEntry
from .coordinator import UnifiSMSGatewayCoordinator
from .entity import UnifiSMSGatewayEntity
from .const import LOGGER, DOMAIN


@dataclass(kw_only=True)
class UnifiSMSGatewayButtonEntityDescription(ButtonEntityDescription):
    """Describes Unifi SMS Gateway button entity."""


BUTTONS: tuple[UnifiSMSGatewayButtonEntityDescription, ...] = (
    # Clear Stored Messages Button
    UnifiSMSGatewayButtonEntityDescription(
        key="clear_stored_messages",
        translation_key="clear_stored_messages",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UnifiSMSGatewayConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Unifi SMS Gateway button entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        UnifiSMSGatewayButtonEntity(coordinator, description) for description in BUTTONS
    )


class UnifiSMSGatewayButtonEntity(UnifiSMSGatewayEntity, ButtonEntity):
    """Implement the button entity for Unifi SMS Gateway."""

    entity_description: UnifiSMSGatewayButtonEntityDescription

    def __init__(
        self,
        coordinator: UnifiSMSGatewayCoordinator,
        entity_description: UnifiSMSGatewayButtonEntityDescription,
    ) -> None:
        """Initialize the entity."""
        self._attr_unique_id = "button-%s" % entity_description.key

        UnifiSMSGatewayEntity.__init__(self, coordinator, entity_description)
        ButtonEntity.__init__(self)

        LOGGER.debug("Initialized button entity for unique_id: %s", self.unique_id)

    def press(self) -> None:
        """Handle the button press."""
        return asyncio.run(self.async_press())

    async def async_press(self) -> None:
        """Handle the button press."""
        LOGGER.debug("Button pressed for unique_id: %s", self.unique_id)

        fn = getattr(self, f"async_press_{self.entity_description.key}", None)
        if fn is not None:
            await fn()
        else:
            LOGGER.error(
                "No handler function found for button with unique_id: %s",
                self.unique_id,
            )

    async def async_press_clear_stored_messages(self) -> None:
        """Clear stored messages on the gateway."""
        await self.coordinator.async_clear_stored_messages()
