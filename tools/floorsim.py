# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Underfloor heating simulation: hysteresis against the proportional controller.

A room (an air node and a screed node) is fed by a buffer tank at a fixed water
temperature through one valve. The zone controller sees the room only through
a sensor that reports on a change or after a while, as a Zigbee sensor does.

The model is illustrative and not calibrated to any house, so only the
differences between controllers mean anything, not the absolute numbers. The
proportional controller is the one the integration ships, loaded from its own
file, so this exercises the real code.

    python tools/floorsim.py            # 35 degC water, the average house
    python tools/floorsim.py 45 heavy   # hotter water, thick screed
"""

from __future__ import annotations

import importlib
import math
import random
import sys
import types
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

# proportional.py has no Home Assistant import, but its package does: stand in for it.
_COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "openhydronic"
_package = types.ModuleType("_openhydronic")
_package.__path__ = [str(_COMPONENT)]
sys.modules.setdefault("_openhydronic", _package)
ProportionalController = importlib.import_module("_openhydronic.proportional").ProportionalController

DT = 15.0  # s, the control loop
MIN_RUN = 600.0
MIN_OFF = 300.0
OPEN_RATE = 1 / 180.0  # the actuator head opens in 3 min
CLOSE_RATE = 1 / 300.0  # and closes in 5
Q_INT = 80.0  # W of internal gains


@dataclass(frozen=True)
class House:
    c_air: float = 2.0e6  # J/K, air, furniture and interior surfaces
    c_scr: float = 2.4e6  # J/K, the screed above the pipes
    ua_env: float = 50.0  # W/K, losses to the outside
    ua_fa: float = 150.0  # W/K, screed to room
    ua_w: float = 200.0  # W/K, water to screed with the valve open
    sun: float = 1.0  # scale of the sun gains
    sun_to_floor: float = 0.25  # share of the sun that lands on the floor


HOUSES = {
    "average": House(),
    "light": House(c_air=1.0e6, c_scr=1.4e6, ua_env=70.0, ua_fa=170.0, sun=1.3),
    "heavy": House(c_air=3.0e6, c_scr=3.8e6, ua_env=40.0, ua_fa=130.0, sun=0.8),
}


def hour(t: float) -> float:
    return (t % 86400.0) / 3600.0


def sun_profile(h: float) -> float:
    """W of sun through the glass."""
    if h < 9.5 or h > 17.5:
        return 0.0
    if h < 11.0:
        return 600.0 * (h - 9.5) / 1.5
    if h < 15.5:
        return 600.0
    return 600.0 * (17.5 - h) / 2.0


def clouds(h: float) -> float:
    for start in (11.5, 13.0, 14.5):  # three clouds of 25 minutes
        if start <= h < start + 25 / 60:
            return 0.2
    return 1.0


def window_open(h: float) -> float:
    """Extra loss in W while a window is open for 15 minutes."""
    for start in (8.0, 19.0):
        if start <= h < start + 0.25:
            return 1500.0
    return 0.0


def _daily_outdoor(t: float) -> float:
    return 7.0 + 4.0 * math.sin(2 * math.pi * (hour(t) - 9.0) / 24.0)


@dataclass
class Scenario:
    name: str
    outdoor: Callable[[float], float]
    sun: Callable[[float], float]
    target: Callable[[float], float]
    window: tuple[float, float]  # hours over which time off target is counted
    dip: tuple[float, float]  # hours over which the lowest temperature is taken
    peak: tuple[float, float]  # hours over which the highest temperature is taken
    extra_loss: Callable[[float], float] = lambda h: 0.0


SCENARIOS = [
    Scenario("cold day", lambda t: 3.0, lambda t: 0.0, lambda t: 21.0, (0, 24), (0, 24), (0, 24)),
    Scenario(
        "sunny day", _daily_outdoor, lambda t: sun_profile(hour(t)), lambda t: 21.0,
        (0, 24), (17.5, 24), (12, 18),
    ),
    Scenario(
        "comfort in the evening", lambda t: 5.0, lambda t: 0.0,
        lambda t: 21.0 if 17.0 <= hour(t) < 23.0 else 18.5, (17, 23), (17, 23), (17, 23),
    ),
    Scenario(
        "cold day, windows opened", lambda t: 3.0, lambda t: 0.0, lambda t: 21.0,
        (0, 24), (0, 24), (0, 24), extra_loss=window_open,
    ),
    Scenario(
        "sunny day with clouds", _daily_outdoor, lambda t: sun_profile(hour(t)) * clouds(hour(t)),
        lambda t: 21.0, (0, 24), (17.5, 24), (12, 18),
    ),
]


class Sensor:
    """Reports on a change of `delta`, or after `max_int`, never faster than `min_int`."""

    def __init__(
        self, delta: float, max_int: float, min_int: float = 60.0,
        resolution: float = 0.01, noise: float = 0.0, seed: int = 1,
    ) -> None:
        self.delta, self.max_int, self.min_int = delta, max_int, min_int
        self.resolution, self.noise = resolution, noise
        self.rng = random.Random(seed)
        self.value: float | None = None
        self.t_last = 0.0

    def update(self, t: float, room: float) -> None:
        if self.noise:
            room += self.rng.gauss(0.0, self.noise)
        measured = round(round(room / self.resolution) * self.resolution, 3)
        if self.value is None:
            send = True
        else:
            waited = t - self.t_last
            send = waited >= self.min_int and (
                abs(measured - self.value) >= self.delta - 1e-9 or waited >= self.max_int
            )
        if send:
            self.value, self.t_last = measured, t


COARSE = {"delta": 1.0, "max_int": 3600.0}  # what many Zigbee sensors ship with
FINE = {"delta": 0.2, "max_int": 600.0}


class Guarded:
    """Whatever wants the valve open still goes through the minimum run and off times."""

    def __init__(self) -> None:
        self.out = False
        self.last_switch = -1e9

    def want(self, t: float, sensor: Sensor, target: float) -> bool:
        raise NotImplementedError

    def step(self, t: float, sensor: Sensor, target: float) -> bool:
        wanted = self.want(t, sensor, target)
        elapsed = t - self.last_switch
        if wanted and not self.out and elapsed < MIN_OFF:
            wanted = False
        elif not wanted and self.out and elapsed < MIN_RUN:
            wanted = True
        if wanted != self.out:
            self.out, self.last_switch = wanted, t
        return self.out


class Hysteresis(Guarded):
    """The band the integration uses by default."""

    def __init__(self, hyst: float = 0.3) -> None:
        super().__init__()
        self.hyst = hyst
        self.demand = False

    def want(self, t: float, sensor: Sensor, target: float) -> bool:
        if self.demand:
            self.demand = sensor.value < target + self.hyst
        else:
            self.demand = sensor.value < target - self.hyst
        return self.demand


class Proportional:
    """The controller the integration ships, fed as the coordinator feeds it."""

    def __init__(self, period: float) -> None:
        self.controller = ProportionalController(period)
        self.out = False
        self.last_switch = -1e9

    def step(self, t: float, sensor: Sensor, target: float) -> bool:
        wanted = self.controller.update(
            error=target - sensor.value, now=t, is_open=self.out,
            since_switch=t - self.last_switch, min_run=MIN_RUN, min_off=MIN_OFF,
        )
        if wanted != self.out:
            self.out, self.last_switch = wanted, t
        return self.out


def run(
    scenario: Scenario, controller, sensor: Sensor, water: float,
    house: House = HOUSES["average"], days: int = 4, trace: bool = False,
):
    """Simulate `days` days and report on the last one. With `trace`, also the valve."""
    ta = tf = scenario.target(0.0)
    valve = 0.0
    start = (days - 1) * 86400.0
    log: dict[str, list] = {"h": [], "ta": [], "tf": [], "on": []}
    ta_dip: list[float] = []
    ta_peak: list[float] = []
    ta_all: list[float] = []
    energy = below = above = 0.0
    cycles = 0
    prev_on = False
    ta0 = tf0 = None
    for i in range(int(days * 86400 / DT)):
        t = i * DT
        h = hour(t)
        sensor.update(t, ta)
        target = scenario.target(t)
        on = controller.step(t, sensor, target)
        command = 1.0 if on else 0.0
        if valve < command:
            valve = min(command, valve + OPEN_RATE * DT)
        else:
            valve = max(command, valve - CLOSE_RATE * DT)
        q_water = house.ua_w * valve * (water - tf)
        q_floor = house.ua_fa * (tf - ta)
        q_loss = house.ua_env * (ta - scenario.outdoor(t)) + scenario.extra_loss(h)
        q_sun = scenario.sun(t) * house.sun
        d_ta = (q_floor + q_sun * (1 - house.sun_to_floor) + Q_INT - q_loss) / house.c_air
        d_tf = (q_water - q_floor + q_sun * house.sun_to_floor) / house.c_scr
        if t >= start:
            if ta0 is None:
                ta0, tf0 = ta, tf
            ta_all.append(ta)
            if scenario.window[0] <= h < scenario.window[1]:
                below += DT if ta < target - 0.5 else 0.0
                above += DT if ta > target + 0.5 else 0.0
            if scenario.dip[0] <= h < scenario.dip[1]:
                ta_dip.append(ta)
            if scenario.peak[0] <= h < scenario.peak[1]:
                ta_peak.append(ta)
            energy += q_water * DT
            if on and not prev_on:
                cycles += 1
            if trace:
                log["h"].append(h)
                log["ta"].append(ta)
                log["tf"].append(tf)
                log["on"].append(1 if on else 0)
        prev_on = on
        ta += DT * d_ta
        tf += DT * d_tf
    # What really had to be supplied: what left the tank minus what was stored.
    stored = house.c_air * (ta - ta0) + house.c_scr * (tf - tf0)
    result = {
        "tmin": min(ta_dip),
        "tmax": max(ta_peak),
        "below": below / 60.0,  # minutes more than 0.5 degC under the target
        "above": above / 60.0,  # minutes more than 0.5 degC over it
        "kwh": (energy - stored) / 3.6e6,
        "mean": sum(ta_all) / len(ta_all),
        "cycles": cycles,
    }
    return (result, log) if trace else result


def controllers():
    return [
        ("hysteresis 0.3, sensor 1 C", lambda: Hysteresis(), COARSE),
        ("hysteresis 0.3, sensor 0.2 C", lambda: Hysteresis(), FINE),
        ("hysteresis 0.2, sensor 0.2 C", lambda: Hysteresis(0.2), FINE),
        ("proportional 60 min, sensor 0.2 C", lambda: Proportional(3600.0), FINE),
        ("proportional 90 min, sensor 0.2 C", lambda: Proportional(5400.0), FINE),
    ]


def table(water: float, house_name: str = "average") -> None:
    house = HOUSES[house_name]
    print(f"\n######## {house_name} house, water at {water:.0f} C ########")
    header = "controller".ljust(36) + " Tmin   Tmax  <t-.5  >t+.5   kWh  mean  cycles"
    for scenario in SCENARIOS:
        print(f"\n=== {scenario.name} ===\n{header}")
        for name, make, sensor in controllers():
            r = run(scenario, make(), Sensor(**sensor), water, house)
            print(
                f"{name.ljust(36)} {r['tmin']:5.1f} {r['tmax']:6.1f} {r['below']:5.0f}m "
                f"{r['above']:5.0f}m {r['kwh']:5.1f} {r['mean']:5.2f} {r['cycles']:6d}"
            )


if __name__ == "__main__":
    table(
        float(sys.argv[1]) if len(sys.argv) > 1 else 35.0,
        sys.argv[2] if len(sys.argv) > 2 else "average",
    )
