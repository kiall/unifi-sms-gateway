from datetime import timedelta

from .client import (
    UnifiSMSGatewayClient,
    UnifiSMSGatewayData,
)
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
)

from .const import LOGGER, DOMAIN


class UnifiSMSGatewayCoordinator(DataUpdateCoordinator[UnifiSMSGatewayData]):
    """Coordinator for the UniFi SMS Gateway integration."""

    def __init__(self, hass, config_entry, client: UnifiSMSGatewayClient):
        """Initialize the coordinator."""

        super().__init__(
            hass,
            LOGGER,
            # Name of the data. For logging purposes.
            name="UniFi SMS Gateway",
            config_entry=config_entry,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=30),
            # Set always_update to `False` if the data returned from the
            # api can be compared via `__eq__` to avoid duplicate updates
            # being dispatched to listeners
            always_update=True,
        )

        self._client = client

    async def _async_setup(self):
        """Set up the coordinator

        This is the place to set up your coordinator,
        or to load data, that only needs to be loaded once.

        This method will be called automatically during
        coordinator.async_config_entry_first_refresh.
        """
        pass

    async def _async_update_data(self) -> UnifiSMSGatewayData:
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        return await self._client.async_get_data()

    async def async_send_message(self, destination_number: str, message: str):
        """Send a message to the specified destination number."""

        return await self._client.async_send_message(destination_number, message)
