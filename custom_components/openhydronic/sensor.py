# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Telemetry per actuator plus system diagnostics."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CYCLES,
    ATTR_RUNTIME_HOURS,
    DOMAIN,
    MASTER_STATE_DISABLED,
    MASTER_STATE_OFF,
    MASTER_STATE_ON,
    MASTER_STATE_PURGING,
    MASTER_STATE_WAITING,
    SYSTEM_MODE_AIR_PURGE,
    SYSTEM_MODE_ANTI_SEIZE,
    SYSTEM_MODE_HOLIDAY,
    SYSTEM_MODE_NORMAL,
    SYSTEM_MODE_SUMMER,
)
from .coordinator import OpenHydronicCoordinator
from .entity import OpenHydronicEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create per-zone metrics and the system diagnostics sensors."""
    coordinator: OpenHydronicCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = [
        OpenHydronicMasterStateSensor(coordinator),
        OpenHydronicSystemModeSensor(coordinator),
        OpenHydronicActiveZonesSensor(coordinator),
    ]
    for zone_id, zone in coordinator.zones.items():
        entities.append(OpenHydronicRuntimeSensor(coordinator, zone_id, zone.name))
        entities.append(OpenHydronicCyclesSensor(coordinator, zone_id, zone.name))

    async_add_entities(entities)


class _ZoneSensor(OpenHydronicEntity, SensorEntity):
    """Base for per-zone telemetry."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(
        self,
        coordinator: OpenHydronicCoordinator,
        zone_id: str,
        zone_name: str,
        key: str,
    ) -> None:
        super().__init__(coordinator, f"zone_{zone_id}_{key}")
        self._zone_id = zone_id
        self._zone_name = zone_name

    @property
    def _zone_data(self) -> dict[str, Any]:
        return self._snapshot.get("zones", {}).get(self._zone_id, {})

    @property
    def available(self) -> bool:
        return super().available and self._zone_id in self.coordinator.zones


class OpenHydronicRuntimeSensor(_ZoneSensor):
    """Cumulative hours the actuator has been energised."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_native_unit_of_measurement = UnitOfTime.HOURS
    _attr_suggested_display_precision = 1
    _attr_icon = "mdi:timer-outline"

    def __init__(
        self, coordinator: OpenHydronicCoordinator, zone_id: str, zone_name: str
    ) -> None:
        super().__init__(coordinator, zone_id, zone_name, "runtime")
        self._attr_name = f"{zone_name} runtime"

    @property
    def native_value(self) -> float | None:
        return self._zone_data.get(ATTR_RUNTIME_HOURS)


class OpenHydronicCyclesSensor(_ZoneSensor):
    """Number of OFF -> ON transitions, i.e. wear on the PTC head."""

    _attr_icon = "mdi:counter"

    def __init__(
        self, coordinator: OpenHydronicCoordinator, zone_id: str, zone_name: str
    ) -> None:
        super().__init__(coordinator, zone_id, zone_name, "cycles")
        self._attr_name = f"{zone_name} cycles"

    @property
    def native_value(self) -> int | None:
        return self._zone_data.get(ATTR_CYCLES)


class OpenHydronicMasterStateSensor(OpenHydronicEntity, SensorEntity):
    """State machine of the circulator / boiler contact."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "master_state"
    _attr_name = "Master state"
    _attr_icon = "mdi:pump"
    _attr_options = [
        MASTER_STATE_DISABLED,
        MASTER_STATE_OFF,
        MASTER_STATE_WAITING,
        MASTER_STATE_ON,
        MASTER_STATE_PURGING,
    ]

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "master_state")

    @property
    def native_value(self) -> str:
        return self._snapshot.get("master_state", MASTER_STATE_DISABLED)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "master_entity": self._snapshot.get("master_entity"),
            "master_mode": self.coordinator.master_mode,
            "start_delay": self.coordinator.master_start_delay,
            "purge_delay": self.coordinator.heat_purge_delay,
        }


class OpenHydronicSystemModeSensor(OpenHydronicEntity, SensorEntity):
    """Normal / summer / holiday / air purge / anti-seize."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_translation_key = "system_mode"
    _attr_name = "System mode"
    _attr_icon = "mdi:home-thermometer"
    _attr_options = [
        SYSTEM_MODE_NORMAL,
        SYSTEM_MODE_SUMMER,
        SYSTEM_MODE_HOLIDAY,
        SYSTEM_MODE_AIR_PURGE,
        SYSTEM_MODE_ANTI_SEIZE,
    ]

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "system_mode")

    @property
    def native_value(self) -> str:
        return self._snapshot.get("system_mode", SYSTEM_MODE_NORMAL)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "air_purge_remaining": self._snapshot.get("air_purge_remaining", 0),
        }


class OpenHydronicActiveZonesSensor(OpenHydronicEntity, SensorEntity):
    """How many valves are actually energised right now."""

    _attr_name = "Active zones"
    _attr_icon = "mdi:valve-open"
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "active_zones")

    @property
    def native_value(self) -> int:
        return self._snapshot.get("active_zones", 0)
