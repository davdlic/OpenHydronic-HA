# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""The integration set up for real, with a zone of each control mode.

Needs Home Assistant, so the plain run skips it. The frontend and the repair
checks are not what is tested here and are left out.
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

pytest.importorskip("pytest_homeassistant_custom_component")

from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry, async_mock_service

from custom_components.openhydronic.const import (
    CONF_CONTROL_MODE,
    CONF_FLOOR_TYPE,
    CONF_HOST,
    CONF_MAC,
    CONF_MASTER_MODE,
    CONF_NODE_NAME,
    CONF_RELAY_ENTITY,
    CONF_SENSOR_ENTITY,
    CONF_ZONES,
    CONTROL_PROPORTIONAL,
    DOMAIN,
    FLOOR_TRADITIONAL,
    MASTER_DISABLED,
)


@pytest.fixture(autouse=True)
def _integration(enable_custom_integrations, hass):
    hass.config.components.update({"http", "frontend", "persistent_notification"})
    with (
        patch("custom_components.openhydronic.async_setup", return_value=True),
        patch("custom_components.openhydronic._async_watch_board"),
    ):
        yield


def zone(zone_id: str, **extra) -> dict:
    return {
        "zone_id": zone_id,
        "name": zone_id.title(),
        CONF_RELAY_ENTITY: f"switch.{zone_id}",
        CONF_SENSOR_ENTITY: f"sensor.{zone_id}_temperature",
        **extra,
    }


async def start(hass, *zones):
    entry = MockConfigEntry(
        domain=DOMAIN,
        unique_id="10061cf5f81c",
        title="OpenHydronic",
        data={CONF_HOST: "192.168.1.40", CONF_MAC: "10061cf5f81c", CONF_NODE_NAME: "node"},
        options={CONF_ZONES: list(zones), CONF_MASTER_MODE: MASTER_DISABLED},
    )
    entry.add_to_hass(hass)
    async_mock_service(hass, "homeassistant", "turn_on")
    async_mock_service(hass, "homeassistant", "turn_off")
    for item in zones:
        hass.states.async_set(item[CONF_RELAY_ENTITY], "off")
        hass.states.async_set(item[CONF_SENSOR_ENTITY], "20.5")
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


def duty_entities(hass, entry):
    return [
        e.entity_id
        for e in er.async_entries_for_config_entry(er.async_get(hass), entry.entry_id)
        if e.unique_id.endswith("_duty")
    ]


async def test_only_a_proportional_zone_gets_a_duty_sensor(hass):
    entry = await start(
        hass,
        zone("old"),
        zone("floor", **{CONF_CONTROL_MODE: CONTROL_PROPORTIONAL}),
    )

    assert duty_entities(hass, entry) == ["sensor.openhydronic_floor_valve_duty"]


async def test_the_duty_sensor_shows_the_share_asked_of_the_valve(hass):
    await start(
        hass,
        zone(
            "floor",
            **{
                CONF_CONTROL_MODE: CONTROL_PROPORTIONAL,
                CONF_FLOOR_TYPE: FLOOR_TRADITIONAL,
            },
        ),
    )

    state = hass.states.get("sensor.openhydronic_floor_valve_duty")

    # 21.0 comfort setpoint against 20.5: half a degree below, Kp 0.5.
    assert state is not None
    assert float(state.state) == pytest.approx(25, abs=1)
    assert state.attributes["unit_of_measurement"] == "%"


async def test_a_zone_with_no_control_mode_saved_still_sets_up(hass):
    entry = await start(hass, zone("old"))

    assert duty_entities(hass, entry) == []
    assert hass.states.get("climate.openhydronic_old") is not None
