# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""The three global controls exposed on the Lovelace card."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import OpenHydronicCoordinator
from .entity import OpenHydronicEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    coordinator: OpenHydronicCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            OpenHydronicSummerSwitch(coordinator),
            OpenHydronicHolidaySwitch(coordinator),
            OpenHydronicAirPurgeSwitch(coordinator),
        ]
    )


class OpenHydronicSummerSwitch(OpenHydronicEntity, SwitchEntity):
    """Summer mode: heating disabled, anti-seize still runs."""

    _attr_name = "Summer mode"
    _attr_icon = "mdi:weather-sunny"

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "summer_mode")

    @property
    def is_on(self) -> bool:
        return bool(self._snapshot.get("summer_mode", False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_summer_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_summer_mode(False)


class OpenHydronicHolidaySwitch(OpenHydronicEntity, SwitchEntity):
    """Holiday mode: every zone clamps to its AWAY setpoint (frost guard)."""

    _attr_name = "Holiday mode"
    _attr_icon = "mdi:bag-suitcase"

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "holiday_mode")

    @property
    def is_on(self) -> bool:
        return bool(self._snapshot.get("holiday_mode", False))

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_holiday_mode(True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_set_holiday_mode(False)


class OpenHydronicAirPurgeSwitch(OpenHydronicEntity, SwitchEntity):
    """Manual air purge: all valves open + circulator, auto-off on timeout."""

    _attr_name = "Air purge"
    _attr_icon = "mdi:air-filter"

    def __init__(self, coordinator: OpenHydronicCoordinator) -> None:
        super().__init__(coordinator, "air_purge")

    @property
    def is_on(self) -> bool:
        return bool(self._snapshot.get("air_purge_active", False))

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {
            "remaining_seconds": self._snapshot.get("air_purge_remaining", 0),
            "duration": self.coordinator.air_purge_duration,
        }

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_start_air_purge()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_stop_air_purge()
