# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""One coordinator per board, plus the domain services and the Lovelace card."""

from __future__ import annotations

import logging
from pathlib import Path

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import Event, HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.typing import ConfigType

from .board import async_get_board, free_channels, taken_relays
from .const import (
    ATTR_DURATION,
    ATTR_ENTRY_ID,
    CARD_FILENAME,
    CONF_DEVICE_NAME,
    CONF_HOST,
    CONF_MAC,
    CONF_NODE_NAME,
    CONF_ZONES,
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

ISSUE_ZONES_UNMAPPED = "zones_unmapped"

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
    try:
        _async_watch_unmapped(hass, entry)
    except Exception:  # noqa: BLE001 - a reminder must never stop a board from loading
        _LOGGER.debug("Could not watch the relays of %s", entry.title, exc_info=True)
    return True


@callback
def _async_check_unmapped(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Raise a repair while the board has relays and none of them is a zone.

    Only an entry with no zones at all is nagged: one that maps some relays has
    probably left the others for the pump or the spare on purpose.
    """
    from homeassistant.helpers import issue_registry as ir

    issue_id = f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}"
    free: list[int] = []
    if not entry.options.get(CONF_ZONES):
        try:
            board = async_get_board(
                hass,
                mac=entry.data.get(CONF_MAC),
                host=entry.data.get(CONF_HOST),
                node_name=entry.data.get(CONF_NODE_NAME),
            )
            if board is not None:
                free = free_channels(board, taken_relays(hass.config_entries.async_entries(DOMAIN)))
        except Exception:  # noqa: BLE001 - a hint must never stop a board from loading
            _LOGGER.debug("Could not read the relays of %s", entry.title, exc_info=True)
            return

    if not free:
        ir.async_delete_issue(hass, DOMAIN, issue_id)
        return

    ir.async_create_issue(
        hass,
        DOMAIN,
        issue_id,
        is_fixable=False,
        severity=ir.IssueSeverity.WARNING,
        translation_key=ISSUE_ZONES_UNMAPPED,
        translation_placeholders={"name": entry.title},
    )


@callback
def _async_watch_unmapped(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Check now, and again whenever ESPHome registers a new entity."""
    from homeassistant.helpers import entity_registry as er

    _async_check_unmapped(hass, entry)
    if entry.options.get(CONF_ZONES):
        return

    @callback
    def _registered(event: Event) -> None:
        if event.data.get("action") == "create":
            _async_check_unmapped(hass, entry)

    entry.async_on_unload(
        hass.bus.async_listen(er.EVENT_ENTITY_REGISTRY_UPDATED, _registered)
    )


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Drop the repair with the entry it belongs to."""
    from homeassistant.helpers import issue_registry as ir

    ir.async_delete_issue(hass, DOMAIN, f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}")


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        # Nothing watches while it is off; a reload raises it again if needed.
        from homeassistant.helpers import issue_registry as ir

        ir.async_delete_issue(hass, DOMAIN, f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}")
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
