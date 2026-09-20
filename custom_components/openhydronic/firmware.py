# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Calls the board's own API actions through the ESPHome integration.

The firmware exposes air purge, anti-seize and emergency stop as
``esphome.<node>_<action>``. Running them on the board keeps them alive
across a Home Assistant restart. If the board is offline or not adopted,
the caller falls back to driving the relay entities directly.
"""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.util import slugify

from .const import (
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_NODE_NAME,
    FW_ACTION_AIR_PURGE,
    FW_ACTION_ALL_ZONES_OFF,
    FW_ACTION_ANTI_SEIZE,
    FW_ACTION_EMERGENCY_STOP,
    FW_ACTION_STOP_AIR_PURGE,
    FW_ACTIONS,
    FW_NUMBER_AIR_PURGE_DURATION,
)

_LOGGER = logging.getLogger(__name__)

ESPHOME_DOMAIN = "esphome"


class FirmwareBridge:
    """Resolves and calls the OpenHydronic actions of one board."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.hass = hass
        self.entry = entry
        self._prefix: str | None = None

    # ------------------------------------------------------------------
    # Resolution
    # ------------------------------------------------------------------
    @property
    def available(self) -> bool:
        return self._async_prefix() is not None

    @callback
    def _async_prefix(self) -> str | None:
        """Service prefix of this board, e.g. ``openhydronic_a1b2c3``."""
        # Re-resolve when the cached prefix stops answering: the ESPHome entry
        # may have been reloaded or the node renamed.
        if self._prefix and self._has(self._prefix):
            return self._prefix

        self._prefix = self._async_resolve()
        return self._prefix

    @callback
    def _async_resolve(self) -> str | None:
        # Node name from discovery wins.
        for candidate in self._candidates_from_entry():
            if self._has(candidate):
                _LOGGER.debug("Firmware actions resolved as %s", candidate)
                return candidate

        # Otherwise accept a single ESPHome node exposing the actions.
        services: dict[str, Any] = self.hass.services.async_services().get(
            ESPHOME_DOMAIN, {}
        )
        suffix = f"_{FW_ACTION_AIR_PURGE}"
        found = [
            name[: -len(suffix)]
            for name in services
            if name.endswith(suffix) and self._has(name[: -len(suffix)])
        ]

        if len(found) == 1:
            _LOGGER.debug("Firmware actions resolved as %s", found[0])
            return found[0]
        if found:
            _LOGGER.debug("%s boards match, none of them this entry", len(found))
        return None

    def _candidates_from_entry(self) -> list[str]:
        """Service prefixes this entry could map to."""
        raw = [
            self.entry.data.get(CONF_NODE_NAME),
            self.entry.data.get(CONF_DEVICE_NAME),
            str(self.entry.data.get(CONF_HOST, "")).split(".")[0] or None,
        ]
        candidates: list[str] = []
        for value in raw:
            if not value:
                continue
            slug = slugify(value)
            if slug and slug not in candidates:
                candidates.append(slug)
        return candidates

    @callback
    def _has(self, prefix: str) -> bool:
        return all(
            self.hass.services.has_service(ESPHOME_DOMAIN, f"{prefix}_{action}")
            for action in FW_ACTIONS
        )

    # ------------------------------------------------------------------
    # Commands
    # ------------------------------------------------------------------
    async def _async_call(self, action: str) -> bool:
        prefix = self._async_prefix()
        if prefix is None:
            return False
        # Older firmware may not have every action.
        if not self.hass.services.has_service(ESPHOME_DOMAIN, f"{prefix}_{action}"):
            return False
        try:
            await self.hass.services.async_call(
                ESPHOME_DOMAIN, f"{prefix}_{action}", {}, blocking=True
            )
        except Exception:  # noqa: BLE001 - a dead board must not break the loop
            _LOGGER.exception("Failed to call %s.%s_%s", ESPHOME_DOMAIN, prefix, action)
            return False
        return True

    async def async_start_air_purge(self, duration: int | None = None) -> bool:
        if duration is not None:
            await self._async_set_purge_duration(duration)
        return await self._async_call(FW_ACTION_AIR_PURGE)

    async def async_stop_air_purge(self) -> bool:
        return await self._async_call(FW_ACTION_STOP_AIR_PURGE)

    async def async_run_anti_seize(self) -> bool:
        return await self._async_call(FW_ACTION_ANTI_SEIZE)

    async def async_emergency_stop(self) -> bool:
        return await self._async_call(FW_ACTION_EMERGENCY_STOP)

    async def async_all_zones_off(self) -> bool:
        return await self._async_call(FW_ACTION_ALL_ZONES_OFF)

    async def _async_set_purge_duration(self, duration: int) -> None:
        """Writes the duration into the board's ``Air Purge Duration``."""
        # Best-effort: without the number entity the board keeps its own value.
        entity_id = self._find_number(FW_NUMBER_AIR_PURGE_DURATION)
        if entity_id is None:
            _LOGGER.debug("No %s entity, board keeps its duration", FW_NUMBER_AIR_PURGE_DURATION)
            return
        try:
            await self.hass.services.async_call(
                "number",
                "set_value",
                {ATTR_ENTITY_ID: entity_id, "value": round(duration / 60, 1)},
                blocking=True,
            )
        except Exception:  # noqa: BLE001
            _LOGGER.debug("Could not set %s", entity_id, exc_info=True)

    @callback
    def _find_number(self, suffix: str) -> str | None:
        matches = [
            state.entity_id
            for state in self.hass.states.async_all("number")
            if state.entity_id.endswith(f"_{suffix}")
        ]
        if len(matches) == 1:
            return matches[0]
        for candidate in self._candidates_from_entry():
            for entity_id in matches:
                if entity_id.startswith(f"number.{candidate}"):
                    return entity_id
        return None
