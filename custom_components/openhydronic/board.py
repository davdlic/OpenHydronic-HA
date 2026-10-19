# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Finds the relays of an OpenHydronic board that Home Assistant already knows.

Nothing here opens a connection to the board. It reads the config entry and the
entity registry that the ESPHome integration filled when the board was added,
and uses them to pre-fill the zone form. The control loop never depends on it:
it keeps driving whatever entities the zones name, ESPHome or not.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from typing import Any

from .const import (
    CONF_AWAY_TEMP,
    CONF_COMFORT_TEMP,
    CONF_ECO_TEMP,
    CONF_IS_BYPASS,
    CONF_MASTER_ENTITY,
    CONF_RELAY_ENTITY,
    CONF_SENSOR_ENTITY,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
    DEFAULT_AWAY_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_ECO_TEMP,
)

ESPHOME_DOMAIN = "esphome"

# Entity names declared in openhydronic-8ch.yaml. The registry keeps them in
# original_name whatever the user renames afterwards, so they are the contract.
MASTER_LOCAL_MODE = "Master Local Mode"
_ZONE = re.compile(r"^Zone ([1-8])$")

# Keys the ESPHome integration stores in its config entries.
_ESPHOME_HOST = "host"
_ESPHOME_NODE = "device_name"


def normalize_mac(value: str | None) -> str | None:
    """Same result as ``device_registry.format_mac`` for the usual spellings."""
    if not value:
        return None
    raw = value.strip().lower().replace(":", "").replace("-", "").replace(".", "")
    if len(raw) != 12:
        return value.strip().lower()
    return ":".join(raw[i : i + 2] for i in range(0, 12, 2))


@dataclass(frozen=True)
class Board:
    """What the registry knows about one adopted board."""

    esphome_entry_id: str
    node_name: str | None
    mac: str | None
    zones: Mapping[int, str] = field(default_factory=dict)  # channel -> switch
    master_local_mode: str | None = None  # switch entity_id


def parse_board(
    entries: Iterable[Any],
    *,
    esphome_entry_id: str,
    node_name: str | None = None,
    mac: str | None = None,
) -> Board:
    """Map the registry entries of one ESPHome config entry to the board."""
    zones: dict[int, str] = {}
    master: str | None = None

    for entry in entries:
        if getattr(entry, "platform", ESPHOME_DOMAIN) != ESPHOME_DOMAIN:
            continue
        # A disabled entity never gets a state, so it cannot be a usable relay.
        if getattr(entry, "disabled_by", None) is not None:
            continue
        name = getattr(entry, "original_name", None)
        if not name or entry.domain != "switch":
            continue
        if (match := _ZONE.match(name)) is not None:
            zones[int(match.group(1))] = entry.entity_id
        elif name == MASTER_LOCAL_MODE:
            master = entry.entity_id

    return Board(
        esphome_entry_id=esphome_entry_id,
        node_name=node_name,
        mac=normalize_mac(mac),
        zones=dict(sorted(zones.items())),
        master_local_mode=master,
    )


def _usable(entry: Any) -> bool:
    # "ignore" is the source of an entry the user dismissed, not a real board.
    return getattr(entry, "source", None) != "ignore" and getattr(entry, "disabled_by", None) is None


def _bare(value: Any) -> str:
    return str(value or "").lower().removesuffix(".local")


def find_esphome_entry(
    hass: Any,
    *,
    mac: str | None = None,
    host: str | None = None,
    node_name: str | None = None,
) -> Any | None:
    """The ESPHome config entry of this board, or None when it is not adopted."""
    entries = hass.config_entries
    wanted = normalize_mac(mac)

    if wanted is not None:
        # ESPHome keys its entries by the formatted MAC.
        entry = entries.async_entry_for_domain_unique_id(ESPHOME_DOMAIN, wanted)
        if entry is not None and _usable(entry):
            return entry

    candidates = [entry for entry in entries.async_entries(ESPHOME_DOMAIN) if _usable(entry)]

    # A stored MAC goes stale when a board is replaced, the node name does not.
    if node_name:
        for entry in candidates:
            if entry.data.get(_ESPHOME_NODE) == node_name:
                return entry

    # A host says little: only trust it when there is no MAC to go by.
    if wanted is None and host:
        for entry in candidates:
            if _bare(entry.data.get(_ESPHOME_HOST)) == _bare(host):
                return entry

    return None


def async_get_board(
    hass: Any,
    *,
    mac: str | None = None,
    host: str | None = None,
    node_name: str | None = None,
) -> Board | None:
    """The adopted board and its relays, or None when ESPHome does not know it."""
    entry = find_esphome_entry(hass, mac=mac, host=host, node_name=node_name)
    if entry is None:
        return None

    from homeassistant.helpers import entity_registry as er  # lazy: tests fake it

    return parse_board(
        er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id),
        esphome_entry_id=entry.entry_id,
        node_name=entry.data.get(_ESPHOME_NODE),
        mac=entry.unique_id,
    )


def zone_section_key(channel: int) -> str:
    return f"zone_{channel}"


def taken_relays(entries: Iterable[Any]) -> set[str]:
    """Entities already claimed by a zone or a master of any OpenHydronic entry."""
    taken: set[str] = set()
    for entry in entries:
        options = entry.options or {}
        for zone in options.get(CONF_ZONES, []):
            if relay := zone.get(CONF_RELAY_ENTITY):
                taken.add(relay)
        if master := options.get(CONF_MASTER_ENTITY):
            taken.add(master)
    return taken


def free_channels(board: Board, taken: Iterable[str]) -> list[int]:
    """Channels whose relay no zone uses yet."""
    used = set(taken)
    return [channel for channel, relay in board.zones.items() if relay not in used]


def unfinished_sections(
    board: Board,
    form: Mapping[str, Mapping[str, Any]],
    *,
    channels: Iterable[int] | None = None,
) -> list[int]:
    """Channels where a room name was typed but no temperature sensor picked.

    Those would be dropped without a word, losing what the user typed.
    """
    allowed = set(board.zones if channels is None else channels)
    unfinished: list[int] = []
    for channel in board.zones:
        if channel not in allowed:
            continue
        block = form.get(zone_section_key(channel)) or {}
        if str(block.get(CONF_ZONE_NAME) or "").strip() and not block.get(CONF_SENSOR_ENTITY):
            unfinished.append(channel)
    return unfinished


def zones_from_form(
    board: Board,
    form: Mapping[str, Mapping[str, Any]],
    *,
    new_id: Any,
    channels: Iterable[int] | None = None,
) -> list[dict[str, Any]]:
    """Turn the multi-zone form into zone dicts.

    A zone exists only when the user picked its temperature sensor. A zone with
    no sensor is faulted by design and would switch its relay off, so a channel
    left empty costs no click and leaves no half-made thermostat.
    """
    allowed = set(board.zones if channels is None else channels)
    zones: list[dict[str, Any]] = []
    for channel, relay in board.zones.items():
        if channel not in allowed:
            continue
        block = form.get(zone_section_key(channel)) or {}
        sensor = block.get(CONF_SENSOR_ENTITY)
        if not sensor:
            continue
        name = str(block.get(CONF_ZONE_NAME) or "").strip() or f"Zone {channel}"
        zones.append(
            {
                CONF_ZONE_ID: new_id(),
                CONF_ZONE_NAME: name,
                CONF_RELAY_ENTITY: relay,
                CONF_SENSOR_ENTITY: sensor,
                CONF_COMFORT_TEMP: DEFAULT_COMFORT_TEMP,
                CONF_ECO_TEMP: DEFAULT_ECO_TEMP,
                CONF_AWAY_TEMP: DEFAULT_AWAY_TEMP,
                CONF_IS_BYPASS: False,
            }
        )
    return zones
