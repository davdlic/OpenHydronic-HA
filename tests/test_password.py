# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""The repair that moves a board off the public password, on a real Home Assistant.

Skipped without pytest-homeassistant-custom-component, like the config flow tests.
"""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.data_entry_flow import FlowResultType
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import issue_registry as ir

from custom_components.openhydronic import (
    ISSUE_DEFAULT_PASSWORD,
    ISSUE_ZONES_UNMAPPED,
    _async_check_password,
    _async_check_unmapped,
    _async_watch_board,
    async_unload_entry,
)
from custom_components.openhydronic import repairs as repairs_module
from custom_components.openhydronic.const import DOMAIN
from custom_components.openhydronic.repairs import (
    DefaultPasswordRepairFlow,
    async_create_fix_flow,
    password_problem,
)

from test_config_flow import adopt, our_entry  # pytest puts tests/ on the path

TEXT = "text.openhydronic_board_password"
FLAG = "binary_sensor.openhydronic_default_password"


@pytest.fixture(autouse=True)
def _integration(enable_custom_integrations, hass):
    hass.config.components.update({"http", "frontend", "persistent_notification"})
    with (
        patch("custom_components.openhydronic.async_setup", return_value=True),
        patch("custom_components.openhydronic.async_setup_entry", return_value=True),
    ):
        yield


def issue_of(hass, entry):
    return ir.async_get(hass).async_get_issue(DOMAIN, f"{ISSUE_DEFAULT_PASSWORD}_{entry.entry_id}")


def board_that_takes_it(hass):
    """The text.set_value service of a board that accepts and then reports it."""
    calls = []

    async def take(call):
        calls.append(call)
        hass.states.async_set(FLAG, "off")

    hass.services.async_register("text", "set_value", take)
    return calls


def flow_for(hass, entry):
    flow = DefaultPasswordRepairFlow(entry.entry_id)
    flow.hass = hass
    flow.handler = DOMAIN
    flow.flow_id = "test"
    return flow


# ---------------------------------------------------------------------------
# The reminder
# ---------------------------------------------------------------------------
async def test_a_board_on_the_public_password_raises_a_repair_you_can_act_on(hass):
    adopt(hass, default_password="on")
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    issue = issue_of(hass, entry)
    assert issue is not None
    assert issue.is_fixable is True
    assert issue.data == {"entry_id": entry.entry_id}
    assert issue.translation_key == ISSUE_DEFAULT_PASSWORD


async def test_a_board_with_its_own_password_raises_nothing(hass):
    adopt(hass, default_password="off")
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


async def test_the_repair_goes_once_the_board_says_it_has_a_password(hass):
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    _async_check_password(hass, entry)
    assert issue_of(hass, entry) is not None

    hass.states.async_set(FLAG, "off")
    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


@pytest.mark.parametrize("state", ["unavailable", "unknown"])
async def test_an_offline_board_leaves_the_repair_as_it_was(hass, state):
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    _async_check_password(hass, entry)
    assert issue_of(hass, entry) is not None

    hass.states.async_set(FLAG, state)
    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is not None


async def test_an_offline_board_does_not_invent_a_repair(hass):
    adopt(hass, default_password="unavailable")
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


async def test_older_firmware_without_the_entities_raises_nothing(hass):
    adopt(hass, password=False)
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


async def test_the_flag_without_the_text_to_set_it_raises_nothing(hass):
    # A repair nobody can complete would only nag.
    adopt(hass, default_password="on")
    from homeassistant.helpers import entity_registry as er

    er.async_get(hass).async_remove(TEXT)
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


async def test_no_board_no_repair(hass):
    entry = our_entry(hass)

    _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


async def test_a_failing_lookup_never_breaks_setup(hass):
    entry = our_entry(hass)

    with patch("custom_components.openhydronic.async_get_board", side_effect=RuntimeError("boom")):
        _async_check_password(hass, entry)

    assert issue_of(hass, entry) is None


# ---------------------------------------------------------------------------
# The watcher follows the board
# ---------------------------------------------------------------------------
async def test_the_repair_clears_by_itself_when_the_board_gets_a_password(hass):
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    _async_watch_board(hass, entry)
    assert issue_of(hass, entry) is not None

    hass.states.async_set(FLAG, "off")
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is None


async def test_the_repair_returns_if_the_board_goes_back_to_the_public_password(hass):
    adopt(hass, default_password="off")
    entry = our_entry(hass)
    _async_watch_board(hass, entry)
    assert issue_of(hass, entry) is None

    hass.states.async_set(FLAG, "on")  # a factory reset
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is not None


async def test_a_board_that_is_added_afterwards_is_picked_up(hass):
    entry = our_entry(hass)
    _async_watch_board(hass, entry)
    assert issue_of(hass, entry) is None

    adopt(hass, default_password="on")
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is not None


async def test_the_watcher_stops_with_the_entry(hass):
    adopt(hass, default_password="off")
    entry = our_entry(hass)
    cleanups = []
    with patch.object(entry, "async_on_unload", side_effect=cleanups.append):
        _async_watch_board(hass, entry)
    assert cleanups  # it registered something to undo

    for stop in cleanups:  # what an unload runs
        stop()
    hass.states.async_set(FLAG, "on")
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is None


# ---------------------------------------------------------------------------
# The renamed sensor and the unload
# ---------------------------------------------------------------------------
async def test_a_renamed_sensor_is_still_followed(hass):
    from homeassistant.helpers import entity_registry as er

    adopt(hass, default_password="on")
    entry = our_entry(hass)
    _async_watch_board(hass, entry)
    assert issue_of(hass, entry) is not None

    er.async_get(hass).async_update_entity(FLAG, new_entity_id="binary_sensor.renamed_by_the_user")
    await hass.async_block_till_done()
    hass.states.async_set("binary_sensor.renamed_by_the_user", "off")
    await hass.async_block_till_done()

    assert issue_of(hass, entry) is None


async def test_unloading_takes_both_reminders_away(hass):
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    _async_check_password(hass, entry)
    _async_check_unmapped(hass, entry)
    registry = ir.async_get(hass)
    assert issue_of(hass, entry) is not None
    assert registry.async_get_issue(DOMAIN, f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}") is not None

    hass.data[DOMAIN] = {
        entry.entry_id: SimpleNamespace(async_shutdown_coordinator=lambda: _done())
    }
    with patch.object(hass.config_entries, "async_unload_platforms", return_value=True):
        assert await async_unload_entry(hass, entry) is True

    assert issue_of(hass, entry) is None
    assert registry.async_get_issue(DOMAIN, f"{ISSUE_ZONES_UNMAPPED}_{entry.entry_id}") is None


async def _done():
    return None


# ---------------------------------------------------------------------------
# What the board will take
# ---------------------------------------------------------------------------
@pytest.mark.parametrize(
    ("password", "problem"),
    [
        ("12345678", None),
        ("a" * 64, None),
        ("p@ss &word!~", None),
        ("1234567", "password_short"),
        ("a" * 65, "password_long"),
        ("pálavra-passe", "password_chars"),  # an accent
        ("émoji-\U0001f600-1234", "password_chars"),
        ("tab\there-1234", "password_chars"),  # not printable
        ("nul\x00inside1", "password_chars"),
        ("ç", "password_chars"),  # short and accented: the accent is what to fix
    ],
)
def test_the_rules_are_the_boards(password, problem):
    assert password_problem(password) == problem


# ---------------------------------------------------------------------------
# The repair flow
# ---------------------------------------------------------------------------
async def test_the_fix_flow_belongs_to_this_repair_only(hass):
    entry = our_entry(hass)

    flow = await async_create_fix_flow(hass, f"{ISSUE_DEFAULT_PASSWORD}_{entry.entry_id}", {"entry_id": entry.entry_id})

    assert isinstance(flow, DefaultPasswordRepairFlow)
    with pytest.raises(ValueError):
        await async_create_fix_flow(hass, "something_else", {"entry_id": entry.entry_id})
    with pytest.raises(ValueError):
        await async_create_fix_flow(hass, f"{ISSUE_DEFAULT_PASSWORD}_x", None)


async def test_the_flow_asks_for_a_password(hass):
    adopt(hass)
    entry = our_entry(hass)

    result = await flow_for(hass, entry).async_step_init()

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "confirm"
    assert result["description_placeholders"] == {"name": entry.title}


@pytest.mark.parametrize(
    ("password", "error"),
    [("short", "password_short"), ("a" * 65, "password_long"), ("pálavra-passe-1", "password_chars")],
)
async def test_a_password_the_board_would_drop_is_refused_and_nothing_is_sent(hass, password, error):
    adopt(hass)
    entry = our_entry(hass)
    calls = board_that_takes_it(hass)

    result = await flow_for(hass, entry).async_step_confirm({"password": password})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": error}
    assert calls == []


async def test_a_good_password_reaches_the_boards_own_entity(hass):
    adopt(hass)
    entry = our_entry(hass)
    calls = board_that_takes_it(hass)  # the fallback when the entity is not reachable

    result = await flow_for(hass, entry).async_step_confirm({"password": "my own p@ss&word"})

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert [(c.data["entity_id"], c.data["value"]) for c in calls] == [(TEXT, "my own p@ss&word")]


async def test_the_password_is_handed_to_the_entity_not_put_on_the_event_bus(hass):
    # A service call fires an event with the value in it, which the recorder keeps.
    adopt(hass)
    entry = our_entry(hass)
    received = []

    class Entity:
        available = True

        async def async_set_value(self, value):
            received.append(value)
            hass.states.async_set(FLAG, "off")

    seen = []
    hass.bus.async_listen("call_service", lambda event: seen.append(event))
    hass.services.async_register("text", "set_value", lambda call: pytest.fail("the service was used"))
    platform = SimpleNamespace(entities={TEXT: Entity()})

    with patch("homeassistant.helpers.entity_platform.async_get_platforms", return_value=[platform]):
        result = await flow_for(hass, entry).async_step_confirm({"password": "my own p@ss&word"})
    await hass.async_block_till_done()

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert received == ["my own p@ss&word"]
    assert not any("my own p@ss&word" in str(event.data) for event in seen)


async def test_an_unavailable_entity_found_directly_is_not_told_it_worked(hass):
    adopt(hass)
    entry = our_entry(hass)

    class Entity:
        available = False

        async def async_set_value(self, value):
            pytest.fail("an unavailable entity was written to")

    platform = SimpleNamespace(entities={TEXT: Entity()})
    with patch("homeassistant.helpers.entity_platform.async_get_platforms", return_value=[platform]):
        result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert result["errors"] == {"base": "password_failed"}


async def test_a_board_that_refuses_it_is_reported(hass):
    adopt(hass)
    entry = our_entry(hass)

    async def refuse(call):
        raise HomeAssistantError("no")

    hass.services.async_register("text", "set_value", refuse)

    result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "password_failed"}


async def test_a_validation_error_that_quotes_the_value_never_reaches_the_log(hass, caplog):
    # Home Assistant's own validation puts the value in its message.
    adopt(hass)
    entry = our_entry(hass)
    secret = "very-secret-value-1"

    async def too_long(call):
        raise ValueError(f"Value {secret} for text.x is too long")

    hass.services.async_register("text", "set_value", too_long)

    result = await flow_for(hass, entry).async_step_confirm({"password": secret})

    assert result["errors"] == {"base": "password_failed"}
    assert secret not in caplog.text


async def test_a_board_that_takes_it_in_silence_is_not_told_it_worked(hass):
    # The board answers before it checks and drops what it will not take: the
    # sensor staying on is the only sign.
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    calls = []

    async def ignore(call):
        calls.append(call)

    hass.services.async_register("text", "set_value", ignore)

    with patch.object(repairs_module, "CONFIRM_SECONDS", 0.2):
        result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert calls and result["errors"] == {"base": "password_failed"}


async def test_the_sensor_flipping_before_the_call_returns_still_counts(hass):
    adopt(hass, default_password="on")
    entry = our_entry(hass)
    board_that_takes_it(hass)

    result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_an_offline_board_is_not_told_it_worked(hass):
    # A service call skips an unavailable entity without an error.
    adopt(hass)
    hass.states.async_set(TEXT, "unavailable")
    entry = our_entry(hass)
    calls = board_that_takes_it(hass)

    result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert result["errors"] == {"base": "password_failed"}
    assert calls == []


async def test_a_board_that_is_gone_is_not_told_it_worked(hass):
    entry = our_entry(hass)
    calls = board_that_takes_it(hass)

    result = await flow_for(hass, entry).async_step_confirm({"password": "long enough 1"})

    assert result["errors"] == {"base": "password_failed"}
    assert calls == []
