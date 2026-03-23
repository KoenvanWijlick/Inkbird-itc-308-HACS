"""Number platform for the Inkbird ITC‑308 controller.

This module defines numeric entities for configurable parameters such as
target temperature, calibration offset and alarm limits.  Each number
entity reads its value from the coordinator and writes changes back to
the device via the `InkbirdDevice` wrapper.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR, DATA_DEVICE, DP_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Inkbird number entities based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]
    device = data[DATA_DEVICE]

    entities: list[NumberEntity] = []
    for dp, meta in DP_MAP.items():
        if meta.get("platform") != "number":
            continue
        description = NumberEntityDescription(
            key=str(dp),
            name=meta.get("name"),
            native_unit_of_measurement=meta.get("unit"),
            native_min_value=meta.get("min"),
            native_max_value=meta.get("max"),
            native_step=meta.get("step"),
        )
        entities.append(InkbirdNumber(coordinator, device, dp, description, meta))

    async_add_entities(entities)


class InkbirdNumber(CoordinatorEntity, NumberEntity):
    """Representation of a numeric entity backed by the coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        device,
        dp: int,
        description: NumberEntityDescription,
        meta: dict[str, Any],
    ) -> None:
        """Initialise the number entity."""
        super().__init__(coordinator)
        self.entity_description = description
        self._device = device
        self._dp = dp
        self._scale = meta.get("scale", 1)

        # Unique ID is config entry id + dp
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{dp}"

    @property
    def native_value(self) -> float | None:
        """Return the current value in human units."""
        dps = self.coordinator.data or {}
        raw = dps.get(self._dp)
        if raw is None:
            return None
        try:
            value = raw * self._scale
        except TypeError:
            return raw
        return float(value)

    async def async_set_native_value(self, value: float) -> None:
        """Set a new value via Tinytuya.

        We divide by the scale to convert to the raw units expected by
        the device.  The Tinytuya library runs in the executor to avoid
        blocking the event loop.  After writing the value we request
        the coordinator to refresh so the UI updates promptly.
        """
        raw_value = int(round(value / self._scale))
        _LOGGER.debug(
            "Setting DP %s to %s (raw=%s)", self._dp, value, raw_value
        )
        await self.hass.async_add_executor_job(self._device.set_dp, self._dp, raw_value)
        # Refresh coordinator to pick up new state
        await self.coordinator.async_request_refresh()