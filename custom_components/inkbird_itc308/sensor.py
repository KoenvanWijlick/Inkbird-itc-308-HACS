"""Sensor platform for the Inkbird ITC‑308 controller.

This module defines Home Assistant sensor entities that report values
from the ITC‑308.  Sensors are created for data points defined in
const.DP_MAP where `platform` == 'sensor'.  Values are scaled from raw
Tuya units to human‑readable units using the defined scale factors.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, DATA_COORDINATOR, DATA_DEVICE, DP_MAP

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Inkbird sensors based on a config entry."""
    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data[DATA_COORDINATOR]

    entities: list[SensorEntity] = []
    for dp, meta in DP_MAP.items():
        if meta.get("platform") != "sensor":
            continue
        description = SensorEntityDescription(
            key=str(dp),
            name=meta.get("name"),
            unit_of_measurement=meta.get("unit"),
            device_class=meta.get("device_class"),
            state_class=meta.get("state_class"),
        )
        entities.append(InkbirdSensor(coordinator, dp, description, meta))

    async_add_entities(entities)


class InkbirdSensor(CoordinatorEntity, SensorEntity):
    """Representation of a sensor entity backed by the coordinator."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator,
        dp: int,
        description: SensorEntityDescription,
        meta: dict[str, Any],
    ) -> None:
        """Initialise the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._dp = dp
        self._scale = meta.get("scale", 1)
        self._mapping = meta.get("mapping")

        # Use config entry id and dp for unique ID
        self._attr_unique_id = f"{coordinator.config_entry.entry_id}_{dp}"

    @property
    def native_value(self) -> Any:
        """Return the value of the sensor."""
        dps = self.coordinator.data or {}
        raw = dps.get(self._dp)
        if raw is None:
            return None
        if self._mapping:
            # Map raw numeric code to string state for relay
            return self._mapping.get(raw, raw)
        try:
            value = raw * self._scale
        except TypeError:
            # If not numeric, return raw value directly
            return raw
        return value