
from typing import Any

from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo

from .coordinator import UnifiSMSGatewayCoordinator
from .const import CONF_NAME, DEFAULT_NAME, DOMAIN

class UnifiSMSGatewayEntity(CoordinatorEntity[UnifiSMSGatewayCoordinator]):
    _attr_has_entity_name = True

    def __init__(self, coordinator, entity_description) -> None:
        super().__init__(coordinator)
        self.entity_description = entity_description

    @property
    def device_info(self) -> DeviceInfo:
        """Return the device info."""

        # Determine Device Identifiers based on MAC address(es) returned by the API
        connections: set[tuple[str, str]] = set()
        for mac in self.coordinator.data.mac:
            connections.add((CONNECTION_NETWORK_MAC, mac))

        return DeviceInfo(
            name=self.coordinator.config_entry.data.get(CONF_NAME) or DEFAULT_NAME,
            identifiers={(DOMAIN, self.coordinator.config_entry.entry_id)},
            connections=connections,
        )
