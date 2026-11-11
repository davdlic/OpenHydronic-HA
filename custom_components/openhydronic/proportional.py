# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Time-proportional control of one valve.

A floor answers in hours, so switching the valve at a temperature threshold
overshoots and then lets the slab cool. Instead the controller works out a duty
(the share of the time the valve should be open) from how far the room is from
its target, and turns that duty into open/close pulses that respect the
minimum run and minimum off times of the actuator.

It knows nothing about Home Assistant: the coordinator feeds it the error and
the clock and gets back whether the valve should be open.
"""

from __future__ import annotations

from .const import PROPORTIONAL_KP, PROPORTIONAL_TI

# A longer gap between two calls (a stall, a restart) counts as this much.
MAX_STEP = 60.0


def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


class ProportionalController:
    """Duty from the error and a slow integral; pulses from the duty."""

    def __init__(
        self,
        period: float,
        *,
        kp: float = PROPORTIONAL_KP,
        ti: float = PROPORTIONAL_TI,
        integral: float = 0.0,
    ) -> None:
        self.period = float(period)
        self.kp = kp
        self.ti = ti
        # The share of the duty the floor needs at steady state, learned slowly.
        self.integral = _clamp(float(integral))
        self.duty = 0.0
        # Duty collected towards the next pulse (and spent while it runs).
        self._pulse = 0.0
        self._last: float | None = None

    def hold(self) -> None:
        """Pause: the zone is not being regulated (fault, purge, no reading)."""
        self.duty = 0.0
        self._pulse = 0.0
        self._last = None

    def reset(self) -> None:
        """Forget what was learned: the zone was switched off on purpose."""
        self.hold()
        self.integral = 0.0

    def update(
        self,
        *,
        error: float,
        now: float,
        is_open: bool,
        since_switch: float,
        min_run: float,
        min_off: float,
    ) -> bool:
        """Return whether the valve should be open.

        error: target minus room temperature, in degrees.
        now: a monotonic clock, in seconds.
        is_open / since_switch: the valve as it really is, and for how long.
        """
        resuming = self._last is None
        dt = 0.0 if resuming else min(max(now - self._last, 0.0), MAX_STEP)
        self._last = now

        # The integral stops growing while the duty is already at a limit.
        raw = self.kp * error + self.integral
        if not ((raw >= 1.0 and error > 0) or (raw <= 0.0 and error < 0)):
            self.integral = _clamp(self.integral + self.kp / self.ti * error * dt)
        duty = _clamp(self.kp * error + self.integral)
        self.duty = duty

        # A pulse needs at least the actuator's minimum run, and the gap before
        # the next at least its minimum off, whatever the duty.
        threshold = max(
            duty * (1.0 - duty) * self.period,
            min_run * (1.0 - duty),
            min_off * duty,
        )
        if not is_open:
            self._pulse = 0.0 if duty <= 0 else min(self._pulse + duty * dt, self.period)
            return duty > 0 and self._pulse >= threshold and since_switch >= min_off

        if resuming and self._pulse <= 0:
            # Found open after a restart or a purge: carry on as if a pulse had
            # just begun, rather than closing a valve the room still needs.
            self._pulse = threshold
        self._pulse = min(self._pulse + (duty - 1.0) * dt, self.period)
        if since_switch >= min_run and (self._pulse <= 0 or duty <= 0):
            self._pulse = 0.0
            return False
        return True
