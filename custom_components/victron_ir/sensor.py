"""Support for Victron Instant Readout BLE sensors."""
from __future__ import annotations

import logging

from homeassistant import config_entries
from homeassistant.components.bluetooth.passive_update_processor import (
    PassiveBluetoothDataProcessor,
    PassiveBluetoothDataUpdate,
    PassiveBluetoothEntityKey,
    PassiveBluetoothProcessorCoordinator,
    PassiveBluetoothProcessorEntity,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.sensor import sensor_device_info_to_hass_device_info

from sensor_state_data import (
    DeviceClass,
    DeviceKey,
    SensorDescription,
    SensorUpdate,
    Units,
)

from .const import DOMAIN, CHARGE_STATE, STATE_OF_CHARGE, TIME_REMAINING, ALARM

LOGGER = logging.getLogger(__name__)


SENSOR_DESCRIPTIONS = {
    (CHARGE_STATE, None): SensorEntityDescription(
        key=CHARGE_STATE,
        device_class=SensorDeviceClass.ENUM,
        native_unit_of_measurement=None,
        state_class=None,
    ),
    (DeviceClass.ENERGY, Units.ELECTRIC_POTENTIAL_VOLT): SensorEntityDescription(
        key=f"{DeviceClass.ENERGY}_{Units.ELECTRIC_POTENTIAL_VOLT}",
        device_class=SensorDeviceClass.ENERGY_STORAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.CURRENT, Units.ELECTRIC_CURRENT_AMPERE): SensorEntityDescription(
        key=f"{DeviceClass.CURRENT}_{Units.ELECTRIC_CURRENT_AMPERE}",
        device_class=SensorDeviceClass.CURRENT,
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.ENERGY, Units.ENERGY_WATT_HOUR): SensorEntityDescription(
        key=f"{DeviceClass.ENERGY}_{Units.ENERGY_WATT_HOUR}",
        device_class=SensorDeviceClass.ENERGY,
        native_unit_of_measurement=UnitOfEnergy.WATT_HOUR,
        state_class=SensorStateClass.TOTAL,
    ),
    (DeviceClass.POWER, Units.POWER_WATT): SensorEntityDescription(
        key=f"{DeviceClass.POWER}_{Units.POWER_WATT}",
        device_class=SensorDeviceClass.POWER,
        native_unit_of_measurement=UnitOfPower.WATT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.VOLTAGE, Units.ELECTRIC_POTENTIAL_VOLT): SensorEntityDescription(
        key=f"{DeviceClass.VOLTAGE}_{Units.ELECTRIC_POTENTIAL_VOLT}",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.BATTERY, Units.PERCENTAGE): SensorEntityDescription(
        key=STATE_OF_CHARGE,
        device_class=SensorDeviceClass.BATTERY,
        native_unit_of_measurement=Units.PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.DURATION, Units.TIME_MINUTES): SensorEntityDescription(
        key=f"{TIME_REMAINING}_{Units.TIME_MINUTES}",
        device_class=SensorDeviceClass.DURATION,
        native_unit_of_measurement=Units.TIME_MINUTES,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (DeviceClass.TEMPERATURE, Units.TEMP_KELVIN): SensorEntityDescription(
        key=f"{DeviceClass.TEMPERATURE}_{Units.TEMP_KELVIN}",
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=Units.TEMP_KELVIN,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    (ALARM, None): SensorEntityDescription(
        key=ALARM,
        device_class=SensorDeviceClass.ENUM,
        native_unit_of_measurement=None,
        state_class=None,
    )
}


def _device_key_to_bluetooth_entity_key(
    device_key: DeviceKey,
) -> PassiveBluetoothEntityKey:
    """Convert a device key to an entity key."""
    return PassiveBluetoothEntityKey(device_key.key, device_key.device_id)


def _to_sensor_key(
    description: SensorDescription,
) -> tuple[SensorDeviceClass, Units | None]:
    assert description.device_class is not None
    return (description.device_class, description.native_unit_of_measurement)


def sensor_update_to_bluetooth_data_update(
    sensor_update: SensorUpdate,
) -> PassiveBluetoothDataUpdate:
    """Convert a sensor update to a bluetooth data update."""
    return PassiveBluetoothDataUpdate(
        devices={
            device_id: sensor_device_info_to_hass_device_info(device_info)
            for device_id, device_info in sensor_update.devices.items()
        },
        entity_descriptions={
            _device_key_to_bluetooth_entity_key(device_key): SENSOR_DESCRIPTIONS[
                _to_sensor_key(description)
            ]
            for device_key, description in sensor_update.entity_descriptions.items()
            if _to_sensor_key(description) in SENSOR_DESCRIPTIONS
        },
        entity_data={
            _device_key_to_bluetooth_entity_key(device_key): sensor_values.native_value
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
        entity_names={
            _device_key_to_bluetooth_entity_key(device_key): sensor_values.name
            for device_key, sensor_values in sensor_update.entity_values.items()
        },
    )


async def async_setup_entry(
    hass: HomeAssistant,
    entry: config_entries.ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Victron Instant Readout BLE sensors."""
    coordinator: PassiveBluetoothProcessorCoordinator = hass.data[DOMAIN][
        entry.entry_id
    ]
    processor = PassiveBluetoothDataProcessor(sensor_update_to_bluetooth_data_update)
    entry.async_on_unload(
        processor.async_add_entities_listener(
            VictronInstantReadoutEntity, async_add_entities
        )
    )
    entry.async_on_unload(coordinator.async_register_processor(processor))


class VictronInstantReadoutEntity(
    PassiveBluetoothProcessorEntity[
        PassiveBluetoothDataProcessor[bool | None, SensorUpdate]
    ],
    SensorEntity,
):
    """Representation of a Victron Instant Readout BLE sensor."""

    @property
    def native_value(self) -> int | float | None:
        """Return the native value."""
        return self.processor.entity_data.get(self.entity_key)
