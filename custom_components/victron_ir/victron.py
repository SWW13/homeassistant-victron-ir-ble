from __future__ import annotations

import logging

from bluetooth_sensor_state_data import BluetoothData
from home_assistant_bluetooth import BluetoothServiceInfo
from sensor_state_data import Units, DeviceClass
from victron_ble.devices import detect_device_type
from victron_ble.devices.base import MODEL_ID_MAPPING
from victron_ble.devices.solar_charger import SolarChargerData

from .const import COMPANY_IDENTIFIER, CHARGE_STATE

LOGGER = logging.getLogger(__name__)


class VictronInstantReadoutData(BluetoothData):
    """Data for Victron Instant Readout."""

    def __init__(self, enckey) -> None:
        super().__init__()
        self._enckey = enckey

    def _start_update(self, data: BluetoothServiceInfo) -> None:
        # get BLE data
        try:
            raw_data = data.manufacturer_data[COMPANY_IDENTIFIER]
        except (KeyError, IndexError):
            LOGGER.debug(f"Manufacturer ID {COMPANY_IDENTIFIER:x} not found in data")
            return

        # detect device type
        device_type = detect_device_type(raw_data)
        if device_type is None:
            LOGGER.debug(f"Unknown device type: {raw_data}")
            return

        # get device model name
        device = device_type(self._enckey)
        model_id = device.get_model_id(raw_data)
        model_name = MODEL_ID_MAPPING.get(model_id, f"<Unknown device: {model_id}>")

        # set name, type and manufacturer
        self.set_device_name(data.name)
        self.set_device_type(model_name)
        self.set_device_manufacturer("Victron Energy")

        # decrypt sensor data
        if device.advertisement_key is None:
            LOGGER.debug(f"No enckey set")
            return

        sensor_data = device.parse(raw_data)

        # convert sensor data to hassio
        if isinstance(sensor_data, SolarChargerData) or True:
            sensor_data: SolarChargerData
            if sensor_data.get_solar_power() > 1500:
                LOGGER.debug(f"invalid sensor_data: {sensor_data._data}")
                LOGGER.debug(f"raw decrypted data: {device.decrypt(raw_data)}")
                return
            self.update_sensor(
                key=CHARGE_STATE,
                device_class=CHARGE_STATE,
                native_unit_of_measurement=None,
                native_value=sensor_data.get_charge_state(),
            )
            self.update_sensor(
                key="battery_voltage",
                device_class=DeviceClass.VOLTAGE,
                native_unit_of_measurement=Units.ELECTRIC_POTENTIAL_VOLT,
                native_value=sensor_data.get_battery_voltage(),
            )
            self.update_sensor(
                key="battery_charging_current",
                device_class=DeviceClass.CURRENT,
                native_unit_of_measurement=Units.ELECTRIC_CURRENT_AMPERE,
                native_value=sensor_data.get_battery_charging_current(),
            )
            self.update_sensor(
                key="yield_today",
                device_class=DeviceClass.ENERGY,
                native_unit_of_measurement=Units.ENERGY_WATT_HOUR,
                native_value=sensor_data.get_yield_today(),
            )
            self.update_sensor(
                key="solar_power",
                device_class=DeviceClass.POWER,
                native_unit_of_measurement=Units.POWER_WATT,
                native_value=sensor_data.get_solar_power(),
            )
            self.update_sensor(
                key="external_device_load",
                device_class=DeviceClass.CURRENT,
                native_unit_of_measurement=Units.ELECTRIC_CURRENT_AMPERE,
                native_value=sensor_data.get_external_device_load(),
            )
        # TODO: add other data classes
        else:
            LOGGER.debug(f"Unsupported data type: {device_type.data_type}")
            return
