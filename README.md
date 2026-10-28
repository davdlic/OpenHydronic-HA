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
| Published firmware | Home Assistant 2026.8 or newer, to adopt it in ESPHome without typing a key |
| Password repair | Published firmware 1.3.0 or newer, which has the `Board Password` entity |
| Sensors | One temperature sensor per zone (a `sensor` with the temperature class, or an `input_number`) |
| Relay domains | `switch`, `input_boolean`, `light`, `fan`, `valve` |
| Installation | HACS custom repository, or manual copy |

---

## Installation

### 1. Flash the board and add it to ESPHome

Follow the [OpenHydronic](https://github.com/davdlic/OpenHydronic) README. With the published
firmware, flash it, then in **Settings → Devices & services** add the **ESPHome** card for the
board and press Submit: there is no key to type. When it is done you have an ESPHome device with
`Zone 1` … `Zone 8` switches.

The official ESPHome integration is the transport; this custom component is the decision layer on
top of it. It never talks to the board itself, only to the entities ESPHome made.

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

### 3. Add the board and map its zones

The board shows up by itself under **Settings → Devices & services** as an **OpenHydronic**
discovery, next to the ESPHome one. Add it after ESPHome, and the next screen already lists every
relay the board has, one section each:

- the **room name** (left empty it is called `Zone N`)
- the **temperature sensor** of that room

Fill in only the relays that heat a room and leave the others empty: a relay with no sensor does not
become a zone, because a zone nobody can measure is switched off by design. Have your room sensors
in Home Assistant first.

The same screen asks what switches your **boiler or circulator**, and nothing is assumed:

| Answer | What happens |
|---|---|
| **None** (default) | Nothing is driven. Pick this if the board does not control it, or if nothing does. |
| **The board switches it** | Turns on the board's own *Master Local Mode*. The board then runs the master on its reserved channel. Only offered when the board has that switch. |
| **Another switch in Home Assistant** | Home Assistant drives that entity, a Shelly say, or a relay of the same board. |

Which answer fits your wiring, in the firmware's own terms:

| Wiring | Answer |
|---|---|
| Mode A, all eight relays are zones and the boiler is switched elsewhere | **Another switch in Home Assistant** |
| Mode B, seven zones and the board's relay 8 switches the boiler | **The board switches it**, and leave relay 8 without a sensor |
| Mode C, six zones, master and a bypass valve | **The board switches it**, then add the bypass valve as a zone in Configure |

Nothing tells you afterwards which answer you gave, so if the boiler never starts check
*Master Local Mode* on the board's device page. A factory reset of the board turns it off again.

If the board is not in ESPHome yet when you add it, you are told so and can check again or add it
without zones. A host you type in by hand that has no relays to read, a Shelly, a Zigbee relay or
another ESPHome board, skips all of this and is mapped under Configure as before.

### 4. Change the zones later

**Devices & Services → OpenHydronic → Configure**:

| Menu | What it sets |
|---|---|
| **Add the board's relays as zones** | The same one-screen mapping, for the relays no zone uses yet. Offered only while there are some |
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
| Minimum OFF time | 300 s | Per relay |
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

Each zone shows its valve, the current temperature and the target, with `-` and `+` on either
side of the target (0.5 °C a step) and three buttons for the presets: Comfort, Eco and Away. The
lit button is the preset in force. A target set by hand leaves none lit, and a tap on a button puts
the zone back on that preset. Tapping the name or the temperature opens the zone's details. The
minimum cycle countdown and any fault appear to the right of the name. The controls are sized for
a phone.

Valve states, matching what the coordinator decided:

| Look | Meaning |
|---|---|
| Grey, flame crossed out | Closed |
| Pulsing orange flame | Opening: PTC travel time, or waiting on the master thermal delay |
| Solid orange flame | Open and flowing |
| Red, warning triangle | Fault: the sensor watchdog tripped or the relay is unavailable |

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

Comfort, Eco and Away are chosen by you, with the buttons on the card or from an automation.
Nothing here detects whether a room is in use. Set each zone's three temperatures in
**Configure → Edit zone**, then let a presence sensor or the clock choose the preset:

```yaml
automation:
  - alias: Office empty, save energy
    triggers:
      - trigger: state
        entity_id: binary_sensor.office_presence
        to: "off"
        for: "00:30:00"
    actions:
      - action: climate.set_preset_mode
        target:
          entity_id: climate.office
        data:
          preset_mode: eco

  - alias: Bedrooms at night
    triggers:
      - trigger: time
        at: "22:00:00"
    actions:
      - action: climate.set_preset_mode
        target:
          entity_id:
            - climate.main_bedroom
            - climate.kids_room
        data:
          preset_mode: eco
```

Use `comfort`, `eco`, `away` or `none` as the `preset_mode`. The **Holiday** switch puts every zone
on its Away temperature at once.

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
   stays off for 5 minutes, long enough for the head to finish closing. This is proportional, not
   a fixed lockout: a zone that has been heating for an hour closes the moment it is asked to,
   because the minimum was met long ago.
   Only a change within the window waits, and the card counts the remaining minutes down. A sensor
   fault **breaks** the lock to turn a zone off, never to turn it on: safety always wins.
3. **Master** — a zone counts as demand only while it is both calling for heat and open, so a
   request the guard is holding back never starts the pump against a closed circuit, and a valve
   the minimum ON time keeps open no longer draws heat to a satisfied room. From the first zone
   opening it waits 3 minutes, the time the PTC heads need to open, before starting the
   circulator. After the last one it keeps running for 2 minutes to dissipate residual heat.
4. **Bypass** — if the circulator is running and no zone is open, the zone marked as bypass opens
   to give the pump somewhere to push.
5. **Watchdog** — a sensor silent for more than 2 hours switches its zone off and notifies.

The loop re-derives every timer on each pass (15 s, plus state-change events), and the cycle
timestamps are persisted, so restarting Home Assistant neither leaves the circuit in an undefined
state nor locks the zones out.

---

## The board's password

The published firmware answers to the public `admin` / `admin` until its owner sets a password. A
board still on it raises a repair, titled with the board's name followed by "still uses the public
password", under **Settings → System → Repairs**. Open it, choose a password of 8 to 64 characters
(letters, digits, spaces and the symbols of an English keyboard, no accents), and Home Assistant
sets it on the board's own `Board Password` entity, through the encrypted ESPHome connection: you
never open the board's page. It needs the published firmware, version 1.3.0 or newer.

The password is handed to that entity directly, so it does not go through the event bus or the
recorder database. Only if the entity cannot be reached that way does it fall back to the
`text.set_value` service, whose call the recorder does store. The repair clears once the board
reports it has left the public password. If the board does not confirm within a few seconds, the
form says so. This integration never writes the password to the log. With debug logging on for the
ESPHome library (`aioesphomeapi`) the outgoing message can appear there, so do not share such a log.

One password then protects the board's page and its firmware updates, and the user name does not
change. Nothing is raised for a board that has a password, for firmware you built yourself, for
older firmware without the entity, or while the board is offline. You can also set it by hand: the
`Board Password` entity is write-only, and the board's own page has the same field under
*Settings → Security*. Setting it from the entity in Home Assistant is a service call, which the
recorder stores, so prefer the repair or the board's page.

A password is not a lock on everything. The board's page is plain HTTP, the board does not lock out
repeated wrong guesses, and anyone who can call services in this Home Assistant, admin or not, can
set a new password without knowing the old one. The firmware README lists these limits.

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| A zone never calls for heat | The sensor is stale or unavailable | Check the notification; the watchdog holds the zone off on purpose. |
| A zone will not turn on right away | Minimum OFF lock | Normal. `locked_until` on the climate entity counts it down. |
| The master never starts | Master manager disabled, or no entity selected | Options → Master manager. |
| The circulator runs with everything closed | No bypass configured | Mark a zone as the bypass loop, or fit a mechanical one. |
| The card does not appear | Version 1.2.1 or older, or the browser cache after an update | Update to 1.2.2 or newer, restart Home Assistant, then hard refresh, Ctrl+Shift+R. |
| The card shows no zones | No zones mapped yet | Options → Add zone. |
| The board was added twice | Added manually and then discovered | Remove one entry; newer versions merge them automatically. |
| A repair says the board has relays but no zones | The board was added without zones | Configure → Add the board's relays as zones. |
| A repair says the board still uses the public password | The published firmware has not had a password set yet | Open the repair under Settings → System → Repairs and choose one. |
| The password repair says the board did not take it | The board is offline or unreachable from Home Assistant, or did not confirm within a few seconds | Check the board is online and connected, then try again. |
| The zones screen says the board is not in ESPHome | Home Assistant gets the relays from the ESPHome integration | Add the board there first, then press Check again. |
| ESPHome asks for an encryption key for the published firmware | Home Assistant is older than 2026.8 and cannot set the key itself | Update Home Assistant, or build the firmware with your own key. |
| The boiler stopped after the board was factory reset | *Master Local Mode* goes back to off | Switch it on again on the board's device page. |

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
