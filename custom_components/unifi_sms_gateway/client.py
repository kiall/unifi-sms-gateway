import asyncio
from dataclasses import dataclass
import logging

import requests

LOGGER = logging.getLogger(__package__)

@dataclass(kw_only=True)
class UnifiSMSGatewayData:
    mac: list[str]
    phone_number: str
    imsi: str
    home_network_operator: str


class UnifiSMSGatewayClient:
    """Client for the UniFi SMS Gateway."""

    def __init__(self, api_url: str, api_token: str):
        """Initialize the client."""

        LOGGER.warning("Initializing UnifiSMSGatewayClient with API URL: %s", api_url)

        self._api_url = api_url
        self._api_token = api_token

    async def async_get_data(self) -> UnifiSMSGatewayData:
        """ Fetches & combines all data from the UniFi SMS Gateway."""
        status = await self._async_get_status()

        return UnifiSMSGatewayData(
            mac=status["mac"],
            phone_number=status["sim"]["Phone Number"],
            imsi=status["sim"]["IMSI"],
            home_network_operator=status["sim"]["Home Network Operator"],
        )

    async def _async_get_status(self):
        """Fetch status data from the UniFi SMS Gateway."""
        def blocking_task(self):
            return requests.get(
                f"{self._api_url}/sms/status",
                headers={"Authorization": f"Bearer {self._api_token}"},
                timeout=10,
            )

        response = await asyncio.to_thread(blocking_task, self)

        return response.json()

    async def async_get_data(self) -> UnifiSMSGatewayData:
        """ Fetches & combines all data from the UniFi SMS Gateway."""
        status = await self._async_get_status()

        return UnifiSMSGatewayData(
            mac=status["mac"],
            phone_number=status["sim"]["Phone Number"],
            imsi=status["sim"]["IMSI"],
            home_network_operator=status["sim"]["Home Network Operator"],
        )

    async def async_send_message(self, destination_number: str, message: str):
        """Send a message to the specified destination number."""
        def blocking_task(self):
            return requests.post(
                f"{self._api_url}/sms/send/{destination_number}",
                headers={"Authorization": f"Bearer {self._api_token}"},
                json={"message": message},
                timeout=10,
            )

        response = await asyncio.to_thread(blocking_task, self)

        return response.json()
