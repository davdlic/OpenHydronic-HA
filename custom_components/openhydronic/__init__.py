# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""One coordinator per board, plus the domain services and the Lovelace card."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .const import (
    ATTR_DURATION,
    ATTR_ENTRY_ID,
    CARD_FILENAME,
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_MAC,
    DOMAIN,
    INTEGRATION_VERSION,
    MANUFACTURER,
    MODEL,
    PLATFORMS,
    SERVICE_AIR_PURGE,
    SERVICE_ANTI_SEIZE,
    SERVICE_EMERGENCY_STOP,
    SERVICE_RESET_METRICS,
    SERVICE_STOP_AIR_PURGE,
    URL_BASE,
)
from .coordinator import OpenHydronicCoordinator

_LOGGER = logging.getLogger(__name__)

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

SERVICE_SCHEMA = vol.Schema(
    {
        vol.Optional(ATTR_ENTRY_ID): cv.string,
        vol.Optional(ATTR_DURATION): vol.All(vol.Coerce(int), vol.Range(min=60, max=7200)),
    }
)


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Register the frontend card once, regardless of how many boards exist."""
    await _async_register_frontend(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up one OpenHydronic board from a config entry."""
    coordinator = OpenHydronicCoordinator(hass, entry)
    await coordinator.async_setup()
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    _async_register_device(hass, entry)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    _async_register_services(hass)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        coordinator: OpenHydronicCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown_coordinator()
        if not hass.data[DOMAIN]:
            for service in (
                SERVICE_AIR_PURGE,
                SERVICE_STOP_AIR_PURGE,
                SERVICE_ANTI_SEIZE,
                SERVICE_RESET_METRICS,
                SERVICE_EMERGENCY_STOP,
            ):
                hass.services.async_remove(DOMAIN, service)
    return unloaded


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when the options (zones, master, timings) change."""
    await hass.config_entries.async_reload(entry.entry_id)


def _async_register_device(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Create the hub device the zone entities are attached to."""
    from homeassistant.helpers import device_registry as dr

    registry = dr.async_get(hass)
    connections = set()
    if mac := entry.data.get(CONF_MAC):
        connections.add((dr.CONNECTION_NETWORK_MAC, dr.format_mac(mac)))

    registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, entry.unique_id or entry.entry_id)},
        connections=connections,
        manufacturer=MANUFACTURER,
        model=MODEL,
        name=entry.data.get(CONF_DEVICE_NAME, entry.title),
        sw_version=INTEGRATION_VERSION,
        configuration_url=(
            f"http://{entry.data[CONF_HOST]}" if entry.data.get(CONF_HOST) else None
        ),
    )


def _async_register_services(hass: HomeAssistant) -> None:
    """Register the domain services (idempotent across multiple boards)."""
    if hass.services.has_service(DOMAIN, SERVICE_AIR_PURGE):
        return

    def _targets(call: ServiceCall) -> list[OpenHydronicCoordinator]:
        entry_id = call.data.get(ATTR_ENTRY_ID)
        coordinators: dict[str, OpenHydronicCoordinator] = hass.data.get(DOMAIN, {})
        if entry_id:
            coordinator = coordinators.get(entry_id)
            return [coordinator] if coordinator else []
        return list(coordinators.values())

    async def _air_purge(call: ServiceCall) -> None:
        for coordinator in _targets(call):
            await coordinator.async_start_air_purge(call.data.get(ATTR_DURATION))

    async def _stop_air_purge(call: ServiceCall) -> None:
        for coordinator in _targets(call):
            await coordinator.async_stop_air_purge()

    async def _anti_seize(call: ServiceCall) -> None:
        for coordinator in _targets(call):
            await coordinator.async_run_anti_seize(call.data.get(ATTR_DURATION))

    async def _reset_metrics(call: ServiceCall) -> None:
        for coordinator in _targets(call):
            await coordinator.async_reset_metrics()

    async def _emergency_stop(call: ServiceCall) -> None:
        for coordinator in _targets(call):
            await coordinator.async_emergency_stop()

    hass.services.async_register(DOMAIN, SERVICE_AIR_PURGE, _air_purge, SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_AIR_PURGE, _stop_air_purge, SERVICE_SCHEMA
    )
    hass.services.async_register(DOMAIN, SERVICE_ANTI_SEIZE, _anti_seize, SERVICE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_RESET_METRICS, _reset_metrics, SERVICE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_EMERGENCY_STOP, _emergency_stop, SERVICE_SCHEMA
    )


async def _async_register_frontend(hass: HomeAssistant) -> None:
    """Serve and auto-load openhydronic-card.js without a manual resource."""
    # Served from the component folder: no CDN, works with the internet down.
    if hass.data.get(f"{DOMAIN}_frontend_registered"):
        return
    hass.data[f"{DOMAIN}_frontend_registered"] = True

    from homeassistant.components.frontend import add_extra_js_url

    www_dir = Path(__file__).parent / "www"
    if not (www_dir / CARD_FILENAME).is_file():
        _LOGGER.warning("%s not found, card will not be served", CARD_FILENAME)
        return

    try:
        from homeassistant.components.http import StaticPathConfig

        await hass.http.async_register_static_paths(
            [StaticPathConfig(URL_BASE, str(www_dir), False)]
        )
    except ImportError:  # Home Assistant < 2024.7
        hass.http.register_static_path(URL_BASE, str(www_dir), False)

    add_extra_js_url(hass, f"{URL_BASE}/{CARD_FILENAME}?v={INTEGRATION_VERSION}")
    _LOGGER.debug("Frontend card registered at %s", URL_BASE)
