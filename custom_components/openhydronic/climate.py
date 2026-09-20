# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""One thermostat per hydraulic zone.

Commands go to the coordinator, never to a relay, so the cycle guards cannot
be bypassed from the UI.
"""

from __future__ import annotations

from typing import Any

from homeassistant.components.climate import (
    ClimateEntity,
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.components.climate.const import (
    PRESET_AWAY,
    PRESET_COMFORT,
    PRESET_ECO,
    PRESET_NONE,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_TEMPERATURE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTR_CYCLES,
    ATTR_DEMAND,
    ATTR_FAULT,
    ATTR_IS_BYPASS,
    ATTR_LOCKED_UNTIL,
    ATTR_MASTER_STATE,
    ATTR_RELAY_ENTITY,
    ATTR_RUNTIME_HOURS,
    ATTR_SENSOR_ENTITY,
    ATTR_SYSTEM_MODE,
    ATTR_VALVE_STATE,
    DOMAIN,
    MAX_TEMP,
    MIN_TEMP,
    SYSTEM_MODE_SUMMER,
    TEMP_STEP,
    VALVE_OPEN,
    VALVE_OPENING,
)
from .coordinator import OpenHydronicCoordinator, ZoneRuntime
from .entity import OpenHydronicEntity

PRESET_MAP = {
    PRESET_COMFORT: "comfort",
    PRESET_ECO: "eco",
    PRESET_AWAY: "away",
    PRESET_NONE: "none",
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create one thermostat per configured zone."""
    coordinator: OpenHydronicCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        OpenHydronicClimate(coordinator, zone_id) for zone_id in coordinator.zones
    )


class OpenHydronicClimate(OpenHydronicEntity, ClimateEntity):
    """Thermostat bound to one relay + one temperature sensor."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_hvac_modes = [HVACMode.HEAT, HVACMode.OFF]
    _attr_preset_modes = [PRESET_COMFORT, PRESET_ECO, PRESET_AWAY, PRESET_NONE]
    _attr_supported_features = (
        ClimateEntityFeature.TARGET_TEMPERATURE
        | ClimateEntityFeature.PRESET_MODE
        | ClimateEntityFeature.TURN_ON
        | ClimateEntityFeature.TURN_OFF
    )
    _attr_min_temp = MIN_TEMP
    _attr_max_temp = MAX_TEMP
    _attr_target_temperature_step = TEMP_STEP
    _enable_turn_on_off_backwards_compatibility = False

    def __init__(self, coordinator: OpenHydronicCoordinator, zone_id: str) -> None:
        super().__init__(coordinator, f"zone_{zone_id}")
        self._zone_id = zone_id
        self._attr_name = coordinator.zones[zone_id].name

    # -- state ---------------------------------------------------------
    @property
    def _zone(self) -> ZoneRuntime | None:
        return self.coordinator.zones.get(self._zone_id)

    @property
    def _zone_data(self) -> dict[str, Any]:
        return self._snapshot.get("zones", {}).get(self._zone_id, {})

    @property
    def available(self) -> bool:
        return super().available and self._zone is not None

    @property
    def current_temperature(self) -> float | None:
        return self._zone_data.get("current_temp")

    @property
    def target_temperature(self) -> float | None:
        return self._zone_data.get("target_temp")

    @property
    def hvac_mode(self) -> HVACMode:
        if self._zone_data.get("hvac_mode") == HVACMode.OFF:
            return HVACMode.OFF
        return HVACMode.HEAT

    @property
    def hvac_action(self) -> HVACAction:
        if self.hvac_mode == HVACMode.OFF:
            return HVACAction.OFF
        if self._snapshot.get(ATTR_SYSTEM_MODE) == SYSTEM_MODE_SUMMER:
            return HVACAction.OFF
        if self._zone_data.get(ATTR_VALVE_STATE) in (VALVE_OPEN, VALVE_OPENING):
            return HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str:
        return self._zone_data.get("preset", PRESET_NONE)

    @property
    def icon(self) -> str:
        if self._zone_data.get(ATTR_IS_BYPASS):
            return "mdi:pipe-valve"
        return "mdi:radiator" if self.hvac_action == HVACAction.HEATING else "mdi:radiator-disabled"

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Everything the Lovelace card needs, in one read."""
        data = self._zone_data
        return {
            ATTR_VALVE_STATE: data.get(ATTR_VALVE_STATE),
            ATTR_RELAY_ENTITY: data.get(ATTR_RELAY_ENTITY),
            ATTR_SENSOR_ENTITY: data.get(ATTR_SENSOR_ENTITY),
            ATTR_IS_BYPASS: data.get(ATTR_IS_BYPASS),
            ATTR_DEMAND: data.get(ATTR_DEMAND),
            ATTR_FAULT: data.get(ATTR_FAULT),
            ATTR_LOCKED_UNTIL: data.get(ATTR_LOCKED_UNTIL),
            ATTR_RUNTIME_HOURS: data.get(ATTR_RUNTIME_HOURS),
            ATTR_CYCLES: data.get(ATTR_CYCLES),
            ATTR_SYSTEM_MODE: self._snapshot.get(ATTR_SYSTEM_MODE),
            ATTR_MASTER_STATE: self._snapshot.get(ATTR_MASTER_STATE),
            "zone_id": self._zone_id,
        }

    # -- commands ------------------------------------------------------
    async def async_set_temperature(self, **kwargs: Any) -> None:
        if (temperature := kwargs.get(ATTR_TEMPERATURE)) is None:
            return
        await self.coordinator.async_set_zone_temperature(self._zone_id, temperature)

    async def async_set_hvac_mode(self, hvac_mode: HVACMode) -> None:
        await self.coordinator.async_set_zone_hvac_mode(self._zone_id, hvac_mode.value)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        await self.coordinator.async_set_zone_preset(
            self._zone_id, PRESET_MAP.get(preset_mode, PRESET_NONE)
        )

    async def async_turn_on(self) -> None:
        await self.async_set_hvac_mode(HVACMode.HEAT)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)
