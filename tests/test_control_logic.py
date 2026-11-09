# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Unit tests for the decision core and for how a zone's inputs are read.

The methods under test read zones, options and a few states and return the
wanted relay states, so they run without a Home Assistant instance.
"""

from __future__ import annotations

import time
import types
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest

# conftest.py installs the Home Assistant stand-ins before this import.
from homeassistant.components import persistent_notification

from custom_components.openhydronic import const
from custom_components.openhydronic.coordinator import (
    COLD_START_AGE,
    HVAC_OFF,
    OpenHydronicCoordinator,
    ZoneRuntime,
    _restore_switch_time,
)


def make_zone(zone_id: str = "z1", **kwargs) -> ZoneRuntime:
    defaults = {
        "zone_id": zone_id,
        "name": zone_id,
        "relay_entity": f"switch.{zone_id}",
        "sensor_entity": f"sensor.{zone_id}",
        "is_bypass": False,
        "comfort_temp": 21.0,
        "eco_temp": 18.5,
        "away_temp": 16.0,
    }
    defaults.update(kwargs)
    return ZoneRuntime(**defaults)


def make_coordinator(zones: list[ZoneRuntime], **options):
    """Coordinator with only the attributes the decision core touches."""
    coordinator = object.__new__(OpenHydronicCoordinator)
    coordinator.entry = types.SimpleNamespace(options=options, entry_id="test")
    coordinator.zones = {zone.zone_id: zone for zone in zones}
    coordinator.summer_mode = False
    coordinator.holiday_mode = False
    coordinator._air_purge_until = None
    coordinator._anti_seize_until = None
    coordinator.master_state = const.MASTER_STATE_DISABLED
    coordinator._demand_started_at = None
    coordinator._demand_ended_at = None
    coordinator._master_output = False
    return coordinator


# ---------------------------------------------------------------------------
# Hysteresis
# ---------------------------------------------------------------------------
def test_zone_calls_for_heat_below_the_band():
    zone = make_zone(current_temp=20.0)
    coordinator = make_coordinator([zone])

    assert coordinator._evaluate_demand() == {"z1": True}


def test_zone_keeps_heating_inside_the_band():
    # Already heating at setpoint: it must not release until setpoint + 0.3.
    zone = make_zone(current_temp=21.0, demand=True)
    coordinator = make_coordinator([zone])

    assert coordinator._evaluate_demand() == {"z1": True}


def test_zone_releases_above_the_band():
    zone = make_zone(current_temp=21.4, demand=True)
    coordinator = make_coordinator([zone])

    assert coordinator._evaluate_demand() == {"z1": False}


def test_faulted_zone_never_calls_for_heat():
    zone = make_zone(current_temp=5.0, fault=const.FAULT_SENSOR_STALE)
    coordinator = make_coordinator([zone])

    assert coordinator._evaluate_demand() == {"z1": False}


def test_zone_switched_off_never_calls_for_heat():
    zone = make_zone(current_temp=5.0, hvac_mode=HVAC_OFF)
    coordinator = make_coordinator([zone])

    assert coordinator._evaluate_demand() == {"z1": False}


# ---------------------------------------------------------------------------
# Cycle guards
# ---------------------------------------------------------------------------
def test_min_off_blocks_an_early_restart():
    now = time.monotonic()
    zone = make_zone(output=False, last_switch_at=now - 60)
    coordinator = make_coordinator([zone])

    assert coordinator._apply_cycle_guards({"z1": True}, now) == {"z1": False}


def test_min_run_holds_a_zone_open():
    now = time.monotonic()
    zone = make_zone(output=True, last_switch_at=now - 60)
    coordinator = make_coordinator([zone])

    assert coordinator._apply_cycle_guards({"z1": False}, now) == {"z1": True}


def test_fault_releases_the_zone_even_inside_min_run():
    now = time.monotonic()
    zone = make_zone(output=True, last_switch_at=now, fault=const.FAULT_SENSOR_STALE)
    coordinator = make_coordinator([zone])

    assert coordinator._apply_cycle_guards({"z1": False}, now) == {"z1": False}


def test_restored_zone_is_not_locked_out_after_a_restart():
    # Regression: zones used to start locked for the whole min-OFF window,
    # which switched the heating off on every reload.
    now = time.monotonic()
    zone = make_zone(output=False)  # default last_switch_at is backdated
    coordinator = make_coordinator([zone])

    assert coordinator._apply_cycle_guards({"z1": True}, now) == {"z1": True}


def test_restore_switch_time_uses_the_stored_wall_clock():
    restored = _restore_switch_time({"last_switch_epoch": time.time() - 120})

    assert time.monotonic() - restored == pytest.approx(120, abs=2)


def test_restore_switch_time_without_history_starts_unlocked():
    restored = _restore_switch_time({})

    assert time.monotonic() - restored == pytest.approx(COLD_START_AGE, abs=2)


def test_restore_switch_time_survives_a_clock_going_backwards():
    restored = _restore_switch_time({"last_switch_epoch": time.time() + 5000})

    assert time.monotonic() - restored == pytest.approx(COLD_START_AGE, abs=2)


# ---------------------------------------------------------------------------
# Master state machine
# ---------------------------------------------------------------------------
def test_master_waits_for_the_thermal_delay():
    now = time.monotonic()
    coordinator = make_coordinator(
        [make_zone()],
        master_mode=const.MASTER_RELAY,
        master_entity="switch.boiler",
    )

    assert coordinator._resolve_master({"z1": True}, now) is False
    assert coordinator.master_state == const.MASTER_STATE_WAITING


def test_master_starts_once_the_delay_elapsed():
    now = time.monotonic()
    coordinator = make_coordinator(
        [make_zone()],
        master_mode=const.MASTER_RELAY,
        master_entity="switch.boiler",
    )
    coordinator._resolve_master({"z1": True}, now)

    later = now + const.DEFAULT_MASTER_START_DELAY + 1
    assert coordinator._resolve_master({"z1": True}, later) is True
    assert coordinator.master_state == const.MASTER_STATE_ON


def test_master_purges_residual_heat_before_stopping():
    now = time.monotonic()
    coordinator = make_coordinator(
        [make_zone()],
        master_mode=const.MASTER_RELAY,
        master_entity="switch.boiler",
    )
    coordinator._resolve_master({"z1": True}, now)
    coordinator._resolve_master({"z1": True}, now + const.DEFAULT_MASTER_START_DELAY + 1)

    stop = now + const.DEFAULT_MASTER_START_DELAY + 2
    assert coordinator._resolve_master({"z1": False}, stop) is True
    assert coordinator.master_state == const.MASTER_STATE_PURGING

    assert (
        coordinator._resolve_master(
            {"z1": False}, stop + const.DEFAULT_HEAT_PURGE_DELAY + 1
        )
        is False
    )
    assert coordinator.master_state == const.MASTER_STATE_OFF


def test_master_stays_disabled_without_an_entity():
    coordinator = make_coordinator([make_zone()], master_mode=const.MASTER_DISABLED)

    assert coordinator._resolve_master({"z1": True}, time.monotonic()) is False
    assert coordinator.master_state == const.MASTER_STATE_DISABLED


# ---------------------------------------------------------------------------
# What reaches the circulator
# ---------------------------------------------------------------------------
def test_a_zone_locked_out_never_starts_the_pump():
    # Regression: a request the guard was still holding back counted as demand,
    # so the pump started against a fully closed circuit.
    now = time.monotonic()
    zone = make_zone(output=False, last_switch_at=now - 60)
    coordinator = make_coordinator([zone])

    outputs = coordinator._apply_cycle_guards({"z1": True}, now)

    assert coordinator._flowing_demand({"z1": True}, outputs) == {"z1": False}


def test_a_zone_held_open_while_closing_stops_asking_for_heat():
    now = time.monotonic()
    zone = make_zone(output=True, last_switch_at=now - 60)
    coordinator = make_coordinator([zone])

    outputs = coordinator._apply_cycle_guards({"z1": False}, now)

    assert outputs == {"z1": True}  # min-RUN keeps the valve open
    assert coordinator._flowing_demand({"z1": False}, outputs) == {"z1": False}


def test_an_open_zone_that_wants_heat_drives_the_pump():
    now = time.monotonic()
    zone = make_zone(output=True, last_switch_at=now - 3600)
    coordinator = make_coordinator([zone])

    outputs = coordinator._apply_cycle_guards({"z1": True}, now)

    assert coordinator._flowing_demand({"z1": True}, outputs) == {"z1": True}


# ---------------------------------------------------------------------------
# Bypass
# ---------------------------------------------------------------------------
def test_bypass_opens_when_the_pump_runs_against_a_closed_circuit():
    zones = [make_zone("z1"), make_zone("bp", is_bypass=True, sensor_entity=None)]
    coordinator = make_coordinator(zones)

    outputs = coordinator._apply_bypass({"z1": False, "bp": False}, True)

    assert outputs["bp"] is True


def test_bypass_closes_once_a_zone_is_open():
    zones = [make_zone("z1"), make_zone("bp", is_bypass=True, sensor_entity=None)]
    coordinator = make_coordinator(zones)

    outputs = coordinator._apply_bypass({"z1": True, "bp": True}, True)

    assert outputs["bp"] is False


def test_bypass_stays_closed_with_the_pump_off():
    zones = [make_zone("z1"), make_zone("bp", is_bypass=True, sensor_entity=None)]
    coordinator = make_coordinator(zones)

    outputs = coordinator._apply_bypass({"z1": False, "bp": False}, False)

    assert outputs["bp"] is False


# ---------------------------------------------------------------------------
# System modes
# ---------------------------------------------------------------------------
def test_summer_mode_stops_every_zone():
    zone = make_zone(current_temp=5.0)
    coordinator = make_coordinator([zone])
    coordinator.summer_mode = True

    assert coordinator._evaluate_demand() == {"z1": False}


def test_holiday_mode_regulates_on_the_away_setpoint():
    zone = make_zone(current_temp=17.0)  # below comfort, above away
    coordinator = make_coordinator([zone])
    coordinator.holiday_mode = True

    assert coordinator._evaluate_demand() == {"z1": False}


def test_air_purge_opens_everything_and_ignores_the_guards():
    now = time.monotonic()
    zone = make_zone(current_temp=30.0, output=False, last_switch_at=now)
    coordinator = make_coordinator([zone])
    coordinator._air_purge_until = now + 600

    demand = coordinator._evaluate_demand()
    assert demand == {"z1": True}
    assert coordinator._apply_cycle_guards(demand, now) == {"z1": True}


# ---------------------------------------------------------------------------
# Lock shown on the card
# ---------------------------------------------------------------------------
def _locked_until(zone: ZoneRuntime) -> int:
    snapshot = make_coordinator([zone])._build_snapshot()
    return snapshot["zones"][zone.zone_id][const.ATTR_LOCKED_UNTIL]


def test_lock_is_shown_while_min_run_holds_a_zone_that_wants_to_stop():
    zone = make_zone(output=True, demand=False, last_switch_at=time.monotonic() - 60)

    assert _locked_until(zone) > 0


def test_lock_is_shown_while_min_off_holds_a_zone_that_wants_to_start():
    zone = make_zone(output=False, demand=True, last_switch_at=time.monotonic() - 60)

    assert _locked_until(zone) > 0


def test_no_lock_is_shown_when_the_relay_already_does_what_is_wanted():
    # Lowered, then raised again before min-run ended: nothing is being held back.
    now = time.monotonic()
    zone = make_zone(output=True, demand=True, last_switch_at=now - 60)
    coordinator = make_coordinator([zone])

    assert coordinator._apply_cycle_guards({"z1": True}, now) == {"z1": True}
    assert _locked_until(zone) == 0


def test_no_lock_is_shown_on_an_idle_zone():
    zone = make_zone(output=False, demand=False, last_switch_at=time.monotonic() - 60)

    assert _locked_until(zone) == 0


# ---------------------------------------------------------------------------
# Zone inputs
# ---------------------------------------------------------------------------
def _state(value: str, age: int = 0):
    seen = datetime.now(timezone.utc) - timedelta(seconds=age)
    return types.SimpleNamespace(state=value, last_updated=seen, last_reported=seen)


def _read_inputs(zone: ZoneRuntime, states: dict):
    coordinator = make_coordinator([zone])
    coordinator.hass = types.SimpleNamespace(
        states=types.SimpleNamespace(get=states.get),
        config=types.SimpleNamespace(language="en"),
    )
    coordinator._notified_faults = set()
    # A fault posts a notification, which needs a real hass under Home Assistant.
    with patch.object(persistent_notification, "async_create"), patch.object(
        persistent_notification, "async_dismiss"
    ):
        coordinator._read_zone_inputs(zone)
    return coordinator


def test_room_temperature_is_read_while_the_relay_is_unavailable():
    # The sensor does not depend on the board.
    zone = make_zone()

    _read_inputs(zone, {"switch.z1": _state("unavailable"), "sensor.z1": _state("19.5")})

    assert zone.current_temp == 19.5
    assert zone.fault == const.FAULT_RELAY_MISSING


def test_room_temperature_is_read_while_the_relay_entity_is_missing():
    zone = make_zone()

    _read_inputs(zone, {"sensor.z1": _state("19.5")})

    assert zone.current_temp == 19.5
    assert zone.fault == const.FAULT_RELAY_MISSING


def test_a_relay_fault_still_holds_back_heat_on_a_cold_room():
    zone = make_zone()

    coordinator = _read_inputs(
        zone, {"switch.z1": _state("unavailable"), "sensor.z1": _state("12.0")}
    )

    assert coordinator._evaluate_demand() == {"z1": False}


def test_the_relay_fault_wins_over_a_sensor_fault():
    zone = make_zone()

    coordinator = _read_inputs(
        zone, {"switch.z1": _state("unavailable"), "sensor.z1": _state("unavailable")}
    )

    assert zone.current_temp is None
    assert zone.fault == const.FAULT_RELAY_MISSING
    assert coordinator._notified_faults == {"z1:relay_missing"}


def test_an_unavailable_sensor_is_a_fault_when_the_relay_is_fine():
    zone = make_zone(current_temp=19.5)

    _read_inputs(zone, {"switch.z1": _state("off"), "sensor.z1": _state("unavailable")})

    assert zone.current_temp is None
    assert zone.fault == const.FAULT_SENSOR_MISSING


def test_a_sensor_silent_past_the_watchdog_is_stale_but_still_shown():
    zone = make_zone()
    age = const.DEFAULT_SENSOR_TIMEOUT + 100

    _read_inputs(zone, {"switch.z1": _state("off"), "sensor.z1": _state("19.5", age)})

    assert zone.current_temp == 19.5
    assert zone.fault == const.FAULT_SENSOR_STALE


def test_healthy_inputs_clear_an_earlier_fault():
    zone = make_zone(fault=const.FAULT_SENSOR_STALE)

    coordinator = _read_inputs(
        zone, {"switch.z1": _state("off"), "sensor.z1": _state("19.5")}
    )

    assert zone.fault is None
    assert coordinator._notified_faults == set()


def test_a_zone_without_a_sensor_is_a_fault_unless_it_is_a_bypass():
    states = {"switch.z1": _state("off")}
    zone = make_zone(sensor_entity=None)
    bypass = make_zone(sensor_entity=None, is_bypass=True)

    _read_inputs(zone, states)
    _read_inputs(bypass, states)

    assert zone.fault == const.FAULT_SENSOR_MISSING
    assert bypass.fault is None


def test_the_relay_is_adopted_on_the_first_read():
    zone = make_zone()

    _read_inputs(zone, {"switch.z1": _state("on"), "sensor.z1": _state("19.5")})

    assert zone.synced
    assert zone.relay_on and zone.output
