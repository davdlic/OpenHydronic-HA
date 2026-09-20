# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Control coordinator: owns every decision, entities are thin views on it.

    sensors -> demand (hysteresis) -> cycle guards -> zone outputs
                                  \\-> master state machine -> bypass fallback

Timers are re-derived on every pass, so a missed tick only delays the next
decision by one interval.
"""

from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass, field
from typing import Any

from homeassistant.components import persistent_notification
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    ATTR_ENTITY_ID,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    STATE_ON,
    STATE_UNAVAILABLE,
    STATE_UNKNOWN,
)
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.helpers.event import (
    async_track_state_change_event,
    async_track_time_change,
)
from homeassistant.helpers.storage import Store
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import dt as dt_util

from .const import (
    ATTR_CYCLES,
    ATTR_DEMAND,
    ATTR_FAULT,
    ATTR_IS_BYPASS,
    ATTR_LOCKED_UNTIL,
    ATTR_RELAY_ENTITY,
    ATTR_RUNTIME_HOURS,
    ATTR_SENSOR_ENTITY,
    ATTR_VALVE_STATE,
    CONF_AIR_PURGE_DURATION,
    CONF_ANTI_SEIZE_DURATION,
    CONF_ANTI_SEIZE_ENABLED,
    CONF_ANTI_SEIZE_HOUR,
    CONF_ANTI_SEIZE_MINUTE,
    CONF_ANTI_SEIZE_WEEKDAY,
    CONF_AWAY_TEMP,
    CONF_COMFORT_TEMP,
    CONF_ECO_TEMP,
    CONF_HEAT_PURGE_DELAY,
    CONF_HYSTERESIS,
    CONF_IS_BYPASS,
    CONF_MASTER_ENTITY,
    CONF_MASTER_MODE,
    CONF_MASTER_START_DELAY,
    CONF_MIN_OFF_TIME,
    CONF_MIN_RUN_TIME,
    CONF_RELAY_ENTITY,
    CONF_SENSOR_ENTITY,
    CONF_SENSOR_TIMEOUT,
    CONF_ZONE_ID,
    CONF_ZONE_NAME,
    CONF_ZONES,
    DEFAULT_AIR_PURGE_DURATION,
    DEFAULT_ANTI_SEIZE_DURATION,
    DEFAULT_ANTI_SEIZE_HOUR,
    DEFAULT_ANTI_SEIZE_MINUTE,
    DEFAULT_ANTI_SEIZE_WEEKDAY,
    DEFAULT_AWAY_TEMP,
    DEFAULT_COMFORT_TEMP,
    DEFAULT_ECO_TEMP,
    DEFAULT_HEAT_PURGE_DELAY,
    DEFAULT_HYSTERESIS,
    DEFAULT_MASTER_START_DELAY,
    DEFAULT_MIN_OFF_TIME,
    DEFAULT_MIN_RUN_TIME,
    DEFAULT_SENSOR_TIMEOUT,
    DOMAIN,
    FAULT_RELAY_MISSING,
    FAULT_SENSOR_MISSING,
    FAULT_SENSOR_STALE,
    MASTER_DISABLED,
    MASTER_EXTERNAL,
    MASTER_RELAY,
    MASTER_STATE_DISABLED,
    MASTER_STATE_OFF,
    MASTER_STATE_ON,
    MASTER_STATE_PURGING,
    MASTER_STATE_WAITING,
    STORAGE_KEY,
    STORAGE_VERSION,
    SYSTEM_MODE_AIR_PURGE,
    SYSTEM_MODE_ANTI_SEIZE,
    SYSTEM_MODE_HOLIDAY,
    SYSTEM_MODE_NORMAL,
    SYSTEM_MODE_SUMMER,
    UPDATE_INTERVAL,
    VALVE_CLOSED,
    VALVE_FAULT,
    VALVE_OPEN,
    VALVE_OPENING,
)
from .firmware import FirmwareBridge

_LOGGER = logging.getLogger(__name__)

PRESET_COMFORT = "comfort"
PRESET_ECO = "eco"
PRESET_AWAY = "away"
PRESET_NONE = "none"

HVAC_HEAT = "heat"
HVAC_OFF = "off"

# Age given to the cycle guards when there is no stored timestamp, so a fresh
# install never starts with every zone locked. Mirrors the firmware on boot.
COLD_START_AGE = 3600.0

NOTIFY_TITLE = {
    "en": "OpenHydronic - zone alert",
    "pt": "OpenHydronic - alerta de zona",
}

NOTIFY_TEXT = {
    "en": {
        FAULT_SENSOR_STALE: (
            "The temperature sensor of zone {zone} ({entity}) has not updated for "
            "more than {hours} h. The zone relay was switched off for safety."
        ),
        FAULT_SENSOR_MISSING: (
            "The sensor of zone {zone} ({entity}) is unavailable. The zone relay "
            "was switched off for safety."
        ),
        FAULT_RELAY_MISSING: (
            "The relay of zone {zone} ({entity}) is unavailable. Check the "
            "connection to the OpenHydronic board."
        ),
    },
    "pt": {
        FAULT_SENSOR_STALE: (
            "O sensor de temperatura da zona {zone} ({entity}) nao atualiza ha mais "
            "de {hours} h. O rele da zona foi desligado por seguranca."
        ),
        FAULT_SENSOR_MISSING: (
            "O sensor da zona {zone} ({entity}) esta indisponivel. O rele da zona "
            "foi desligado por seguranca."
        ),
        FAULT_RELAY_MISSING: (
            "O rele da zona {zone} ({entity}) esta indisponivel. Verifique a ligacao "
            "a placa OpenHydronic."
        ),
    },
}


@dataclass
class ZoneRuntime:
    """Live state of a single hydraulic zone."""

    zone_id: str
    name: str
    relay_entity: str
    sensor_entity: str | None
    is_bypass: bool
    comfort_temp: float
    eco_temp: float
    away_temp: float

    # User intent (persisted)
    hvac_mode: str = HVAC_HEAT
    preset: str = PRESET_COMFORT
    manual_target: float | None = None

    # Measured
    current_temp: float | None = None
    sensor_age: float | None = None
    relay_on: bool = False
    fault: str | None = None

    # Control
    demand: bool = False
    output: bool = False
    last_switch_at: float = field(
        default_factory=lambda: time.monotonic() - COLD_START_AGE
    )
    last_seen_on: bool = False
    # False until the first pass adopts the relay's real state.
    synced: bool = False

    # Metrics (persisted)
    runtime_seconds: float = 0.0
    cycles: int = 0

    @property
    def target_temp(self) -> float:
        """Setpoint currently in force for this zone."""
        if self.preset == PRESET_COMFORT:
            return self.comfort_temp
        if self.preset == PRESET_ECO:
            return self.eco_temp
        if self.preset == PRESET_AWAY:
            return self.away_temp
        return self.manual_target if self.manual_target is not None else self.comfort_temp


def _restore_switch_time(saved: dict[str, Any]) -> float:
    """Rebuilds the cycle-guard clock of a zone across a restart."""
    # Stored as wall clock: monotonic restarts with the process.
    epoch = saved.get("last_switch_epoch")
    if not epoch:
        return time.monotonic() - COLD_START_AGE
    elapsed = time.time() - float(epoch)
    if elapsed < 0:  # clock moved backwards
        elapsed = COLD_START_AGE
    return time.monotonic() - elapsed


class OpenHydronicCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Own the hydraulic state machine for one OpenHydronic board."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=UPDATE_INTERVAL,
        )
        self.entry = entry
        self.zones: dict[str, ZoneRuntime] = {}
        self.firmware = FirmwareBridge(hass, entry)

        self._store: Store[dict[str, Any]] = Store(
            hass, STORAGE_VERSION, f"{STORAGE_KEY}_{entry.entry_id}"
        )
        self._persisted: dict[str, Any] = {}
        self._unsub: list[Any] = []

        # System modes
        self.summer_mode: bool = False
        self.holiday_mode: bool = False
        self._air_purge_until: float | None = None
        self._anti_seize_until: float | None = None

        # Master state machine
        self.master_state: str = MASTER_STATE_DISABLED
        self._demand_started_at: float | None = None
        self._demand_ended_at: float | None = None
        self._master_output: bool = False

        self._notified_faults: set[str] = set()
        self._last_metrics_tick: float = time.monotonic()

    # ------------------------------------------------------------------
    # Options helpers
    # ------------------------------------------------------------------
    def _opt(self, key: str, default: Any) -> Any:
        return self.entry.options.get(key, default)

    @property
    def hysteresis(self) -> float:
        return float(self._opt(CONF_HYSTERESIS, DEFAULT_HYSTERESIS))

    @property
    def master_mode(self) -> str:
        return str(self._opt(CONF_MASTER_MODE, MASTER_DISABLED))

    @property
    def master_entity(self) -> str | None:
        entity = self._opt(CONF_MASTER_ENTITY, None)
        if self.master_mode in (MASTER_RELAY, MASTER_EXTERNAL) and entity:
            return str(entity)
        return None

    @property
    def master_start_delay(self) -> int:
        return int(self._opt(CONF_MASTER_START_DELAY, DEFAULT_MASTER_START_DELAY))

    @property
    def heat_purge_delay(self) -> int:
        return int(self._opt(CONF_HEAT_PURGE_DELAY, DEFAULT_HEAT_PURGE_DELAY))

    @property
    def min_run_time(self) -> int:
        return int(self._opt(CONF_MIN_RUN_TIME, DEFAULT_MIN_RUN_TIME))

    @property
    def min_off_time(self) -> int:
        return int(self._opt(CONF_MIN_OFF_TIME, DEFAULT_MIN_OFF_TIME))

    @property
    def sensor_timeout(self) -> int:
        return int(self._opt(CONF_SENSOR_TIMEOUT, DEFAULT_SENSOR_TIMEOUT))

    @property
    def air_purge_duration(self) -> int:
        return int(self._opt(CONF_AIR_PURGE_DURATION, DEFAULT_AIR_PURGE_DURATION))

    @property
    def system_mode(self) -> str:
        if self._air_purge_until is not None:
            return SYSTEM_MODE_AIR_PURGE
        if self._anti_seize_until is not None:
            return SYSTEM_MODE_ANTI_SEIZE
        if self.summer_mode:
            return SYSTEM_MODE_SUMMER
        if self.holiday_mode:
            return SYSTEM_MODE_HOLIDAY
        return SYSTEM_MODE_NORMAL

    @property
    def air_purge_active(self) -> bool:
        return self._air_purge_until is not None

    @property
    def bypass_zone(self) -> ZoneRuntime | None:
        return next((z for z in self.zones.values() if z.is_bypass), None)

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------
    async def async_setup(self) -> None:
        """Restore persisted state, build zones and wire up listeners."""
        self._persisted = await self._store.async_load() or {}
        self.summer_mode = bool(self._persisted.get("summer_mode", False))
        self.holiday_mode = bool(self._persisted.get("holiday_mode", False))

        self._build_zones()
        self._register_listeners()

    def _build_zones(self) -> None:
        """(Re)build zone runtimes from the options, keeping persisted state."""
        stored_zones: dict[str, Any] = self._persisted.get("zones", {})
        zones: dict[str, ZoneRuntime] = {}

        for raw in self.entry.options.get(CONF_ZONES, []):
            zone_id = raw.get(CONF_ZONE_ID) or uuid.uuid4().hex[:8]
            saved = stored_zones.get(zone_id, {})
            zones[zone_id] = ZoneRuntime(
                zone_id=zone_id,
                name=raw.get(CONF_ZONE_NAME, f"Zone {zone_id}"),
                relay_entity=raw[CONF_RELAY_ENTITY],
                sensor_entity=raw.get(CONF_SENSOR_ENTITY),
                is_bypass=bool(raw.get(CONF_IS_BYPASS, False)),
                comfort_temp=float(raw.get(CONF_COMFORT_TEMP, DEFAULT_COMFORT_TEMP)),
                eco_temp=float(raw.get(CONF_ECO_TEMP, DEFAULT_ECO_TEMP)),
                away_temp=float(raw.get(CONF_AWAY_TEMP, DEFAULT_AWAY_TEMP)),
                hvac_mode=saved.get("hvac_mode", HVAC_HEAT),
                preset=saved.get("preset", PRESET_COMFORT),
                manual_target=saved.get("manual_target"),
                runtime_seconds=float(saved.get("runtime_seconds", 0.0)),
                cycles=int(saved.get("cycles", 0)),
                last_switch_at=_restore_switch_time(saved),
            )

        self.zones = zones

    def _register_listeners(self) -> None:
        """Local-push: react to relay/sensor changes instead of only polling."""
        self._async_clear_listeners()

        tracked: list[str] = []
        for zone in self.zones.values():
            tracked.append(zone.relay_entity)
            if zone.sensor_entity:
                tracked.append(zone.sensor_entity)
        if self.master_entity:
            tracked.append(self.master_entity)

        if tracked:
            self._unsub.append(
                async_track_state_change_event(
                    self.hass, sorted(set(tracked)), self._handle_source_event
                )
            )

        if self._opt(CONF_ANTI_SEIZE_ENABLED, True):
            self._unsub.append(
                async_track_time_change(
                    self.hass,
                    self._handle_anti_seize_trigger,
                    hour=int(self._opt(CONF_ANTI_SEIZE_HOUR, DEFAULT_ANTI_SEIZE_HOUR)),
                    minute=int(
                        self._opt(CONF_ANTI_SEIZE_MINUTE, DEFAULT_ANTI_SEIZE_MINUTE)
                    ),
                    second=0,
                )
            )

    @callback
    def _async_clear_listeners(self) -> None:
        while self._unsub:
            self._unsub.pop()()

    async def async_shutdown_coordinator(self) -> None:
        """Persist metrics and drop listeners on unload."""
        self._async_clear_listeners()
        await self._async_save()

    @callback
    def _handle_source_event(self, event: Event) -> None:
        """A relay or sensor moved: re-run the loop without waiting for the tick."""
        self.hass.async_create_task(self.async_request_refresh())

    @callback
    def _handle_anti_seize_trigger(self, now: Any) -> None:
        weekday = int(self._opt(CONF_ANTI_SEIZE_WEEKDAY, DEFAULT_ANTI_SEIZE_WEEKDAY))
        if dt_util.as_local(now).weekday() != weekday:
            return
        _LOGGER.info("Starting scheduled anti-seize routine")
        self.hass.async_create_task(self.async_run_anti_seize())

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------
    async def _async_update_data(self) -> dict[str, Any]:
        await self._async_control()
        return self._build_snapshot()

    async def _async_control(self) -> None:
        now = time.monotonic()

        self._expire_timed_modes(now)
        for zone in self.zones.values():
            self._read_zone_inputs(zone)

        self._accumulate_metrics(now)
        demand = self._evaluate_demand()
        outputs = self._apply_cycle_guards(demand, now)
        master_output = self._resolve_master(demand, now)
        outputs = self._apply_bypass(outputs, master_output)

        await self._commit_outputs(outputs, master_output, now)

    def _expire_timed_modes(self, now: float) -> None:
        if self._air_purge_until is not None and now >= self._air_purge_until:
            _LOGGER.info("Air purge finished")
            self._air_purge_until = None
        if self._anti_seize_until is not None and now >= self._anti_seize_until:
            _LOGGER.info("Anti-seize routine finished")
            self._anti_seize_until = None

    def _read_zone_inputs(self, zone: ZoneRuntime) -> None:
        """Refresh measured values and raise/clear the sensor watchdog fault."""
        relay_state = self.hass.states.get(zone.relay_entity)
        if relay_state is None or relay_state.state == STATE_UNAVAILABLE:
            zone.relay_on = False
            zone.fault = FAULT_RELAY_MISSING
            self._notify_fault(zone, FAULT_RELAY_MISSING)
            return
        zone.relay_on = relay_state.state == STATE_ON

        if not zone.synced:
            # Adopt the relay after a restart: a zone that is heating stays on
            # and no phantom cycle is counted.
            zone.output = zone.relay_on
            zone.last_seen_on = zone.relay_on
            zone.synced = True

        if not zone.sensor_entity:
            # Bypass loops legitimately have no room sensor.
            zone.current_temp = None
            zone.sensor_age = None
            if zone.is_bypass:
                self._clear_fault(zone)
                zone.fault = None
            else:
                zone.fault = FAULT_SENSOR_MISSING
                self._notify_fault(zone, FAULT_SENSOR_MISSING)
            return

        sensor_state = self.hass.states.get(zone.sensor_entity)
        if sensor_state is None or sensor_state.state in (
            STATE_UNAVAILABLE,
            STATE_UNKNOWN,
        ):
            zone.current_temp = None
            zone.sensor_age = None
            zone.fault = FAULT_SENSOR_MISSING
            self._notify_fault(zone, FAULT_SENSOR_MISSING)
            return

        try:
            zone.current_temp = float(sensor_state.state)
        except (TypeError, ValueError):
            zone.current_temp = None
            zone.fault = FAULT_SENSOR_MISSING
            self._notify_fault(zone, FAULT_SENSOR_MISSING)
            return

        zone.sensor_age = (dt_util.utcnow() - sensor_state.last_updated).total_seconds()

        if zone.sensor_age > self.sensor_timeout:
            zone.fault = FAULT_SENSOR_STALE
            self._notify_fault(zone, FAULT_SENSOR_STALE)
        else:
            self._clear_fault(zone)
            zone.fault = None

    def _evaluate_demand(self) -> dict[str, bool]:
        """Hysteresis band, plus every override that can veto heat."""
        hyst = self.hysteresis
        mode = self.system_mode
        demand: dict[str, bool] = {}

        for zone_id, zone in self.zones.items():
            if mode in (SYSTEM_MODE_AIR_PURGE, SYSTEM_MODE_ANTI_SEIZE):
                zone.demand = True
                demand[zone_id] = True
                continue

            if mode == SYSTEM_MODE_SUMMER or zone.hvac_mode == HVAC_OFF:
                zone.demand = False
                demand[zone_id] = False
                continue

            if zone.fault is not None or zone.current_temp is None or zone.is_bypass:
                # Never heat what we cannot measure; a bypass makes no demand.
                zone.demand = False
                demand[zone_id] = False
                continue

            target = zone.away_temp if mode == SYSTEM_MODE_HOLIDAY else zone.target_temp
            if zone.demand:
                zone.demand = zone.current_temp < target + hyst
            else:
                zone.demand = zone.current_temp < target - hyst
            demand[zone_id] = zone.demand

        return demand

    def _apply_cycle_guards(
        self, demand: dict[str, bool], now: float
    ) -> dict[str, bool]:
        """Enforce min ON / min OFF so the PTC actuators are not hammered."""
        # A faulted zone is released at once; purge and anti-seize ignore the lock.
        outputs: dict[str, bool] = {}
        forced = self.system_mode in (SYSTEM_MODE_AIR_PURGE, SYSTEM_MODE_ANTI_SEIZE)

        for zone_id, zone in self.zones.items():
            wanted = demand.get(zone_id, False)
            elapsed = now - zone.last_switch_at

            if forced:
                outputs[zone_id] = wanted
                continue

            if zone.fault is not None:
                outputs[zone_id] = False
                continue

            if wanted and not zone.output and elapsed < self.min_off_time:
                outputs[zone_id] = False  # still inside the min-OFF lock
            elif not wanted and zone.output and elapsed < self.min_run_time:
                outputs[zone_id] = True  # still inside the min-RUN lock
            else:
                outputs[zone_id] = wanted

        return outputs

    def _resolve_master(self, demand: dict[str, bool], now: float) -> bool:
        """Thermal delay on start, residual heat purge on stop."""
        if self.master_mode == MASTER_DISABLED or not self.master_entity:
            self.master_state = MASTER_STATE_DISABLED
            self._master_output = False
            return False

        any_demand = any(demand.values())

        if self.system_mode in (SYSTEM_MODE_AIR_PURGE, SYSTEM_MODE_ANTI_SEIZE):
            # Purge needs the circulator right away, no thermal delay.
            self._demand_started_at = self._demand_started_at or now
            self._demand_ended_at = None
            self.master_state = MASTER_STATE_ON
            self._master_output = True
            return True

        if any_demand:
            self._demand_ended_at = None
            if self._demand_started_at is None:
                self._demand_started_at = now

            if self._master_output:
                self.master_state = MASTER_STATE_ON
                return True

            if now - self._demand_started_at >= self.master_start_delay:
                self.master_state = MASTER_STATE_ON
                self._master_output = True
                return True

            self.master_state = MASTER_STATE_WAITING
            self._master_output = False
            return False

        # No demand left anywhere.
        self._demand_started_at = None
        if self._master_output:
            if self._demand_ended_at is None:
                self._demand_ended_at = now
            if now - self._demand_ended_at < self.heat_purge_delay:
                self.master_state = MASTER_STATE_PURGING
                return True
            self._master_output = False

        self._demand_ended_at = None
        self.master_state = MASTER_STATE_OFF
        return False

    def _apply_bypass(
        self, outputs: dict[str, bool], master_output: bool
    ) -> dict[str, bool]:
        """Never let the circulator run against a fully closed circuit."""
        bypass = self.bypass_zone
        if bypass is None:
            return outputs

        circuit_open = any(
            state for zone_id, state in outputs.items() if zone_id != bypass.zone_id
        )
        pump_running = master_output or self.master_state in (
            MASTER_STATE_WAITING,
            MASTER_STATE_PURGING,
        )
        outputs[bypass.zone_id] = pump_running and not circuit_open
        return outputs

    async def _commit_outputs(
        self, outputs: dict[str, bool], master_output: bool, now: float
    ) -> None:
        for zone_id, wanted in outputs.items():
            zone = self.zones[zone_id]
            if wanted != zone.output:
                zone.output = wanted
                zone.last_switch_at = now
            if wanted != zone.relay_on:
                await self._async_switch(zone.relay_entity, wanted)

        if self.master_entity:
            master_state = self.hass.states.get(self.master_entity)
            is_on = master_state is not None and master_state.state == STATE_ON
            if master_output != is_on:
                await self._async_switch(self.master_entity, master_output)

    async def _async_switch(self, entity_id: str, turn_on: bool) -> None:
        """Domain-agnostic on/off so relays may live in switch/light/input_boolean."""
        try:
            await self.hass.services.async_call(
                "homeassistant",
                SERVICE_TURN_ON if turn_on else SERVICE_TURN_OFF,
                {ATTR_ENTITY_ID: entity_id},
                blocking=False,
            )
        except Exception:  # noqa: BLE001 - one dead relay must not stall the loop
            _LOGGER.exception("Failed to switch %s", entity_id)

    def _accumulate_metrics(self, now: float) -> None:
        elapsed = now - self._last_metrics_tick
        self._last_metrics_tick = now
        if elapsed <= 0:
            return

        for zone in self.zones.values():
            if zone.relay_on:
                zone.runtime_seconds += elapsed
                if not zone.last_seen_on:
                    zone.cycles += 1
            zone.last_seen_on = zone.relay_on

        self._schedule_save()

    # ------------------------------------------------------------------
    # Fault notifications
    # ------------------------------------------------------------------
    def _notify_fault(self, zone: ZoneRuntime, fault: str) -> None:
        key = f"{zone.zone_id}:{fault}"
        if key in self._notified_faults:
            return
        self._notified_faults.add(key)

        lang = (self.hass.config.language or "en")[:2]
        texts = NOTIFY_TEXT.get(lang, NOTIFY_TEXT["en"])
        entity = (
            zone.relay_entity
            if fault == FAULT_RELAY_MISSING
            else zone.sensor_entity
        )

        persistent_notification.async_create(
            self.hass,
            texts[fault].format(
                zone=zone.name,
                entity=entity,
                hours=max(1, self.sensor_timeout // 3600),
            ),
            title=NOTIFY_TITLE.get(lang, NOTIFY_TITLE["en"]),
            notification_id=f"{DOMAIN}_{self.entry.entry_id}_{key}",
        )

    def _clear_fault(self, zone: ZoneRuntime) -> None:
        for fault in (FAULT_SENSOR_STALE, FAULT_SENSOR_MISSING, FAULT_RELAY_MISSING):
            key = f"{zone.zone_id}:{fault}"
            if key in self._notified_faults:
                self._notified_faults.discard(key)
                persistent_notification.async_dismiss(
                    self.hass, f"{DOMAIN}_{self.entry.entry_id}_{key}"
                )

    # ------------------------------------------------------------------
    # Snapshot consumed by the entities and by the Lovelace card
    # ------------------------------------------------------------------
    def _valve_state(self, zone: ZoneRuntime) -> str:
        if zone.fault is not None:
            return VALVE_FAULT
        if not zone.output:
            return VALVE_CLOSED
        # "Opening" covers both the PTC travel time and the master thermal delay.
        if self.master_state == MASTER_STATE_WAITING or (
            time.monotonic() - zone.last_switch_at < self.master_start_delay
        ):
            return VALVE_OPENING
        return VALVE_OPEN

    def _build_snapshot(self) -> dict[str, Any]:
        now = time.monotonic()
        zones: dict[str, dict[str, Any]] = {}

        for zone_id, zone in self.zones.items():
            elapsed = now - zone.last_switch_at
            lock = self.min_run_time if zone.output else self.min_off_time
            zones[zone_id] = {
                "zone_id": zone_id,
                "name": zone.name,
                ATTR_RELAY_ENTITY: zone.relay_entity,
                ATTR_SENSOR_ENTITY: zone.sensor_entity,
                ATTR_IS_BYPASS: zone.is_bypass,
                "current_temp": zone.current_temp,
                "target_temp": zone.target_temp,
                "hvac_mode": zone.hvac_mode,
                "preset": zone.preset,
                ATTR_DEMAND: zone.demand,
                "output": zone.output,
                "relay_on": zone.relay_on,
                ATTR_VALVE_STATE: self._valve_state(zone),
                ATTR_FAULT: zone.fault,
                ATTR_LOCKED_UNTIL: max(0, int(lock - elapsed)),
                ATTR_RUNTIME_HOURS: round(zone.runtime_seconds / 3600, 2),
                ATTR_CYCLES: zone.cycles,
            }

        return {
            "zones": zones,
            "system_mode": self.system_mode,
            "master_state": self.master_state,
            "master_entity": self.master_entity,
            "summer_mode": self.summer_mode,
            "holiday_mode": self.holiday_mode,
            "air_purge_active": self.air_purge_active,
            "air_purge_remaining": (
                max(0, int(self._air_purge_until - now))
                if self._air_purge_until is not None
                else 0
            ),
            "active_zones": sum(1 for z in self.zones.values() if z.relay_on),
        }

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------
    @callback
    def _schedule_save(self) -> None:
        self._store.async_delay_save(self._data_to_save, 60)

    @callback
    def _data_to_save(self) -> dict[str, Any]:
        return {
            "summer_mode": self.summer_mode,
            "holiday_mode": self.holiday_mode,
            "zones": {
                zone_id: {
                    "hvac_mode": zone.hvac_mode,
                    "preset": zone.preset,
                    "manual_target": zone.manual_target,
                    "runtime_seconds": round(zone.runtime_seconds, 1),
                    "cycles": zone.cycles,
                    # Wall clock, so the cycle guards survive a restart.
                    "last_switch_epoch": round(
                        time.time() - (time.monotonic() - zone.last_switch_at), 1
                    ),
                }
                for zone_id, zone in self.zones.items()
            },
        }

    async def _async_save(self) -> None:
        await self._store.async_save(self._data_to_save())

    # ------------------------------------------------------------------
    # Public commands (called by entities and by the services)
    # ------------------------------------------------------------------
    async def async_set_zone_hvac_mode(self, zone_id: str, hvac_mode: str) -> None:
        self.zones[zone_id].hvac_mode = hvac_mode
        await self._async_save()
        await self.async_request_refresh()

    async def async_set_zone_preset(self, zone_id: str, preset: str) -> None:
        zone = self.zones[zone_id]
        zone.preset = preset
        if preset != PRESET_NONE:
            zone.manual_target = None
        await self._async_save()
        await self.async_request_refresh()

    async def async_set_zone_temperature(
        self, zone_id: str, temperature: float
    ) -> None:
        zone = self.zones[zone_id]
        zone.manual_target = float(temperature)
        zone.preset = PRESET_NONE
        await self._async_save()
        await self.async_request_refresh()

    async def async_set_summer_mode(self, enabled: bool) -> None:
        self.summer_mode = bool(enabled)
        await self._async_save()
        await self.async_request_refresh()

    async def async_set_holiday_mode(self, enabled: bool) -> None:
        self.holiday_mode = bool(enabled)
        await self._async_save()
        await self.async_request_refresh()

    async def async_start_air_purge(self, duration: int | None = None) -> None:
        seconds = int(duration or self.air_purge_duration)
        # Run it on the board when possible: it then survives a HA restart.
        on_board = await self.firmware.async_start_air_purge(duration)
        self._air_purge_until = time.monotonic() + seconds
        _LOGGER.info(
            "Air purge started for %s s (%s)",
            seconds,
            "board" if on_board else "Home Assistant",
        )
        await self.async_request_refresh()

    async def async_stop_air_purge(self) -> None:
        await self.firmware.async_stop_air_purge()
        self._air_purge_until = None
        await self.async_request_refresh()

    async def async_run_anti_seize(self, duration: int | None = None) -> None:
        seconds = int(
            duration
            or self._opt(CONF_ANTI_SEIZE_DURATION, DEFAULT_ANTI_SEIZE_DURATION)
        )
        await self.firmware.async_run_anti_seize()
        self._anti_seize_until = time.monotonic() + seconds
        await self.async_request_refresh()

    async def async_emergency_stop(self) -> None:
        """Closes every valve now, ignoring the cycle guards."""
        await self.firmware.async_emergency_stop()

        now = time.monotonic()
        self._air_purge_until = None
        self._anti_seize_until = None
        self._demand_started_at = None
        self._demand_ended_at = None
        self._master_output = False

        for zone in self.zones.values():
            zone.demand = False
            zone.output = False
            # Re-arm the min-OFF lock, like the board does on an emergency stop.
            zone.last_switch_at = now
            await self._async_switch(zone.relay_entity, False)

        if self.master_entity:
            await self._async_switch(self.master_entity, False)

        _LOGGER.warning("Emergency stop: all zones closed")
        await self._async_save()
        await self.async_request_refresh()

    async def async_reset_metrics(self) -> None:
        for zone in self.zones.values():
            zone.runtime_seconds = 0.0
            zone.cycles = 0
        await self._async_save()
        await self.async_request_refresh()
