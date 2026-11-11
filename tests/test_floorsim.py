# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""The floor simulation in tools/, run against the controller the integration ships.

The model is illustrative, so these only guard what the controller is for, with
wide margins: it must keep to the minimum run and off times, hold a steady
target, and not overshoot with hot water.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))

import floorsim  # noqa: E402

SCENARIO = {s.name: s for s in floorsim.SCENARIOS}
COLD = SCENARIO["cold day"]
SUNNY = SCENARIO["sunny day"]


def simulate(scenario, controller, water=35.0, house="average", sensor=None, **kwargs):
    sensor = sensor or floorsim.Sensor(**floorsim.FINE)
    return floorsim.run(scenario, controller, sensor, water, floorsim.HOUSES[house], **kwargs)


def runs(on):
    """(state, seconds) of each complete run; the first and last are cut off."""
    out = []
    count = 1
    for before, after in zip(on, on[1:]):
        if after == before:
            count += 1
        else:
            out.append((before, count * floorsim.DT))
            count = 1
    return out[1:]


@pytest.mark.parametrize("period", [3600.0, 5400.0])
@pytest.mark.parametrize("noise", [0.0, 0.1])
def test_the_valve_keeps_to_the_minimum_run_and_off_times(period, noise):
    sensor = floorsim.Sensor(0.2, 600.0, resolution=0.1, noise=noise)

    _, log = simulate(SUNNY, floorsim.Proportional(period), sensor=sensor, trace=True)

    complete = runs(log["on"])
    assert any(state for state, _ in complete)
    assert all(seconds >= floorsim.MIN_RUN for state, seconds in complete if state)
    assert all(seconds >= floorsim.MIN_OFF for state, seconds in complete if not state)


def test_it_holds_the_target_on_a_cold_day():
    result = simulate(COLD, floorsim.Proportional(3600.0))

    assert 20.9 <= result["tmin"] and result["tmax"] <= 21.1
    assert result["below"] == 0 and result["above"] == 0


def test_it_does_not_overshoot_with_hot_water_where_hysteresis_does():
    proportional = simulate(COLD, floorsim.Proportional(3600.0), water=45.0)
    hysteresis = simulate(COLD, floorsim.Hysteresis(), water=45.0)

    assert proportional["above"] == 0
    assert hysteresis["above"] > 300


def test_a_longer_cycle_opens_the_valve_less_often():
    short = simulate(COLD, floorsim.Proportional(3600.0))
    long = simulate(COLD, floorsim.Proportional(5400.0))

    assert long["cycles"] < short["cycles"] <= 24
    assert long["cycles"] <= 16


def test_it_uses_about_the_energy_of_hysteresis():
    proportional = simulate(COLD, floorsim.Proportional(3600.0))
    hysteresis = simulate(COLD, floorsim.Hysteresis(0.2))

    assert proportional["kwh"] == pytest.approx(hysteresis["kwh"], rel=0.05)
