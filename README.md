# Inkbird ITC‑308 WiFi Home Assistant Integration

This repository contains a custom Home Assistant integration (HACS
add‑on) for the Inkbird ITC‑308 WiFi temperature controller.  The
official Home Assistant Inkbird integration currently supports only
Bluetooth models, leaving WiFi models such as the ITC‑308 unhandled【937736449530754†L34-L46】.  This custom component uses the
local Tuya protocol via the [`tinytuya`](https://github.com/jasonacox/tinytuya)
library to communicate directly with the device on your LAN, so no
cloud account is required once you have extracted the device’s local
key.

## Features

* **Local control:** Communicates directly with the controller over
  your local network using Tuya’s LAN protocol; no cloud required.
* **Automatic discovery:** Provide the device ID, IP address and
  local key in the configuration UI and Home Assistant will set up
  sensors and number entities for all supported data points.
* **Entities exposed:**
  * Current temperature (`sensor.current_temperature`)
  * Target temperature (`number.target_temperature`)
  * Calibration offset (`number.calibration_offset`)
  * Compressor delay (`number.compressor_delay`)
  * Alarm high/low limits (`number.alarm_high_limit` / `number.alarm_low_limit`)
  * Heating and cooling differentials (`number.heating_differential` / `number.cooling_differential`)
  * Relay state (`sensor.relay_state`)
* **Configurable polling:** Default update interval is 30 seconds,
  configurable via the UI.

## Obtaining the local key

To control a Tuya‑based device locally you need its **device ID**,
**IP address** and **local key**.  The device ID can be found in
the Tuya/Inkbird app under device information.  To obtain the local
key you have a few options:

1. **Tuya CLI:** Install Node.js and run `npx tuya-cli wizard`, then
   follow the prompts to log into your Tuya account and extract the
   local key for each device.  Users on the Home Assistant community
   forum report this method still works【613956879721990†L114-L164】.
2. **Tuya IoT platform:** Create a free developer account at
   [iot.tuya.com](https://iot.tuya.com), link your Tuya/Inkbird app account and
   use the API Explorer to query device details.  The response
   includes the `localKey` field【613956879721990†L251-L260】.
3. **BlueStacks/Android emulator:** Some tutorials recommend using
   an Android emulator to inspect the app’s storage and extract
   keys.  This method is more complex but can be used if other
   methods fail.

Once you have the device ID, IP and local key, add the integration
through the Home Assistant UI (`Settings` → `Devices & Services` → `Add
Integration` → `Inkbird ITC‑308 WiFi`) and enter the values when
prompted.

## Data point mapping

The integration uses the data point (DP) mappings documented on the
ESPHome devices page for the ITC‑308 WiFi controller.  Key DPs include
temperature (`DP104`), target temperature (`DP106`), calibration
(`DP102`), compressor delay (`DP108`), alarm limits (`DP109`/`DP110`)
and relay status (`DP115`)【694099120580140†L864-L960】.  See
`custom_components/inkbird_itc308/const.py` for the complete mapping.

## License

This project is provided as is under the MIT license.  See
[`LICENSE`](LICENSE) for details.