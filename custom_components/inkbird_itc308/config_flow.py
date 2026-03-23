"""Config flow for the Inkbird ITC‑308 WiFi integration.

This module implements the UI flow that collects the required
information from the user: the Tuya device ID, the device's IP
address, the local key and an optional polling interval.  It also
performs basic validation (e.g. ensuring the device ID has the
expected length) and prevents adding the same device twice.
"""

from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST, CONF_NAME
from homeassistant.core import HomeAssistant

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

CONF_DEVICE_ID = "device_id"
CONF_LOCAL_KEY = "local_key"
CONF_SCAN_INTERVAL = "scan_interval"


class InkbirdConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Inkbird ITC‑308."""

    VERSION = 1
    MINOR_VERSION = 0

    def __init__(self) -> None:
        """Initialise the config flow."""
        super().__init__()

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        """Handle the initial step where the user inputs device details."""
        errors: dict[str, str] = {}

        if user_input is not None:
            device_id = user_input[CONF_DEVICE_ID]
            # Check if this device is already configured
            await self.async_set_unique_id(device_id)
            self._abort_if_unique_id_configured()

            # Save config entry
            return self.async_create_entry(
                title=user_input.get(CONF_NAME) or f"ITC‑308 ({device_id[-4:]})",
                data={
                    "device_id": device_id,
                    "ip_address": user_input[CONF_HOST],
                    "local_key": user_input[CONF_LOCAL_KEY],
                    # Convert scan interval to seconds, default to 30
                    "scan_interval": user_input.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL.total_seconds()),
                },
            )

        # Present the form to the user
        default_scan = int(DEFAULT_SCAN_INTERVAL.total_seconds())
        data_schema = vol.Schema(
            {
                vol.Required(CONF_DEVICE_ID): vol.All(str, vol.Length(min=16)),
                vol.Required(CONF_HOST): str,
                vol.Required(CONF_LOCAL_KEY): vol.All(str, vol.Length(min=16)),
                vol.Optional(CONF_SCAN_INTERVAL, default=default_scan): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=3600)
                ),
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)

    async def async_step_import(self, import_data: dict[str, Any]):
        """Handle import from YAML.  This integration does not support YAML."""
        return await self.async_step_user(import_data)