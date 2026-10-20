# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Unit tests for the board lookup that pre-fills the zone form.

Nothing here needs Home Assistant: the registries are small fakes.
"""

from __future__ import annotations

import itertools
import types

from custom_components.openhydronic import const
from custom_components.openhydronic.board import (
    Board,
    find_esphome_entry,
    free_channels,
    normalize_mac,
    parse_board,
    taken_relays,
    unfinished_sections,
    zone_section_key,
    zones_from_form,
)

MAC = "10:06:1c:f5:f8:1c"
NODE = "openhydronic-f5f81c"


def row(name, *, domain="switch", entity_id=None, platform="esphome", disabled_by=None):
    return types.SimpleNamespace(
        domain=domain,
        platform=platform,
        original_name=name,
        disabled_by=disabled_by,
        entity_id=entity_id or f"{domain}.{name.lower().replace(' ', '_')}",
    )


def esphome_entry(entry_id="e1", unique_id=MAC, **data):
    data = {"host": "192.168.1.40", "device_name": NODE, **data}
    return types.SimpleNamespace(
        entry_id=entry_id, unique_id=unique_id, data=data, source="zeroconf", disabled_by=None
    )


class FakeConfigEntries:
    def __init__(self, entries):
        self._entries = entries

    def async_entry_for_domain_unique_id(self, domain, unique_id):
        return next(
            (e for e in self._entries if e.unique_id == unique_id and domain == "esphome"), None
        )

    def async_entries(self, domain=None):
        return list(self._entries) if domain == "esphome" else []


def fake_hass(*entries):
    return types.SimpleNamespace(config_entries=FakeConfigEntries(list(entries)))


# ---------------------------------------------------------------------------
# MAC handling
# ---------------------------------------------------------------------------
def test_mac_spellings_all_become_the_esphome_form():
    for spelling in ("10061cf5f81c", "10:06:1C:F5:F8:1C", "10-06-1c-f5-f8-1c", "1006.1cf5.f81c"):
        assert normalize_mac(spelling) == MAC


def test_mac_missing_or_odd_is_left_alone():
    assert normalize_mac(None) is None
    assert normalize_mac("") is None
    assert normalize_mac("Not-A-Mac") == "not-a-mac"


# ---------------------------------------------------------------------------
# Reading the registry rows
# ---------------------------------------------------------------------------
def test_zones_are_found_by_the_name_the_firmware_gave_them():
    rows = [row(f"Zone {n}") for n in (1, 2, 3)]
    board = parse_board(rows, esphome_entry_id="e1", node_name=NODE, mac=MAC)

    assert board.zones == {1: "switch.zone_1", 2: "switch.zone_2", 3: "switch.zone_3"}
    assert board.mac == MAC and board.node_name == NODE


def test_a_renamed_entity_id_still_maps_to_its_channel():
    # The user renames the entity, original_name stays what the firmware said.
    board = parse_board(
        [row("Zone 2", entity_id="switch.living_room_floor")], esphome_entry_id="e1"
    )

    assert board.zones == {2: "switch.living_room_floor"}


def test_only_switches_named_zone_n_count():
    rows = [
        row("Zone 1"),
        row("Zone 1 Lock", domain="sensor"),  # a countdown, not a relay
        row("Zone 1", domain="sensor"),  # same name, wrong domain
        row("Zone 9"),  # a board has eight channels
        row("Zone 0"),
        row("Air Purge (start)", domain="button"),
        row("Summer Mode"),
    ]
    board = parse_board(rows, esphome_entry_id="e1")

    assert board.zones == {1: "switch.zone_1"}


def test_disabled_or_foreign_rows_are_skipped():
    rows = [
        row("Zone 1", disabled_by="user"),
        row("Zone 2", platform="tasmota"),
        row("Zone 3"),
    ]

    assert parse_board(rows, esphome_entry_id="e1").zones == {3: "switch.zone_3"}


def test_the_boards_own_master_switch_is_found_by_name():
    rows = [row("Zone 1"), row("Master Local Mode", entity_id="switch.master_local_mode")]

    assert parse_board(rows, esphome_entry_id="e1").master_local_mode == "switch.master_local_mode"


def test_the_password_entities_are_found_by_name():
    rows = [
        row("Zone 1"),
        row("Board Password", domain="text", entity_id="text.my_password"),
        row("Default Password", domain="binary_sensor", entity_id="binary_sensor.exposed"),
    ]

    board = parse_board(rows, esphome_entry_id="e1")

    assert board.password_text == "text.my_password"
    assert board.default_password == "binary_sensor.exposed"


def test_older_firmware_has_no_password_entities():
    board = parse_board([row("Zone 1")], esphome_entry_id="e1")

    assert board.password_text is None and board.default_password is None


def test_an_entity_of_another_kind_with_the_password_name_is_not_one():
    rows = [
        row("Board Password", domain="switch"),
        row("Board Password", domain="sensor"),
        row("Default Password", domain="switch"),
        row("Default Password", domain="sensor"),
        row("Default Password", domain="text"),
    ]

    board = parse_board(rows, esphome_entry_id="e1")

    assert board.password_text is None and board.default_password is None


def test_a_board_without_the_master_switch_reports_none():
    assert parse_board([row("Zone 1")], esphome_entry_id="e1").master_local_mode is None


# ---------------------------------------------------------------------------
# Finding the ESPHome entry
# ---------------------------------------------------------------------------
def test_the_entry_is_found_by_mac():
    entry = esphome_entry()

    assert find_esphome_entry(fake_hass(entry), mac="10061cf5f81c") is entry


def test_not_adopted_is_none():
    assert find_esphome_entry(fake_hass(), mac=MAC, host="192.168.1.40", node_name=NODE) is None


def test_a_stale_mac_falls_back_to_the_node_name():
    # Board replaced: ESPHome's entry carries the new MAC, the node name is kept.
    entry = esphome_entry(unique_id="aa:bb:cc:dd:ee:ff")

    assert find_esphome_entry(fake_hass(entry), mac=MAC, node_name=NODE) is entry


def test_another_boards_node_name_is_not_borrowed():
    entry = esphome_entry(unique_id="aa:bb:cc:dd:ee:ff", device_name="openhydronic-other")

    assert find_esphome_entry(fake_hass(entry), mac=MAC, node_name=NODE) is None


def test_the_host_is_only_trusted_without_a_mac():
    entry = esphome_entry(unique_id="aa:bb:cc:dd:ee:ff", device_name="something-else")

    assert find_esphome_entry(fake_hass(entry), host="192.168.1.40") is entry
    assert find_esphome_entry(fake_hass(entry), mac=MAC, host="192.168.1.40") is None


def test_a_dismissed_or_disabled_entry_is_not_a_board():
    ignored = esphome_entry()
    ignored.source = "ignore"
    disabled = esphome_entry(entry_id="e2", unique_id="aa:bb:cc:dd:ee:ff")
    disabled.disabled_by = "user"

    assert find_esphome_entry(fake_hass(ignored), mac=MAC) is None
    assert find_esphome_entry(fake_hass(disabled), mac="aabbccddeeff") is None


# ---------------------------------------------------------------------------
# What is already taken
# ---------------------------------------------------------------------------
def entry_with(zones=(), master=None):
    options = {
        const.CONF_ZONES: [{const.CONF_RELAY_ENTITY: relay} for relay in zones],
        const.CONF_MASTER_ENTITY: master,
    }
    return types.SimpleNamespace(options=options)


def test_taken_relays_cover_every_entry_and_the_master():
    taken = taken_relays([entry_with(["switch.a", "switch.b"]), entry_with([], "switch.pump")])

    assert taken == {"switch.a", "switch.b", "switch.pump"}


def test_free_channels_skip_the_relays_in_use():
    board = Board("e1", NODE, MAC, zones={1: "switch.a", 2: "switch.b", 3: "switch.c"})

    assert free_channels(board, ["switch.b"]) == [1, 3]
    assert free_channels(board, []) == [1, 2, 3]


# ---------------------------------------------------------------------------
# The form
# ---------------------------------------------------------------------------
BOARD = Board("e1", NODE, MAC, zones={1: "switch.z1", 2: "switch.z2", 3: "switch.z3"})


def ids():
    counter = itertools.count(1)
    return lambda: f"id{next(counter)}"


def test_a_zone_exists_only_where_a_sensor_was_picked():
    form = {
        zone_section_key(1): {"name": "Living room", "sensor_entity": "sensor.living"},
        zone_section_key(2): {"name": "Left alone"},
        zone_section_key(3): {},
    }

    zones = zones_from_form(BOARD, form, new_id=ids())

    assert [z[const.CONF_ZONE_NAME] for z in zones] == ["Living room"]
    assert zones[0][const.CONF_RELAY_ENTITY] == "switch.z1"
    assert zones[0][const.CONF_SENSOR_ENTITY] == "sensor.living"
    assert zones[0][const.CONF_IS_BYPASS] is False


def test_an_empty_name_falls_back_to_the_channel():
    form = {zone_section_key(2): {"name": "  ", "sensor_entity": "sensor.s"}}

    assert zones_from_form(BOARD, form, new_id=ids())[0][const.CONF_ZONE_NAME] == "Zone 2"


def test_new_zones_take_the_usual_setpoints_and_distinct_ids():
    form = {
        zone_section_key(1): {"sensor_entity": "sensor.a"},
        zone_section_key(2): {"sensor_entity": "sensor.b"},
    }

    zones = zones_from_form(BOARD, form, new_id=ids())

    assert [z[const.CONF_ZONE_ID] for z in zones] == ["id1", "id2"]
    assert zones[0][const.CONF_COMFORT_TEMP] == const.DEFAULT_COMFORT_TEMP
    assert zones[0][const.CONF_ECO_TEMP] == const.DEFAULT_ECO_TEMP
    assert zones[0][const.CONF_AWAY_TEMP] == const.DEFAULT_AWAY_TEMP


def test_the_import_form_only_touches_the_channels_it_offered():
    form = {
        zone_section_key(1): {"sensor_entity": "sensor.a"},
        zone_section_key(2): {"sensor_entity": "sensor.b"},
    }

    zones = zones_from_form(BOARD, form, new_id=ids(), channels=[2])

    assert [z[const.CONF_RELAY_ENTITY] for z in zones] == ["switch.z2"]


def test_a_typed_name_without_a_sensor_is_flagged_not_dropped():
    form = {
        zone_section_key(1): {"name": "Living room"},
        zone_section_key(2): {"name": "Kitchen", "sensor_entity": "sensor.k"},
        zone_section_key(3): {"name": "  "},
    }

    assert unfinished_sections(BOARD, form) == [1]


def test_unfinished_sections_only_look_at_the_channels_offered():
    form = {zone_section_key(1): {"name": "Living room"}}

    assert unfinished_sections(BOARD, form, channels=[2, 3]) == []
