"""Config flow for Unifi SMS Gateway integration."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.service_info.hassio import HassioServiceInfo
from homeassistant.helpers.selector import (TextSelector, TextSelectorConfig)

from .const import DOMAIN, LOGGER, CONF_NAME, DEFAULT_NAME, CONF_HOST, DEFAULT_HOST, CONF_PORT, DEFAULT_PORT, CONF_PASSWORD ,CONF_DESTINATION_NUMBERS


def user_form_schema(user_input: dict[str, Any] | None) -> vol.Schema:
    """Return user form schema."""
    user_input = user_input or {}
    return vol.Schema(
        {
            vol.Required(
                CONF_HOST, default=user_input.get(CONF_HOST, DEFAULT_HOST)
            ): str,
            vol.Required(
                CONF_PORT, default=user_input.get(CONF_PORT, DEFAULT_PORT)
            ): int,
            vol.Required(
                CONF_PASSWORD, default=user_input.get(CONF_PASSWORD)
            ): str,
            vol.Optional(
                CONF_DESTINATION_NUMBERS, default=user_input.get(CONF_DESTINATION_NUMBERS, [])
            ): TextSelector(config=TextSelectorConfig(multiple=True, type="tel")),
        }
    )

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, str]:
    """Validate the user input allows us to connect."""

    if data[CONF_HOST] == "":
        raise ConfigError(translation_key="host_required")

    # TODO: Attempt to contact SMS Gateway API to verify config details

    # CONF_NAME is only present in the imported YAML data.
    return {"title": data.get(CONF_NAME) or DEFAULT_NAME}


class UnifiSMSGatewayConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unifi SMS Gateway."""

    VERSION = 1
    hassio_discovery: dict[str, Any] | None = None

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=user_form_schema(user_input)
            )

        self._async_abort_entries_match(
            {CONF_HOST: user_input[CONF_HOST], CONF_PORT: user_input[CONF_PORT]}
        )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except Exception:
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(user_input[CONF_HOST])
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=user_form_schema(user_input), errors=errors
        )

    async def async_step_reconfigure(self, user_input: dict[str, Any] | None = None):
        """Handle reconfiguration."""
        if user_input is None:
            existing_config_entry = self.hass.config_entries.async_get_entry(
                self.context["entry_id"]
            )

            return self.async_show_form(
                step_id="reconfigure", data_schema=user_form_schema(existing_config_entry.data)
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except Exception:
            LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            await self.async_set_unique_id(user_input[CONF_HOST])
            self._abort_if_unique_id_mismatch()
            return self.async_update_reload_and_abort(
                self._get_reconfigure_entry(),
                data_updates=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure", data_schema=user_form_schema(user_input), errors=errors
        )

    async def async_step_hassio(
        self, discovery_info: HassioServiceInfo
    ) -> ConfigFlowResult:
        """Handle the discovery step via hassio."""

        await self.async_set_unique_id(discovery_info.config[CONF_HOST])
        self._abort_if_unique_id_configured(discovery_info.config)

        self.hassio_discovery = discovery_info.config
        self.context["title_placeholders"] = {"host": discovery_info.config[CONF_HOST]}

        return await self.async_step_hassio_confirm()

    async def async_step_hassio_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm Supervisor discovery."""
        assert self.hassio_discovery

        if user_input is None:
            return self.async_show_form(
                step_id="hassio_confirm",
                description_placeholders={"addon": self.hassio_discovery["addon"]},
            )

        self.hassio_discovery.pop("addon")

        try:
            info = await validate_input(self.hass, self.hassio_discovery)
        except Exception:
            LOGGER.exception("Unexpected exception")
            return self.async_abort(reason="unknown")

        return self.async_create_entry(title=info["title"], data=self.hassio_discovery)

class ConfigError(HomeAssistantError):
    """Error to indicate a configuration issue."""