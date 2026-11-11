# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Unit tests for the time-proportional valve controller.

The controller is plain arithmetic on an error and a clock, so these run
against an ideal valve that follows the controller instantly.
"""

from __future__ import annotations

import pytest

from custom_components.openhydronic.proportional import (
    MAX_STEP,
    ProportionalController,
)

MIN_RUN = 600.0
MIN_OFF = 300.0
STEP = 15.0
HOUR = 3600.0


def run(controller, error, hours, *, start_open=False):
    """Drive the controller with a valve that does as it is told.

    Returns the valve state at every step. `error` is a number or a function of
    the time in seconds.
    """
    is_open = start_open
    last_switch = 0.0 if start_open else -1e9
    states = []
    for i in range(int(hours * HOUR / STEP)):
        now = i * STEP
        wanted = controller.update(
            error=error(now) if callable(error) else error,
            now=now,
            is_open=is_open,
            since_switch=now - last_switch,
            min_run=MIN_RUN,
            min_off=MIN_OFF,
        )
        if wanted != is_open:
            is_open, last_switch = wanted, now
        states.append(is_open)
    return states


def runs_of(states):
    """(state, seconds) of every complete run; the first and last are cut."""
    runs = []
    count = 1
    for before, after in zip(states, states[1:]):
        if after == before:
            count += 1
        else:
            runs.append((before, count * STEP))
            count = 1
    return runs[1:]


def starts(states):
    return sum(1 for before, after in zip(states, states[1:]) if after and not before)


def flat(period=HOUR, **kwargs):
    """A controller whose integral does not move, to test the proportional part."""
    kwargs.setdefault("ti", 1e12)
    return ProportionalController(period, **kwargs)


# ---------------------------------------------------------------------------
# Duty
# ---------------------------------------------------------------------------
def test_no_duty_at_the_target():
    controller = flat()
    run(controller, 0.0, 1)
    assert controller.duty == 0.0


def test_duty_follows_the_error():
    controller = flat()
    run(controller, 1.0, 0.1)
    assert controller.duty == pytest.approx(0.5)


def test_duty_stops_at_both_ends():
    controller = flat()
    run(controller, 5.0, 0.1)
    assert controller.duty == 1.0
    run(controller, -5.0, 0.1)
    assert controller.duty == 0.0


def test_room_above_target_asks_for_nothing():
    controller = flat()
    states = run(controller, -0.4, 6)
    assert controller.duty == 0.0
    assert not any(states)


def test_integral_builds_up_while_the_room_stays_below():
    controller = ProportionalController(HOUR)
    run(controller, 0.2, 4)
    # One integral time at 0.2 degC adds Kp * 0.2 to the duty.
    assert controller.integral == pytest.approx(0.1, abs=0.005)
    assert controller.duty > controller.kp * 0.2


def test_integral_unwinds_while_the_room_stays_above():
    controller = ProportionalController(HOUR, integral=0.5)
    run(controller, -0.3, 8)
    assert controller.integral < 0.3


def test_integral_stops_where_the_duty_reaches_a_limit():
    controller = ProportionalController(HOUR)
    run(controller, 0.4, 48)
    assert controller.integral == pytest.approx(0.8, abs=0.01)
    run(controller, -0.4, 96)
    assert controller.integral == pytest.approx(0.2, abs=0.01)


def test_integral_does_not_wind_up_while_the_duty_is_full():
    controller = ProportionalController(HOUR)
    run(controller, 5.0, 12)
    assert controller.integral == 0.0


def test_integral_does_not_go_negative_while_the_duty_is_nil():
    controller = ProportionalController(HOUR)
    run(controller, -3.0, 12)
    assert controller.integral == 0.0


def test_a_saved_integral_is_clamped():
    assert ProportionalController(HOUR, integral=7).integral == 1.0
    assert ProportionalController(HOUR, integral=-1).integral == 0.0


def test_a_long_gap_counts_as_a_short_one():
    controller = ProportionalController(HOUR)
    controller.update(
        error=1.0, now=0.0, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    controller.update(
        error=1.0, now=10 * HOUR, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    expected = controller.kp / controller.ti * 1.0 * MAX_STEP
    assert controller.integral == pytest.approx(expected)


def test_the_clock_going_backwards_changes_nothing():
    controller = ProportionalController(HOUR)
    controller.update(
        error=1.0, now=100.0, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    controller.update(
        error=1.0, now=50.0, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    assert controller.integral == 0.0


# ---------------------------------------------------------------------------
# Pulses
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("error", [0.4, 1.0, 1.6])
def test_open_share_matches_the_duty(error):
    controller = flat()
    states = run(controller, error, 24)
    open_share = sum(states) / len(states)
    assert open_share == pytest.approx(controller.duty, abs=0.05)


def test_half_duty_cycles_about_once_an_hour():
    states = run(flat(HOUR), 1.0, 24)
    assert 22 <= starts(states) <= 26


def test_a_longer_period_means_fewer_and_longer_pulses():
    short = run(flat(HOUR), 1.0, 24)
    long = run(flat(1.5 * HOUR), 1.0, 24)
    assert starts(long) < starts(short)
    assert starts(long) in range(14, 18)


def test_every_pulse_is_at_least_the_minimum_run():
    for error in (0.1, 0.5, 1.0, 1.6, 1.9):
        states = run(flat(), error, 48)
        on = [seconds for state, seconds in runs_of(states) if state]
        assert on, error
        assert min(on) >= MIN_RUN, error


def test_every_gap_is_at_least_the_minimum_off():
    for error in (0.1, 0.5, 1.0, 1.6, 1.9):
        states = run(flat(), error, 48)
        off = [seconds for state, seconds in runs_of(states) if not state]
        assert off, error
        assert min(off) >= MIN_OFF, error


def test_a_small_duty_gives_few_minimum_pulses():
    controller = flat()
    states = run(controller, 0.1, 48)
    on = [seconds for state, seconds in runs_of(states) if state]
    assert controller.duty == pytest.approx(0.05)
    assert max(on) <= MIN_RUN + 3 * STEP
    # One minimum pulse every min_run / duty = 3.3 h.
    assert 12 <= starts(states) <= 16
    assert sum(states) / len(states) == pytest.approx(0.05, abs=0.015)


def test_full_duty_keeps_the_valve_open():
    states = run(flat(), 5.0, 6)
    assert all(states[int(MIN_OFF / STEP) + 1 :])


def test_no_duty_never_opens_the_valve():
    assert not any(run(flat(), 0.0, 12))


def test_an_open_valve_closes_once_the_demand_is_gone():
    states = run(flat(), -1.0, 1, start_open=True)
    held = int(MIN_RUN / STEP)
    assert all(states[:held])
    assert not any(states[held:])


def test_an_open_valve_is_not_closed_before_the_minimum_run():
    controller = flat()
    wanted = controller.update(
        error=-1.0, now=0.0, is_open=True, since_switch=MIN_RUN - 1,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    wanted_later = controller.update(
        error=-1.0, now=STEP, is_open=True, since_switch=MIN_RUN - 1 + STEP,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    assert wanted is True
    assert wanted_later is False


def test_a_closed_valve_is_not_opened_before_the_minimum_off():
    controller = flat()
    for i in range(400):
        wanted = controller.update(
            error=5.0, now=i * STEP, is_open=False, since_switch=MIN_OFF - 1,
            min_run=MIN_RUN, min_off=MIN_OFF,
        )
        assert wanted is False


def test_a_valve_held_shut_by_a_guard_still_opens_afterwards():
    controller = flat()
    for i in range(25):
        controller.update(
            error=5.0, now=i * STEP, is_open=False, since_switch=0.0,
            min_run=MIN_RUN, min_off=MIN_OFF,
        )
    wanted = controller.update(
        error=5.0, now=25 * STEP, is_open=False, since_switch=MIN_OFF,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    assert wanted is True


def test_timing_follows_the_real_clock_not_the_call_count():
    # Calls every second, as when the sensor and the relay keep reporting.
    controller = flat()
    is_open = False
    last_switch = -1e9
    open_seconds = 0
    for now in range(0, 24 * 3600):
        wanted = controller.update(
            error=1.0, now=float(now), is_open=is_open,
            since_switch=now - last_switch, min_run=MIN_RUN, min_off=MIN_OFF,
        )
        if wanted != is_open:
            is_open, last_switch = wanted, now
        open_seconds += is_open
    assert open_seconds / (24 * 3600) == pytest.approx(0.5, abs=0.05)


def test_a_valve_found_open_with_the_room_far_below_stays_open():
    # After a restart: the controller has no pulse in hand, the valve is open.
    states = run(flat(), 5.0, 3, start_open=True)

    assert all(states)


def test_a_valve_found_open_is_given_a_full_pulse_to_finish():
    states = run(flat(), 1.0, 4, start_open=True)
    first_pulse = next(seconds for state, seconds in runs_of([False] + states) if state)

    # Half duty on a 60 minute cycle: a pulse of about half an hour.
    assert 0.8 * 1800 <= first_pulse <= 1.2 * 1800


def test_a_valve_found_open_with_no_demand_still_closes():
    states = run(flat(), -1.0, 1, start_open=True)

    assert not states[-1]


# ---------------------------------------------------------------------------
# Pause and reset
# ---------------------------------------------------------------------------
def test_hold_clears_the_duty_and_keeps_what_was_learned():
    controller = ProportionalController(HOUR)
    run(controller, 0.5, 6)
    learned = controller.integral
    assert learned > 0 and controller.duty > 0

    controller.hold()

    assert controller.duty == 0.0
    assert controller.integral == learned


def test_reset_forgets_what_was_learned():
    controller = ProportionalController(HOUR)
    run(controller, 0.5, 6)

    controller.reset()

    assert controller.duty == 0.0
    assert controller.integral == 0.0


def test_the_time_spent_on_hold_is_not_integrated():
    controller = ProportionalController(HOUR)
    controller.update(
        error=1.0, now=0.0, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    controller.hold()
    controller.update(
        error=1.0, now=5 * HOUR, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    assert controller.integral == 0.0


def test_the_pulse_collected_before_a_hold_is_dropped():
    controller = flat()
    run(controller, 1.0, 0.2)
    controller.hold()
    wanted = controller.update(
        error=1.0, now=1e6, is_open=False, since_switch=1e9,
        min_run=MIN_RUN, min_off=MIN_OFF,
    )
    assert wanted is False
