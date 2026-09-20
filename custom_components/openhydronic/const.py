# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Constants for the OpenHydronic integration.

The integration is a *supervisor* layer: the ESP32 board itself is exposed to
Home Assistant through the standard ESPHome integration (native API), and
OpenHydronic binds those relay switches to arbitrary temperature sensors,
adding hysteresis control, master/circulator management and hydraulic
protections on top of them.
"""

from __future__ import annotations

from datetime import timedelta
from typing import Final

DOMAIN: Final = "openhydronic"
MANUFACTURER: Final = "OpenHydronic"
MODEL: Final = "ESP32 Hydronic Controller"
INTEGRATION_VERSION: Final = "1.0.0"

PLATFORMS: Final[list[str]] = ["climate", "sensor", "switch"]

# Control loop. The coordinator is also state-change driven (local push), the
# interval is only the safety heartbeat that lets timers expire deterministically.
UPDATE_INTERVAL: Final = timedelta(seconds=15)
STORAGE_VERSION: Final = 1
STORAGE_KEY: Final = f"{DOMAIN}.metrics"

# Frontend
URL_BASE: Final = "/openhydronic_frontend"
CARD_FILENAME: Final = "openhydronic-card.js"

# --------------------------------------------------------------------------
# Config entry data keys
# --------------------------------------------------------------------------
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_MAC: Final = "mac"
CONF_DEVICE_NAME: Final = "device_name"
CONF_FW_VERSION: Final = "fw_version"
# ESPHome node slug (``openhydronic-a1b2c3``). Used to address the firmware's
# own API actions as ``esphome.<node>_<action>``; see firmware.py.
CONF_NODE_NAME: Final = "node_name"

# --------------------------------------------------------------------------
# Options keys
# --------------------------------------------------------------------------
CONF_ZONES: Final = "zones"
CONF_ZONE_ID: Final = "zone_id"
CONF_ZONE_NAME: Final = "name"
CONF_RELAY_ENTITY: Final = "relay_entity"
CONF_SENSOR_ENTITY: Final = "sensor_entity"
CONF_IS_BYPASS: Final = "is_bypass"
CONF_COMFORT_TEMP: Final = "comfort_temp"
CONF_ECO_TEMP: Final = "eco_temp"
CONF_AWAY_TEMP: Final = "away_temp"

CONF_MASTER_MODE: Final = "master_mode"
CONF_MASTER_ENTITY: Final = "master_entity"

CONF_HYSTERESIS: Final = "hysteresis"
CONF_MASTER_START_DELAY: Final = "master_start_delay"
CONF_HEAT_PURGE_DELAY: Final = "heat_purge_delay"
CONF_MIN_RUN_TIME: Final = "min_run_time"
CONF_MIN_OFF_TIME: Final = "min_off_time"
CONF_SENSOR_TIMEOUT: Final = "sensor_timeout"
CONF_AIR_PURGE_DURATION: Final = "air_purge_duration"

CONF_ANTI_SEIZE_ENABLED: Final = "anti_seize_enabled"
CONF_ANTI_SEIZE_WEEKDAY: Final = "anti_seize_weekday"
CONF_ANTI_SEIZE_HOUR: Final = "anti_seize_hour"
CONF_ANTI_SEIZE_MINUTE: Final = "anti_seize_minute"
CONF_ANTI_SEIZE_DURATION: Final = "anti_seize_duration"

# --------------------------------------------------------------------------
# Master modes
# --------------------------------------------------------------------------
MASTER_DISABLED: Final = "disabled"
MASTER_RELAY: Final = "relay"
MASTER_EXTERNAL: Final = "external"
MASTER_MODES: Final = [MASTER_DISABLED, MASTER_RELAY, MASTER_EXTERNAL]

# Master state machine (exposed as a sensor + consumed by the Lovelace card)
MASTER_STATE_OFF: Final = "off"
MASTER_STATE_WAITING: Final = "waiting"
MASTER_STATE_ON: Final = "on"
MASTER_STATE_PURGING: Final = "purging"
MASTER_STATE_DISABLED: Final = "disabled"

# --------------------------------------------------------------------------
# Valve visual states (consumed by the Lovelace card)
# --------------------------------------------------------------------------
VALVE_CLOSED: Final = "closed"
VALVE_OPENING: Final = "opening"
VALVE_OPEN: Final = "open"
VALVE_FAULT: Final = "fault"

# --------------------------------------------------------------------------
# System operating modes
# --------------------------------------------------------------------------
SYSTEM_MODE_NORMAL: Final = "normal"
SYSTEM_MODE_SUMMER: Final = "summer"
SYSTEM_MODE_HOLIDAY: Final = "holiday"
SYSTEM_MODE_AIR_PURGE: Final = "air_purge"
SYSTEM_MODE_ANTI_SEIZE: Final = "anti_seize"

# --------------------------------------------------------------------------
# Faults
# --------------------------------------------------------------------------
FAULT_NONE: Final = None
FAULT_SENSOR_MISSING: Final = "sensor_missing"
FAULT_SENSOR_STALE: Final = "sensor_stale"
FAULT_RELAY_MISSING: Final = "relay_missing"

# --------------------------------------------------------------------------
# Defaults (seconds unless noted). These mirror the firmware protections so the
# hydraulic circuit stays safe even if the HA side is the one in command.
# --------------------------------------------------------------------------
DEFAULT_HYSTERESIS: Final = 0.3            # +/- 0.3 degC
DEFAULT_MASTER_START_DELAY: Final = 180    # 3 min actuator opening time
DEFAULT_HEAT_PURGE_DELAY: Final = 120      # 2 min residual heat purge
DEFAULT_MIN_RUN_TIME: Final = 600          # 10 min minimum ON (PTC protection)
DEFAULT_MIN_OFF_TIME: Final = 600          # 10 min minimum OFF
DEFAULT_SENSOR_TIMEOUT: Final = 7200       # 2 h watchdog
DEFAULT_AIR_PURGE_DURATION: Final = 1800   # 30 min
DEFAULT_ANTI_SEIZE_DURATION: Final = 300   # 5 min
DEFAULT_ANTI_SEIZE_WEEKDAY: Final = 6      # Sunday (Monday = 0)
DEFAULT_ANTI_SEIZE_HOUR: Final = 10
DEFAULT_ANTI_SEIZE_MINUTE: Final = 0

DEFAULT_COMFORT_TEMP: Final = 21.0
DEFAULT_ECO_TEMP: Final = 18.5
DEFAULT_AWAY_TEMP: Final = 16.0

MIN_TEMP: Final = 5.0
MAX_TEMP: Final = 30.0
TEMP_STEP: Final = 0.5

# --------------------------------------------------------------------------
# Services
# --------------------------------------------------------------------------
SERVICE_AIR_PURGE: Final = "air_purge"
SERVICE_STOP_AIR_PURGE: Final = "stop_air_purge"
SERVICE_ANTI_SEIZE: Final = "run_anti_seize"
SERVICE_RESET_METRICS: Final = "reset_metrics"
SERVICE_EMERGENCY_STOP: Final = "emergency_stop"
ATTR_DURATION: Final = "duration"
ATTR_ENTRY_ID: Final = "entry_id"

# --------------------------------------------------------------------------
# Firmware API actions (declared in openhydronic-8ch.yaml under ``api.actions``).
# Home Assistant sees them as ``esphome.<node>_<action>`` once the board is
# adopted by the ESPHome integration.
# --------------------------------------------------------------------------
FW_ACTION_AIR_PURGE: Final = "start_air_purge"
FW_ACTION_STOP_AIR_PURGE: Final = "stop_air_purge"
FW_ACTION_ANTI_SEIZE: Final = "start_anti_seize"
FW_ACTION_EMERGENCY_STOP: Final = "emergency_stop"
FW_ACTION_ALL_ZONES_OFF: Final = "all_zones_off"
# Actions a board must expose to be recognised as OpenHydronic.
FW_ACTIONS: Final = [
    FW_ACTION_AIR_PURGE,
    FW_ACTION_ANTI_SEIZE,
    FW_ACTION_EMERGENCY_STOP,
    FW_ACTION_ALL_ZONES_OFF,
]
# Runtime number entity on the board, written before a custom-duration purge.
FW_NUMBER_AIR_PURGE_DURATION: Final = "air_purge_duration"

# --------------------------------------------------------------------------
# Attributes published on the climate entities (read by the card)
# --------------------------------------------------------------------------
ATTR_VALVE_STATE: Final = "valve_state"
ATTR_RELAY_ENTITY: Final = "relay_entity"
ATTR_SENSOR_ENTITY: Final = "sensor_entity"
ATTR_IS_BYPASS: Final = "is_bypass"
ATTR_RUNTIME_HOURS: Final = "runtime_hours"
ATTR_CYCLES: Final = "cycles"
ATTR_FAULT: Final = "fault"
ATTR_DEMAND: Final = "demand"
ATTR_LOCKED_UNTIL: Final = "locked_until"
ATTR_SYSTEM_MODE: Final = "system_mode"
ATTR_MASTER_STATE: Final = "master_state"
