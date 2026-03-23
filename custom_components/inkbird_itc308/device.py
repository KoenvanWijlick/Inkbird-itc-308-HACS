"""Wrapper class for communicating with the Inkbird ITC‑308 controller.

This module wraps the Tinytuya `Device` class and provides helper
functions for reading and writing data points.  Tinytuya is a Python
library that speaks the Tuya local protocol directly over the LAN.  To
communicate with the device you need its device ID, IP address and
local key.  These values are obtained from the Tuya IoT platform or
via the `tuya-cli wizard` tool (see README and report for details).
"""

from __future__ import annotations

import logging
from typing import Any

import tinytuya

_LOGGER = logging.getLogger(__name__)


class InkbirdDevice:
    """Represents a single Inkbird ITC‑308 device on the local network."""

    def __init__(self, device_id: str, ip: str, local_key: str) -> None:
        """Initialise the Tinytuya device and set the protocol version.

        The ITC‑308 uses protocol version 3.3 as per the ESPHome
        documentation.  If your device fails to respond try setting
        another version using `self.device.set_version(...)`.

        Args:
            device_id: The 20‑character Tuya device ID.
            ip: The local IP address of the device.
            local_key: The 16‑character local key.
        """
        self._device = tinytuya.Device(device_id, ip, local_key)
        # Set to protocol 3.3 which is used by ITC‑308 controllers.
        self._device.set_version(3.3)

    def status(self) -> dict[str, Any]:
        """Return the current status dictionary (dps) from the device.

        Tinytuya returns a dictionary with keys 'cmd', 'data', 'dps', etc.
        We extract the 'dps' sub‑dictionary and return it.  If an
        exception occurs, we log and re‑raise it for the caller to
        handle.
        """
        try:
            status = self._device.status()
            dps = status.get("dps", {})
            return dps
        except Exception as err:
            _LOGGER.error("Error fetching status from device: %s", err)
            raise

    def set_dp(self, dp: int, value: Any) -> Any:
        """Set a single data point on the device.

        Args:
            dp: The data point number to set.
            value: The value to write.  For number values the caller
                should already have converted to the raw units using
                the scale factor from const.DP_MAP.

        Returns:
            The response from Tinytuya.  The caller can inspect this
            dictionary if needed.
        """
        try:
            result = self._device.set_dps({dp: value})
            return result
        except Exception as err:
            _LOGGER.error("Error setting DP %s to %s: %s", dp, value, err)
            raise
