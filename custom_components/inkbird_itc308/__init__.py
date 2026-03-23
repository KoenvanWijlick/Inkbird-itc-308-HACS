"""Home Assistant integration for the Inkbird ITC‑308 WiFi controller.

This custom integration allows Home Assistant to communicate with an
Inkbird ITC‑308 WiFi temperature controller using the local Tuya
protocol via the `tinytuya` library.  It exposes the controller's
temperature sensor, set‑point and other parameters as native Home
Assistant entities such as sensors and numbers.  The integration is
configured via the UI (config flow) where the user enters the device
ID, IP address and local key.  Values are polled using a
DataUpdateCoordinator and entities subscribe to updates.

See the report accompanying this integration for details on how to
obtain the required credentials and how the data points are mapped to
Home Assistant entities.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import Any, Callable

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    CoordinatorEntity,
)

from .const import (
    DOMAIN,
    DATA_COORDINATOR,
    DATA_DEVICE,
    DP_MAP,
    DEFAULT_SCAN_INTERVAL,
)
from .device import InkbirdDevice

_LOGGER = logging.getLogger(__name__)


async def async_setup(_hass: HomeAssistant, _config: dict[str, Any]) -> bool:
    """Set up the integration via YAML (not supported)."""
    # This integration is configured via the UI, so return True
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up an Inkbird ITC‑308 controller from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    # Pull credentials from the entry data
    device_id: str = entry.data["device_id"]
    ip: str = entry.data["ip_address"]
    local_key: str = entry.data["local_key"]
    update_interval: int | None = entry.data.get("scan_interval")

    # Instantiate the device wrapper
    device = InkbirdDevice(device_id, ip, local_key)

    # Define the async update method for the coordinator
    async def async_update_data() -> dict[int, Any]:
        """Fetch the latest status from the device asynchronously."""
        return await hass.async_add_executor_job(device.status)

    # Determine scan interval
    scan_interval = timedelta(seconds=update_interval) if update_interval else DEFAULT_SCAN_INTERVAL

    # Create the coordinator
    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=f"{DOMAIN} {device_id}",
        update_method=async_update_data,
        update_interval=scan_interval,
    )

    hass.data[DOMAIN][entry.entry_id] = {
        DATA_COORDINATOR: coordinator,
        DATA_DEVICE: device,
    }

    # Perform an initial refresh to populate data
    await coordinator.async_config_entry_first_refresh()

    # Set up platforms based on DP map: gather unique platforms
    platforms = {v["platform"] for v in DP_MAP.values()}

    # Forward entry setup to the individual platforms
    await hass.config_entries.async_forward_entry_setups(entry, list(platforms))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload an Inkbird config entry."""
    data = hass.data[DOMAIN].pop(entry.entry_id)
    coordinator: DataUpdateCoordinator = data[DATA_COORDINATOR]

    # Unload entity platforms
    platforms = {v["platform"] for v in DP_MAP.values()}
    unload_ok = await hass.config_entries.async_unload_platforms(entry, list(platforms))

    if unload_ok:
        # Remove the coordinator reference
        coordinator.async_unregister_listener(lambda: None)
    return unload_ok