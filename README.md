# HA Victron IR BLE Integration
Home Assistant Victron Instant Readout BLE Integration

This integration is based on [victron-ble](https://github.com/keshavdv/victron-ble).

## Supported Devices

- Solar Charger (e.g. BlueSolar 75/15):
    - Charger State (Off, Bulk, Absorption, Float)
    - Battery Voltage (V)
    - Battery Charging Current (A)
    - Solar Power (W)
    - Yield Today (Wh)
    - External Device Load (A)
- SmartShunt 500A/500mv and BMV-712/702 (TODO)
- Smart Battery Sense (TODO)

## Quick Setup

Copy `custom_components/victron_ir` into your config dir or use the HACS setup described below:

This quick setup guide is based on [My Home Assistant](https://my.home-assistant.io/) links and the [Home Assistant Community Store (HACS)](https://hacs.xyz).

As this integration is currently not part of Home Assistant Core, you have to download it first into your Home Assistant installation. To download it via HACS, click the following button to open the download page for this integration in HACS.

[![Open your Home Assistant instance and open this repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=SWW13&repository=homeassistant-victron-ir-ble&category=integration)

After a restart of Home Assistant, this integration is configurable by via "Add Integration" at "Devices & Services" like any core integration. Select "Victron IR BLE" and follow the instructions.

To get there in one click, use this button:

[![Open your Home Assistant instance and start setting up this integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=victron_ir)
