"""Constants for the Inkbird ITC‑308 WiFi integration.

This file defines common constants used throughout the integration. It
collects things like the domain name, default update interval and the
data point definitions for the Inkbird controller. Keeping these in a
single place makes it easy to adjust values in the future and avoids
duplicating magic numbers throughout the code base.

The data points are documented on the ESPHome devices page for the
Inkbird ITC‑308 WiFi controller. Each entry specifies the data point
identifier (as used by the Tuya protocol), the type of entity that
should expose it in Home Assistant, the unit of measurement (if any),
a scaling factor to convert the raw value into human‑readable units and
optional metadata such as value ranges.  See documentation lines
around DP104 on the ESPHome devices page for details【694099120580140†L864-L889】.
"""

from __future__ import annotations

from datetime import timedelta

DOMAIN = "inkbird_itc308"

# Default update interval for polling the device.  A 30 second interval
# strikes a balance between timely updates and not overwhelming the
# controller or the network. Users can adjust this in the config flow.
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# Mapping of Tuya data points (dps) to Home Assistant entity metadata.
# Each entry contains a name, the Home Assistant platform to use, the
# unit of measurement, the scaling factor to apply to the raw value and
# optional min/max/step values for number entities.  The `scale`
# attribute is used both when reading (multiply raw value by scale) and
# when writing (divide user value by scale to convert back to device
# units).
DP_MAP: dict[int, dict[str, object]] = {
    # Current temperature sensor.  DP104 returns a raw integer that
    # needs to be multiplied by 0.1 to get degrees Celsius【694099120580140†L864-L871】.
    104: {
        "name": "Current Temperature",
        "platform": "sensor",
        "unit": "°C",
        "device_class": "temperature",
        "state_class": "measurement",
        "scale": 0.1,
    },
    # Temperature set point.  DP106 uses the same scaling as the
    # temperature sensor.  The valid range for the ITC‑308 controller is
    # approximately 5–42°C according to the ESPHome documentation【694099120580140†L907-L915】.
    106: {
        "name": "Target Temperature",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": 5.0,
        "max": 42.0,
        "step": 0.1,
    },
    # Calibration offset.  DP102 allows adjusting the displayed
    # temperature by ±10°C in 0.1°C increments【694099120580140†L896-L903】.
    102: {
        "name": "Calibration Offset",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": -10.0,
        "max": 10.0,
        "step": 0.1,
    },
    # Compressor delay time.  DP108 stores the compressor delay in
    # minutes; no scaling is required.  Valid values from the controller
    # range from 0–10 minutes【694099120580140†L917-L924】.
    108: {
        "name": "Compressor Delay",
        "platform": "number",
        "unit": "min",
        "scale": 1,
        "min": 0,
        "max": 10,
        "step": 1,
    },
    # Alarm high limit.  DP109 sets the upper alarm threshold; uses the
    # same scaling as temperature【694099120580140†L927-L933】.
    109: {
        "name": "Alarm High Limit",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": 0.0,
        "max": 60.0,
        "step": 0.1,
    },
    # Alarm low limit.  DP110 sets the lower alarm threshold【694099120580140†L936-L942】.
    110: {
        "name": "Alarm Low Limit",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": -40.0,
        "max": 60.0,
        "step": 0.1,
    },
    # Relay status.  DP115 reports the current relay state: 1 = cooling,
    # 2 = off, 3 = heating【694099120580140†L864-L889】.  Presented as a sensor with
    # string states.
    115: {
        "name": "Relay State",
        "platform": "sensor",
        "unit": None,
        "scale": 1,
        "mapping": {1: "cooling", 2: "off", 3: "heating"},
    },
    # Heating differential (also called hysteresis).  DP117
    # expresses the temperature difference that triggers heating; uses 0.1°C
    # increments【694099120580140†L944-L960】.
    117: {
        "name": "Heating Differential",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
    },
    # Cooling differential (hysteresis).  DP118 expresses the
    # temperature difference that triggers cooling【694099120580140†L944-L960】.
    118: {
        "name": "Cooling Differential",
        "platform": "number",
        "unit": "°C",
        "scale": 0.1,
        "min": 0.0,
        "max": 10.0,
        "step": 0.1,
    },
}

# Keys used in the Home Assistant data store (hass.data).
DATA_COORDINATOR = "coordinator"
DATA_DEVICE = "device"