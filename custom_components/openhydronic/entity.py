# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Shared base entity for OpenHydronic."""

from __future__ import annotations

from typing import Any

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_DEVICE_NAME,
    CONF_HOST,
    DOMAIN,
    INTEGRATION_VERSION,
    MANUFACTURER,
    MODEL,
)
from .coordinator import OpenHydronicCoordinator


class OpenHydronicEntity(CoordinatorEntity[OpenHydronicCoordinator]):
    """Attach every entity to the board device and keep naming consistent."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: OpenHydronicCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.entry
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
            manufacturer=MANUFACTURER,
            model=MODEL,
            name=entry.data.get(CONF_DEVICE_NAME, entry.title),
            sw_version=INTEGRATION_VERSION,
            configuration_url=(
                f"http://{entry.data[CONF_HOST]}" if entry.data.get(CONF_HOST) else None
            ),
        )

    @property
    def _snapshot(self) -> dict[str, Any]:
        return self.coordinator.data or {}
