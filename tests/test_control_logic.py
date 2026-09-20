# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Unit tests for the decision core.

The methods under test are pure: they read zones and options and return the
wanted relay states, so they run without a Home Assistant instance.
"""

from __future__ import annotations

import time
import types

import pytest

# conftest.py installs the Home Assistant stand-ins before this import.
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
