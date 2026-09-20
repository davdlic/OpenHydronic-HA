<!--
OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
Copyright (C) 2026 David Lopes (https://github.com/davdlic)
Licensed under the GNU General Public License v3.0 - see LICENSE
-->

# OpenHydronic — Home Assistant integration

[![Validate](https://github.com/davdlic/OpenHydronic-HA/actions/workflows/validate.yml/badge.svg)](https://github.com/davdlic/OpenHydronic-HA/actions/workflows/validate.yml)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![Home Assistant](https://img.shields.io/badge/HA-2024.10%2B-blue.svg)](https://www.home-assistant.io/)

Custom integration and Lovelace card for [OpenHydronic](https://github.com/davdlic/OpenHydronic),
the open source ESP32 firmware that replaces the zone controller of an underfloor heating or
radiator installation.

The firmware protects the hardware; this integration is the thermal brain on top of it. It binds
each relay to any temperature sensor you already have, runs a thermostat per zone, manages the
boiler or circulator, and watches the sensors for silence.

> [!NOTE]
> The split between the two repositories is deliberate. Critical protections exist on **both**
> sides: if Home Assistant goes down the board keeps the installation safe on its own, and if the
> board goes down Home Assistant marks the zones unavailable and notifies you. Home Assistant is
> never the only guard.

---

## What you get

- **Any relay, any sensor.** A zone is one switchable entity plus one temperature sensor, so
  Zigbee, BLE, Wi-Fi or wired sensors all work, and the relay does not have to be an OpenHydronic
  board at all.
- **A thermostat per zone** with configurable hysteresis (±0.3 °C by default) and Comfort, Eco and
  Away presets, exposed as standard `climate` entities.
- **mDNS discovery.** Boards announce themselves as `openhydronic-*` and show up as a discovery
  card. Several boards in one instance are supported and coordinated together.
- **Flexible master manager**, in three modes: disabled (100% actuators), a physical relay on a
  board, or any external Home Assistant entity such as `switch.buffer_pump`.
- **The firmware protections, mirrored.** Thermal start delay, residual heat purge and minimum
  ON/OFF cycle guards run here as well, so an installation driving third-party relays is just as
  protected.
- **Bypass zone.** Mark one zone as the bypass and it opens by itself whenever the circulator runs
  against a closed circuit.
- **Sensor watchdog.** A sensor that stops updating for two hours switches its zone off and raises
  a persistent notification.
- **Routines run on the board.** Air purge, anti-seize and emergency stop are handed to the
  firmware when the board exposes them, so a 30 minute purge survives a Home Assistant restart.
  Without an OpenHydronic board they run here instead.
- **Metrics per actuator**: runtime hours and cycle counts, ready for the energy dashboard.
- **Bundled Lovelace card**, registered automatically, no manual resource entry, no CDN, English
  and Portuguese.

---

## Compatibility

| Item | Requirement |
|---|---|
| Home Assistant | 2024.10 or newer |
| Board | [OpenHydronic](https://github.com/davdlic/OpenHydronic) firmware, or any `switch`-like entity |
| Sensors | One temperature sensor per zone (`sensor`, `number` or `input_number`) |
| Relay domains | `switch`, `input_boolean`, `light`, `fan`, `valve` |
| Installation | HACS custom repository, or manual copy |

---

## Installation

### 1. Flash the board

Follow the [OpenHydronic](https://github.com/davdlic/OpenHydronic) README. When it is done you
should have an ESPHome device in Home Assistant with `Zone 1` … `Zone 8` switches.

The official ESPHome integration is the transport; this custom component is the decision layer on
top of it.

### 2. Install the integration

**Via HACS (recommended)**

1. HACS → **Integrations** → ⋮ → **Custom repositories**
2. URL `https://github.com/davdlic/OpenHydronic-HA`, category **Integration**
3. Install **OpenHydronic** and restart Home Assistant

**Manual**

Copy `custom_components/openhydronic/` into `<config>/custom_components/` and restart.

The Lovelace card is served and loaded by the integration itself from
`/openhydronic_frontend/openhydronic-card.js`. Nothing to add under *Settings → Dashboards →
Resources*.

### 3. Add the board

A board on the network shows up by itself under **Settings → Devices & Services** as a discovery.
Otherwise use **Add integration → OpenHydronic** and type its IP.

### 4. Map the zones

**Devices & Services → OpenHydronic → Configure**:

| Menu | What it sets |
|---|---|
| **Add zone** | Name, relay, temperature sensor, Comfort/Eco/Away setpoints, bypass flag |
| **Master manager** | Disabled, physical relay, or external entity |
| **Regulation and cycle timings** | Hysteresis, thermal delay, residual purge, min ON, min OFF |
| **Protections and routines** | Sensor watchdog, air purge duration, anti-seize schedule |

Every zone becomes a `climate.<name>` entity, with `sensor.<name>_runtime` and
`sensor.<name>_cycles` alongside it.

### 5. Add the card

Edit the dashboard → **Add card** → search for *OpenHydronic*. With no configuration at all the
card finds the zones by itself:

```yaml
type: custom:openhydronic-card
title: Underfloor heating
```

---

## Configuration

Everything is set in the UI. The defaults mirror the firmware:

| Option | Default | Notes |
|---|---|---|
| Hysteresis | 0.3 °C | Zone calls below `setpoint - h`, releases above `setpoint + h` |
| Master start delay | 180 s | Time for the PTC heads to open before the pump starts |
| Residual heat purge | 120 s | Pump keeps running after the last zone closes |
| Minimum ON time | 600 s | Per relay |
| Minimum OFF time | 600 s | Per relay |
| Sensor watchdog | 7200 s | Stale sensor switches its zone off |
| Air purge duration | 1800 s | All valves open, pump running |
| Anti-seize | Sunday 10:00, 300 s | Weekly exercise of every actuator |
| Comfort / Eco / Away | 21.0 / 18.5 / 16.0 °C | Per zone |

---

## Entities

| Entity | Type | Purpose |
|---|---|---|
| `climate.<zone>` | climate | Thermostat: setpoint, presets, HVAC action |
| `sensor.<zone>_runtime` | sensor | Actuator runtime, in hours |
| `sensor.<zone>_cycles` | sensor | Number of open cycles |
| `sensor.<board>_master_state` | sensor | `disabled`, `off`, `waiting`, `on`, `purging` |
| `sensor.<board>_system_mode` | sensor | `normal`, `summer`, `holiday`, `air_purge`, `anti_seize` |
| `sensor.<board>_active_zones` | sensor | Zones physically open |
| `switch.<board>_summer_mode` | switch | Heating off, anti-seize still runs |
| `switch.<board>_holiday_mode` | switch | Every zone clamps to its Away setpoint |
| `switch.<board>_air_purge` | switch | Manual air purge, auto-off on timeout |

Each `climate` entity also publishes the attributes the card reads: `valve_state`, `fault`,
`locked_until`, `demand`, `runtime_hours`, `cycles`, `system_mode` and `master_state`.

---

## Lovelace card

```yaml
type: custom:openhydronic-card
title: Underfloor heating
zones:                      # optional, empty = auto-detect
  - climate.living_room
  - climate.main_bedroom
  - climate.bypass
show_global: true           # Summer / Holiday / Air purge buttons
show_metrics: false         # runtime hours and cycles per zone
```

Valve states, matching what the coordinator decided:

| Colour | Meaning |
|---|---|
| Grey | Closed |
| Pulsing orange | Opening: PTC travel time, or waiting on the master thermal delay |
| Solid orange | Open and flowing |
| Red | Fault: the sensor watchdog tripped or the relay is unavailable |

The card takes its language from Home Assistant, English or Portuguese.

---

## Services and automations

| Service | Description |
|---|---|
| `openhydronic.air_purge` | Opens every valve with the circulator running. Optional `duration`, default 1800 s. |
| `openhydronic.stop_air_purge` | Cancels a running purge. |
| `openhydronic.run_anti_seize` | Cycles every relay. Optional `duration`, default 300 s. |
| `openhydronic.emergency_stop` | Closes everything now, ignoring the minimum cycle timers. |
| `openhydronic.reset_metrics` | Clears runtime hours and cycle counters. |

All of them take an optional `entry_id`; without it they apply to every board.

```yaml
action: openhydronic.air_purge
data:
  duration: 1800
```

Turn the heating off while a window is open:

```yaml
automation:
  - alias: Living room window open
    triggers:
      - trigger: state
        entity_id: binary_sensor.living_room_window
        to: "on"
        for: "00:02:00"
    actions:
      - action: climate.set_hvac_mode
        target:
          entity_id: climate.living_room
        data:
          hvac_mode: "off"
```

Stop everything when the water pressure drops:

```yaml
automation:
  - alias: Low heating pressure
    triggers:
      - trigger: numeric_state
        entity_id: sensor.boiler_pressure
        below: 0.8
    actions:
      - action: openhydronic.emergency_stop
```

---

## How the control loop works

```
sensors ──► hysteresis ──► cycle guards ──► zone relays
                 │
                 └──────► master state machine ──► bypass
```

1. **Hysteresis** — a zone calls for heat below `setpoint - 0.3 °C` and releases above
   `setpoint + 0.3 °C`.
2. **Cycle guards** — a relay that just turned on stays on for 10 minutes, one that just turned off
   stays off for 10 minutes. A sensor fault **breaks** the lock to turn a zone off, never to turn
   it on: safety always wins.
3. **Master** — on the first request it waits 3 minutes, the time the PTC heads need to open,
   before starting the circulator. After the last one it keeps running for 2 minutes to dissipate
   residual heat.
4. **Bypass** — if the circulator is running and no zone is open, the zone marked as bypass opens
   to give the pump somewhere to push.
5. **Watchdog** — a sensor silent for more than 2 hours switches its zone off and notifies.

The loop re-derives every timer on each pass (15 s, plus state-change events), and the cycle
timestamps are persisted, so restarting Home Assistant neither leaves the circuit in an undefined
state nor locks the zones out.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| A zone never calls for heat | The sensor is stale or unavailable | Check the notification; the watchdog holds the zone off on purpose. |
| A zone will not turn on right away | Minimum OFF lock | Normal. `locked_until` on the climate entity counts it down. |
| The master never starts | Master manager disabled, or no entity selected | Options → Master manager. |
| The circulator runs with everything closed | No bypass configured | Mark a zone as the bypass loop, or fit a mechanical one. |
| The card does not appear | Browser cache after an update | Hard refresh, Ctrl+Shift+R. |
| The card shows no zones | No zones mapped yet | Options → Add zone. |
| The board was added twice | Added manually and then discovered | Remove one entry; newer versions merge them automatically. |

Enable debug logging:

```yaml
logger:
  logs:
    custom_components.openhydronic: debug
```

---

## Known limitations

- The integration mirrors the firmware protections but cannot enforce them on third-party relays
  beyond switching them: a relay driven by something else can still be toggled behind its back.
- A custom air purge duration is pushed to the board's own `Air Purge Duration` number entity when
  it can be found. If it cannot, the board keeps its configured duration and only the Home
  Assistant side honours the custom value.
- The anti-seize schedule runs on Home Assistant's clock. The board has its own weekly schedule as
  a backup, which needs a time source.
- Zone metrics count what the relay actually did, so they reset if you rebuild a zone from scratch.

---

## FAQ

**Do I need the OpenHydronic firmware?**
No. Any switchable entity works as a zone relay. With the firmware you additionally get the
hardware-side protections and routines that survive a Home Assistant outage.

**Can I use it with radiators instead of underfloor heating?**
Yes. Shorten the master start delay if the valves are fast, and keep the minimum cycle guards.

**Several boards?**
Add each one as its own entry. Zones from different boards can share a single master.

**Does it need the internet?**
No. Everything is local, including the Lovelace card.

---

## Contributing

Pull requests are welcome. Read [CONTRIBUTING.md](CONTRIBUTING.md) first, especially the rule that
all decisions belong in `coordinator.py`.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md).

---

## Acknowledgments

Built on [ESPHome](https://esphome.io/) and the Home Assistant developer APIs. Thanks to everyone
who documented the quirks of thermal actuators and boiler room-stat inputs so this did not have to
be learned the expensive way.

---

## License

GNU General Public License v3.0. See [LICENSE](LICENSE).
