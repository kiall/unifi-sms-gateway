"""Support for Fully Kiosk Browser notifications."""

from __future__ import annotations
from dataclasses import dataclass

from collections.abc import Callable
from typing import Any
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
    SensorDeviceClass,
)
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.core import callback

from . import UnifiSMSGatewayConfigEntry
from .coordinator import UnifiSMSGatewayCoordinator
from .entity import UnifiSMSGatewayEntity
from .const import LOGGER, DOMAIN


@dataclass(kw_only=True)
class UnifiSMSGatewayEntityDescription(SensorEntityDescription):
    """Describes Unifi SMS Gateway sensor entity."""

    value_fn: Callable[[Any], StateType]


SENSORS: tuple[UnifiSMSGatewayEntityDescription, ...] = (
    # Phone Number Sensor
    UnifiSMSGatewayEntityDescription(
        key="phone_number",
        translation_key="phone_number",
        # state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.data.phone_number,
    ),
    # IMSI Sensor
    UnifiSMSGatewayEntityDescription(
        key="imsi",
        translation_key="imsi",
        # state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.data.imsi,
    ),
    # Home Network Operator Sensor
    UnifiSMSGatewayEntityDescription(
        key="home_network_operator",
        translation_key="home_network_operator",
        # state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: coordinator.data.home_network_operator,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: UnifiSMSGatewayConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the Unifi SMS Gateway sensor entities."""
    coordinator = hass.data[DOMAIN][config_entry.entry_id]["coordinator"]

    await coordinator.async_config_entry_first_refresh()

    async_add_entities(
        UnifiSMSGatewaySensorEntity(coordinator, description) for description in SENSORS
    )


class UnifiSMSGatewaySensorEntity(UnifiSMSGatewayEntity, SensorEntity):
    """Implement the sensor entity for Unifi SMS Gateway."""

    entity_description: UnifiSMSGatewayEntityDescription

    def __init__(
        self,
        coordinator: UnifiSMSGatewayCoordinator,
        entity_description: UnifiSMSGatewayEntityDescription,
    ) -> None:
        """Initialize the entity."""
        self._attr_unique_id = "sensor-%s" % entity_description.key

        UnifiSMSGatewayEntity.__init__(self, coordinator, entity_description)
        SensorEntity.__init__(self)

        LOGGER.debug("Initialized sensor entity for unique_id: %s", self.unique_id)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._attr_available = True

        self._attr_native_value = self.entity_description.value_fn(self.coordinator)

        self.async_write_ha_state()
