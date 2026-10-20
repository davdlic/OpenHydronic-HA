# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""The config and options flows, run against a real Home Assistant.

These need pytest-homeassistant-custom-component (see CONTRIBUTING.md)
and are skipped without it, so the plain test run stays dependency free.
"""

from __future__ import annotations

import time
from ipaddress import ip_address
from unittest.mock import patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant import config_entries, data_entry_flow
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers import issue_registry as ir
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

try:  # Home Assistant >= 2025.1
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:  # the 2024.10 floor
    from homeassistant.components.zeroconf import ZeroconfServiceInfo

try:  # Home Assistant >= 2026.9 serialises its forms with probatio
    from probatio import to_field_list
except ImportError:
    import voluptuous_serialize

    def to_field_list(schema, custom_serializer=None):
        return voluptuous_serialize.convert(schema, custom_serializer=custom_serializer)

from custom_components.openhydronic import (
    ISSUE_ZONES_UNMAPPED,
    _async_check_unmapped,
    _async_watch_board,
    async_remove_entry,
)
from custom_components.openhydronic import config_flow as flow_module
from custom_components.openhydronic.const import (
    CONF_HOST,
    CONF_MAC,
    CONF_MASTER_CHOICE,
    CONF_MASTER_ENTITY,
    CONF_MASTER_MODE,
    CONF_NODE_NAME,
    CONF_RELAY_ENTITY,
    CONF_SENSOR_ENTITY,
    CONF_ZONES,
    DOMAIN,
    MASTER_DISABLED,
    MASTER_EXTERNAL,
    MASTER_RELAY,
)

MAC = "10:06:1c:f5:f8:1c"
NODE = "openhydronic-f5f81c"
HOST = "192.168.1.40"


@pytest.fixture(autouse=True)
def _integration(enable_custom_integrations, hass):
    """Load our integration, and skip the dependencies it only needs at run time."""
    hass.config.components.update({"http", "frontend", "persistent_notification"})
    with (
        patch("custom_components.openhydronic.async_setup", return_value=True),
        patch("custom_components.openhydronic.async_setup_entry", return_value=True),
    ):
        yield


def discovery(mac="10061cf5f81c", name=NODE, host=HOST):
    return ZeroconfServiceInfo(
        ip_address=ip_address(host),
        ip_addresses=[ip_address(host)],
        port=6053,
        hostname=f"{name}.local.",
        type="_esphomelib._tcp.local.",
        name=f"{name}._esphomelib._tcp.local.",
        properties={"mac": mac, "friendly_name": "OpenHydronic", "version": "2026.9.1"},
    )


def adopt(
    hass, zones=(1, 2, 3, 4, 5, 6, 7, 8), master=True, mac=MAC, node=NODE, host=HOST,
    master_state="off", password=True, default_password="on",
):
    """What the ESPHome integration leaves behind once it has adopted the board."""
    entry = MockConfigEntry(
        domain="esphome",
        unique_id=mac,
        title="OpenHydronic f5f81c",
        data={"host": host, "device_name": node, "port": 6053},
    )
    entry.add_to_hass(hass)
    registry = er.async_get(hass)
    for n in zones:
        registry.async_get_or_create(
            "switch", "esphome", f"{mac}-switch-{n}", config_entry=entry,
            original_name=f"Zone {n}", suggested_object_id=f"openhydronic_zone_{n}",
        )
    if master:
        row = registry.async_get_or_create(
            "switch", "esphome", f"{mac}-switch-master", config_entry=entry,
            original_name="Master Local Mode", suggested_object_id="openhydronic_master_local_mode",
        )
        # A registry row has no state of its own; the board reports one when connected.
        if master_state is not None:
            hass.states.async_set(row.entity_id, master_state)
    if password:
        text = registry.async_get_or_create(
            "text", "esphome", f"{mac}-text-password", config_entry=entry,
            original_name="Board Password", suggested_object_id="openhydronic_board_password",
        )
        flag = registry.async_get_or_create(
            "binary_sensor", "esphome", f"{mac}-binary_sensor-default-password", config_entry=entry,
            original_name="Default Password", suggested_object_id="openhydronic_default_password",
        )
        # The board never publishes the password, so its state is "unknown".
        hass.states.async_set(text.entity_id, "unknown")
        if default_password is not None:
            hass.states.async_set(flag.entity_id, default_password)
    return entry


async def discover(hass):
    return await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=discovery()
    )


async def confirm(hass, result):
    return await hass.config_entries.flow.async_configure(result["flow_id"], {})


def fields(result):
    """The form's field names, sections expanded, as the frontend would see them."""
    schema = to_field_list(result["data_schema"], custom_serializer=cv.custom_serializer)
    names = {}
    for item in schema:
        names[item["name"]] = item
    return names


def master_choices(result):
    """The values the master question offers, in order."""
    options = fields(result)[CONF_MASTER_CHOICE]["selector"]["select"]["options"]
    return [o if isinstance(o, str) else o["value"] for o in options]


# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
async def test_discovery_only_asks_to_confirm(hass):
    result = await discover(hass)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "discovery_confirm"


async def test_the_board_is_looked_up_when_the_user_confirms_not_before(hass):
    # The OpenHydronic card appeared first; ESPHome was added afterwards. The
    # confirm step must see that, without anyone reopening the card.
    result = await discover(hass)
    adopt(hass)

    result = await confirm(hass, result)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "zones"


async def test_zones_form_has_a_section_per_relay_and_the_master_question(hass):
    adopt(hass, zones=(1, 2, 3))
    result = await confirm(hass, await discover(hass))

    names = fields(result)

    assert {"zone_1", "zone_2", "zone_3", CONF_MASTER_CHOICE, CONF_MASTER_ENTITY} <= set(names)
    assert "zone_4" not in names
    assert names[CONF_MASTER_CHOICE]["default"] == "none"


async def test_the_board_master_is_only_offered_when_the_board_has_one(hass):
    adopt(hass, zones=(1,), master=False)
    result = await confirm(hass, await discover(hass))

    assert master_choices(result) == ["none", "entity"]


async def test_the_board_master_is_offered_when_it_exists(hass):
    adopt(hass, zones=(1,), master=True)
    result = await confirm(hass, await discover(hass))

    assert master_choices(result) == ["none", "board", "entity"]


# ---------------------------------------------------------------------------
# Creating the entry
# ---------------------------------------------------------------------------
async def test_a_sensor_makes_a_zone_and_the_rest_are_left_out(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "zone_1": {"name": "Living room", "sensor_entity": "sensor.living"},
            "zone_2": {"sensor_entity": "sensor.bedroom"},
            CONF_MASTER_CHOICE: "none",
        },
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    zones = result["options"][CONF_ZONES]
    assert [(z["name"], z[CONF_RELAY_ENTITY], z[CONF_SENSOR_ENTITY]) for z in zones] == [
        ("Living room", "switch.openhydronic_zone_1", "sensor.living"),
        ("Zone 2", "switch.openhydronic_zone_2", "sensor.bedroom"),
    ]
    assert result["options"][CONF_MASTER_MODE] == MASTER_DISABLED
    assert result["data"][CONF_MAC] == "10061cf5f81c"
    assert result["data"][CONF_NODE_NAME] == NODE


async def test_submitting_with_no_sensor_adds_the_board_without_zones(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MASTER_CHOICE: "none"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_ZONES] == []


async def test_a_relay_another_board_uses_is_refused(hass):
    adopt(hass)
    MockConfigEntry(
        domain=DOMAIN, unique_id="other", data={CONF_HOST: "10.0.0.9"},
        options={CONF_ZONES: [{CONF_RELAY_ENTITY: "switch.openhydronic_zone_1"}]},
    ).add_to_hass(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"zone_1": {"sensor_entity": "sensor.living"}, CONF_MASTER_CHOICE: "none"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "relay_in_use"}


# ---------------------------------------------------------------------------
# What drives the boiler
# ---------------------------------------------------------------------------
async def test_another_switch_becomes_the_external_master(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "zone_1": {"sensor_entity": "sensor.living"},
            CONF_MASTER_CHOICE: "entity",
            CONF_MASTER_ENTITY: "switch.boiler_shelly",
        },
    )

    assert result["options"][CONF_MASTER_MODE] == MASTER_EXTERNAL
    assert result["options"][CONF_MASTER_ENTITY] == "switch.boiler_shelly"


async def test_a_free_relay_of_the_same_board_becomes_the_relay_master(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "zone_1": {"sensor_entity": "sensor.living"},
            CONF_MASTER_CHOICE: "entity",
            CONF_MASTER_ENTITY: "switch.openhydronic_zone_8",
        },
    )

    assert result["options"][CONF_MASTER_MODE] == MASTER_RELAY
    assert result["options"][CONF_MASTER_ENTITY] == "switch.openhydronic_zone_8"


async def test_choosing_an_entity_without_picking_one_is_an_error(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MASTER_CHOICE: "entity"}
    )

    assert result["errors"] == {"base": "master_entity_required"}


async def test_the_master_cannot_be_a_relay_just_made_a_zone(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "zone_1": {"sensor_entity": "sensor.living"},
            CONF_MASTER_CHOICE: "entity",
            CONF_MASTER_ENTITY: "switch.openhydronic_zone_1",
        },
    )

    assert result["errors"] == {"base": "master_is_zone"}


async def test_the_board_master_is_switched_on_when_chosen(hass):
    adopt(hass)
    calls = async_mock_service(hass, "switch", "turn_on")
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"zone_1": {"sensor_entity": "sensor.living"}, CONF_MASTER_CHOICE: "board"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert [c.data["entity_id"] for c in calls] == ["switch.openhydronic_master_local_mode"]
    # The board runs its own master, so Home Assistant keeps none.
    assert result["options"][CONF_MASTER_MODE] == MASTER_DISABLED


async def test_the_board_master_cannot_be_chosen_when_the_board_has_none(hass):
    adopt(hass, master=False)
    result = await confirm(hass, await discover(hass))

    with pytest.raises(data_entry_flow.InvalidData):
        await hass.config_entries.flow.async_configure(
            result["flow_id"], {CONF_MASTER_CHOICE: "board"}
        )


# ---------------------------------------------------------------------------
# The board is not ready
# ---------------------------------------------------------------------------
async def test_a_board_not_in_esphome_gets_a_way_forward(hass):
    result = await confirm(hass, await discover(hass))

    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "not_adopted"
    assert result["menu_options"] == ["retry", "skip"]


async def test_check_again_finds_the_board_once_it_is_adopted(hass):
    result = await confirm(hass, await discover(hass))
    adopt(hass)

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "retry"}
    )

    assert result["step_id"] == "zones"


async def test_skip_adds_the_board_with_no_zones(hass):
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"next_step_id": "skip"}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_ZONES] == []


async def test_a_board_whose_relays_have_not_appeared_is_waited_for(hass):
    adopt(hass, zones=(), master=False)
    with patch.object(flow_module, "WAIT_POLLS", 1):
        result = await confirm(hass, await discover(hass))
        assert result["type"] is FlowResultType.SHOW_PROGRESS
        assert result["progress_action"] == "wait_board"

        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"])
        while result["type"] in (FlowResultType.SHOW_PROGRESS, FlowResultType.SHOW_PROGRESS_DONE):
            await hass.async_block_till_done()
            result = await hass.config_entries.flow.async_configure(result["flow_id"])

    assert result["type"] is FlowResultType.MENU
    assert result["step_id"] == "no_zones"


async def test_the_wait_ends_as_soon_as_the_relays_show_up(hass):
    entry = adopt(hass, zones=(), master=False)
    started = time.monotonic()
    result = await confirm(hass, await discover(hass))
    assert result["type"] is FlowResultType.SHOW_PROGRESS

    er.async_get(hass).async_get_or_create(
        "switch", "esphome", f"{MAC}-switch-1", config_entry=entry,
        original_name="Zone 1", suggested_object_id="openhydronic_zone_1",
    )
    await hass.async_block_till_done()
    result = await hass.config_entries.flow.async_configure(result["flow_id"])
    while result["type"] in (FlowResultType.SHOW_PROGRESS, FlowResultType.SHOW_PROGRESS_DONE):
        await hass.async_block_till_done()
        result = await hass.config_entries.flow.async_configure(result["flow_id"])

    assert result["step_id"] == "zones"
    assert time.monotonic() - started < 10  # the full wait is 30 s


# ---------------------------------------------------------------------------
# Typed by hand
# ---------------------------------------------------------------------------
async def test_a_host_of_an_adopted_board_goes_to_the_zones_form(hass):
    adopt(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST, "port": 6053}
    )

    assert result["step_id"] == "zones"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"zone_1": {"sensor_entity": "sensor.living"}, CONF_MASTER_CHOICE: "none"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["data"][CONF_MAC] == "10061cf5f81c"
    assert hass.config_entries.async_entries(DOMAIN)[0].unique_id == "10061cf5f81c"


async def test_a_host_unknown_to_esphome_is_added_as_before(hass):
    # A Shelly or a Zigbee relay: nothing to pre-fill, nothing to wait for.
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "10.0.0.50", "port": 6053}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_ZONES] == []


# ---------------------------------------------------------------------------
# Options: map the relays that are still free
# ---------------------------------------------------------------------------
def our_entry(hass, zones=()):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="10061cf5f81c",
        title="OpenHydronic",
        data={CONF_HOST: HOST, CONF_MAC: "10061cf5f81c", CONF_NODE_NAME: NODE},
        options={
            CONF_ZONES: [{"zone_id": f"z{i}", "name": f"Z{i}", CONF_RELAY_ENTITY: relay} for i, relay in enumerate(zones)],
            CONF_MASTER_MODE: MASTER_DISABLED,
        },
    )
    entry.add_to_hass(hass)
    return entry


async def test_the_options_menu_offers_the_free_relays_first(hass):
    adopt(hass, zones=(1, 2))
    entry = our_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["type"] is FlowResultType.MENU
    assert result["menu_options"][0] == "import_zones"


async def test_the_options_menu_does_not_offer_it_without_a_board(hass):
    entry = our_entry(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert "import_zones" not in result["menu_options"]


async def test_the_options_menu_does_not_offer_it_when_every_relay_is_used(hass):
    adopt(hass, zones=(1, 2))
    entry = our_entry(hass, zones=("switch.openhydronic_zone_1", "switch.openhydronic_zone_2"))

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert "import_zones" not in result["menu_options"]


async def test_importing_adds_zones_for_the_free_relays_only(hass):
    adopt(hass, zones=(1, 2, 3))
    entry = our_entry(hass, zones=("switch.openhydronic_zone_1",))
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "import_zones"}
    )

    assert set(fields(result)) == {"zone_2", "zone_3"}

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"zone_3": {"name": "Study", "sensor_entity": "sensor.study"}}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    relays = [z[CONF_RELAY_ENTITY] for z in result["data"][CONF_ZONES]]
    assert relays == ["switch.openhydronic_zone_1", "switch.openhydronic_zone_3"]


async def test_importing_with_no_sensor_asks_for_one(hass):
    adopt(hass, zones=(1,))
    entry = our_entry(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "import_zones"}
    )

    result = await hass.config_entries.options.async_configure(result["flow_id"], {})

    assert result["errors"] == {"base": "no_zone_selected"}


# ---------------------------------------------------------------------------
# The reminder
# ---------------------------------------------------------------------------
def issue_of(hass, entry):
    return ir.async_get(hass).async_get_issue(DOMAIN, f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}")


async def test_a_board_with_relays_and_no_zones_raises_a_reminder(hass):
    adopt(hass, zones=(1, 2))
    entry = our_entry(hass)

    _async_check_unmapped(hass, entry)

    issue = issue_of(hass, entry)
    assert issue is not None and issue.is_fixable is False
    assert issue.translation_key == ISSUE_ZONES_UNMAPPED


async def test_the_reminder_goes_once_a_zone_exists(hass):
    adopt(hass, zones=(1, 2))
    entry = our_entry(hass)
    _async_check_unmapped(hass, entry)

    hass.config_entries.async_update_entry(
        entry, options={**entry.options, CONF_ZONES: [{"zone_id": "a", CONF_RELAY_ENTITY: "switch.x"}]}
    )
    _async_check_unmapped(hass, entry)

    assert issue_of(hass, entry) is None


async def test_no_reminder_without_a_board_to_read(hass):
    entry = our_entry(hass)

    _async_check_unmapped(hass, entry)

    assert issue_of(hass, entry) is None


async def test_a_failing_lookup_never_breaks_setup(hass):
    entry = our_entry(hass)

    with patch("custom_components.openhydronic.async_get_board", side_effect=RuntimeError("boom")):
        _async_check_unmapped(hass, entry)

    assert issue_of(hass, entry) is None


# ---------------------------------------------------------------------------
# Review follow-ups
# ---------------------------------------------------------------------------
async def test_a_master_switch_that_is_unavailable_is_not_taken_for_done(hass):
    # A service call skips an unavailable entity without a word.
    adopt(hass, master_state="unavailable")
    calls = async_mock_service(hass, "switch", "turn_on")
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {"zone_1": {"sensor_entity": "sensor.living"}, CONF_MASTER_CHOICE: "board"},
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "master_switch_failed"}
    assert calls == []


async def test_a_master_switch_that_refuses_is_reported(hass):
    adopt(hass)

    async def refuse(call):
        raise HomeAssistantError("no")

    hass.services.async_register("switch", "turn_on", refuse)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MASTER_CHOICE: "board"}
    )

    assert result["errors"] == {"base": "master_switch_failed"}


async def test_a_switch_picked_without_the_answer_still_counts(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {
            "zone_1": {"sensor_entity": "sensor.living"},
            CONF_MASTER_CHOICE: "none",
            CONF_MASTER_ENTITY: "switch.boiler_shelly",
        },
    )

    assert result["options"][CONF_MASTER_MODE] == MASTER_EXTERNAL
    assert result["options"][CONF_MASTER_ENTITY] == "switch.boiler_shelly"


async def test_a_room_name_without_its_sensor_is_not_silently_dropped(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zone_1": {"name": "Living room"}, CONF_MASTER_CHOICE: "none"}
    )

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "sensor_required"}


async def test_the_form_keeps_what_was_typed_after_an_error(hass):
    adopt(hass)
    result = await confirm(hass, await discover(hass))

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {"zone_1": {"name": "Living room"}, CONF_MASTER_CHOICE: "none"}
    )

    section = fields(result)["zone_1"]
    suggested = {
        item["name"]: item.get("description", {}).get("suggested_value") for item in section["schema"]
    }
    assert suggested.get("name") == "Living room"


async def test_a_host_typed_by_hand_with_nothing_to_read_is_added_at_once(hass):
    # An ESPHome board that is not this one: no Zone N switches, nothing to wait for.
    adopt(hass, zones=(), master=False)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST, "port": 6053}
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["options"][CONF_ZONES] == []


async def test_typing_the_host_while_the_discovery_card_is_open_is_not_refused(hass):
    adopt(hass)
    await discover(hass)  # the card is still waiting
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST, "port": 6053}
    )
    assert result["step_id"] == "zones"
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_MASTER_CHOICE: "none"}
    )
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    # The entry took the card's place: nothing is left to confirm.
    assert hass.config_entries.flow.async_progress_by_handler(DOMAIN) == []


async def test_a_board_added_by_hand_meanwhile_is_not_added_twice(hass):
    result = await discover(hass)
    MockConfigEntry(
        domain=DOMAIN, unique_id=HOST, data={CONF_HOST: HOST}, options={CONF_ZONES: []}
    ).add_to_hass(hass)

    result = await confirm(hass, result)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_an_entry_from_before_the_mac_was_stored_still_gets_the_menu(hass):
    # v1.0.x entries carry only a host.
    adopt(hass, zones=(1, 2))
    entry = MockConfigEntry(
        domain=DOMAIN, unique_id=HOST, title="OpenHydronic",
        data={CONF_HOST: HOST}, options={CONF_ZONES: [], CONF_MASTER_MODE: MASTER_DISABLED},
    )
    entry.add_to_hass(hass)

    result = await hass.config_entries.options.async_init(entry.entry_id)

    assert result["menu_options"][0] == "import_zones"
    _async_check_unmapped(hass, entry)
    assert issue_of(hass, entry) is not None


async def test_importing_with_a_name_but_no_sensor_says_so(hass):
    adopt(hass, zones=(1,))
    entry = our_entry(hass)
    result = await hass.config_entries.options.async_init(entry.entry_id)
    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"next_step_id": "import_zones"}
    )

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {"zone_1": {"name": "Living room"}}
    )

    assert result["errors"] == {"base": "sensor_required"}


async def test_no_reminder_when_another_entry_already_owns_the_relays(hass):
    adopt(hass, zones=(1, 2))
    mine = our_entry(hass)
    MockConfigEntry(
        domain=DOMAIN, unique_id="other", data={CONF_HOST: "10.0.0.9"},
        options={CONF_ZONES: [{CONF_RELAY_ENTITY: "switch.openhydronic_zone_1"},
                              {CONF_RELAY_ENTITY: "switch.openhydronic_zone_2"}]},
    ).add_to_hass(hass)

    _async_check_unmapped(hass, mine)

    assert issue_of(hass, mine) is None


async def test_the_reminder_follows_the_board_as_ESPHome_registers_it(hass):
    entry = our_entry(hass)
    _async_watch_board(hass, entry)
    assert issue_of(hass, entry) is None

    adopt(hass, zones=(1, 2))
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is not None


async def test_removing_the_entry_takes_its_reminder_with_it(hass):
    adopt(hass, zones=(1,))
    entry = our_entry(hass)
    _async_check_unmapped(hass, entry)
    assert issue_of(hass, entry) is not None

    await async_remove_entry(hass, entry)

    assert issue_of(hass, entry) is None
