# Changelog

All notable changes to this integration are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/).

## [1.2.3] - 2026-10-28

### Fixed

- The card was slow to follow the buttons. Home Assistant lets a coordinator refresh
  once every 10 seconds, so each tap on `-`, `+` or a preset showed up ten seconds
  after the one before it, and a burst of taps took a minute to arrive. A tap is now
  applied at once, and the card shows it straight away until the board confirms.
  Repeated taps on `+` or `-` add up instead of all starting from the old value, and
  the setpoint stays inside the zone's limits.
- The card showed "minimum cycle" next to a zone whose relay was already doing what
  was asked, for example after lowering the setpoint and raising it again. It now
  shows the lock only while it holds the relay against the request. The relay itself
  already behaved correctly.
- A zone with a long name grew wider than the card. The grid no longer stretches and
  the name wraps onto a second line.
- A sensor that repeats the same temperature was counted as not updating after two
  hours, because only a change of value reset the clock. A report of the same value
  now counts.

### Changed

- The temperature sensor list offers `sensor` entities with the temperature class and
  `input_number` helpers. It no longer offers `number` entities: a thermostat's
  setpoints are numbers with the same name as its sensor, and choosing one made the zone
  report a sensor that never updates. A zone already set to a `number` keeps working
  until it is edited.
- A sensor or relay fault now says on the card what to check and which entity it is
  about, and where to pick another one.
- The "Master disabled" pill reads "Pump not managed" and only shows while a zone is
  asking for heat, since leaving the pump to something else is a valid setup.

## [1.2.2] - 2026-10-27

### Fixed

- The card never showed up in Home Assistant's card picker. Home Assistant
  imports the card file when the page starts, before its own Lovelace elements
  exist, and the card borrowed Lit from them, so it failed on the first line and
  registered nothing. Lit now ships inside the card. This applies to every
  earlier version, which the tests could not see because they supplied Lit
  themselves.

## [1.2.1] - 2026-10-25

### Changed

- The card is built for a phone. Each zone has the `-` and `+` on either side of
  the target temperature, 52 px wide, and three preset buttons (Comfort, Eco,
  Away) that set the preset with a tap. The active preset is lit; a temperature
  set by hand leaves none lit instead of showing the word `none`.
- The minimum cycle and fault messages sit to the right of the zone name.
- The valve is a flame on a disc: orange when it heats, crossed out and grey
  when closed, a red warning triangle on a fault.
- Presets read in the Home Assistant language (Conforto, Eco, Ausente), and
  "Air purge" is shortened to "Purge" so the three global buttons fit across a
  phone.
- The README explains that the presets do not detect anyone in the room, and
  gives automations that switch them from a presence sensor or a schedule.

## [1.2.0] - 2026-10-19

### Added

- A repair while a board still answers to the public `admin` / `admin`. It can
  be fixed from the repair itself: Home Assistant asks for a password and sets
  it on the board's own `Board Password` entity, through the encrypted ESPHome
  connection, so nobody has to open the board's page. The board says it is
  exposed through its `Default Password` sensor, so nothing is raised for a
  board that has a password of its own, for older firmware without the entities,
  or while the board is offline.

## [1.1.0] - 2026-10-17

### Added

- The relays of the board fill in the zones screen. After the board is added in
  the ESPHome integration, adding OpenHydronic lists every relay it has, one
  section each, and a zone is made wherever a temperature sensor is picked.
  Eight screens and the relay entity picked by hand, per zone, become one
  screen. Nothing talks to the board: the relays are read from the entities
  ESPHome already made, found by the names the firmware gave them, so renaming
  an entity changes nothing.
- The same screen asks what switches the boiler or circulator and assumes
  nothing: none (the default), the board's own master, or another switch.
- If the board is not in ESPHome yet the flow says so, with Check again and Add
  without zones, instead of a dead end. A board that is in ESPHome but has not
  listed its relays is waited for, with a progress step.
- A room name typed without its sensor is refused instead of dropped, a switch
  picked without choosing the answer counts as that answer, and what was typed
  comes back after an error on every supported Home Assistant.
- Configure offers to map the relays no zone uses yet, and a repair reminds you
  when a board was added without any zone.
- The config flow runs in CI against a real Home Assistant, the oldest release
  `hacs.json` promises (2024.10) and the latest, besides the stand-in tests.

### Fixed

- Configure could not be opened on Home Assistant 2024.10, the oldest release
  `hacs.json` promises. The options flow used a property Home Assistant only
  adds in 2024.11. It now keeps the entry itself.
- The device page reported firmware 1.0.0 on every version: `INTEGRATION_VERSION`
  was a constant of its own and never followed `manifest.json`. The release
  workflow now refuses to publish if the two disagree.

### Changed

- A board typed in by hand that ESPHome knows is keyed by its MAC, so a later
  discovery completes it instead of adding it twice, and a discovery card left
  open no longer refuses it. A host with no relays to read, a Shelly, a Zigbee
  relay or any other ESPHome board, is added at once as before.
- Choosing that the board switches the boiler is refused while the board's
  master switch is unavailable. Home Assistant skips an unavailable entity
  without an error, so the flow would have reported a master it never started.
- The reminder about relays with no zones is dropped when the entry is unloaded.

## [1.0.2] - 2026-10-15

### Fixed

- The circulator could run against a fully closed circuit. A zone the cycle
  guard was still holding back counted as heat demand, so the master started
  while every valve stayed shut. Demand now counts a zone only while it is both
  calling for heat and open, which also stops a valve held open by the minimum
  ON time from drawing heat to a room that is already satisfied.

### Changed

- Minimum OFF time defaults to 5 min instead of 10, enough to cover the
  actuator closing.

## [1.0.1] - 2026-10-15

### Added

- Tagged releases are published automatically, after the bundled card is
  rebuilt from source and checked against the committed one.

### Fixed

- Manifest keys sorted and `quality_scale` dropped, so hassfest passes.
- Brand assets are served by the integration itself instead of waiting on a
  pull request to the Home Assistant brands repository.

### Documentation

- Clarified that the cycle guards are proportional to the time since the last
  change, not a fixed lockout.

## [1.0.0] - 2026-09-15

First public release.

### Added

- Config flow with mDNS discovery of `openhydronic-*` boards and support for
  several boards in one Home Assistant instance.
- Dynamic zone mapping: any relay entity bound to any temperature sensor.
- One thermostat per zone with configurable hysteresis and comfort, eco and
  away presets.
- Master manager in three modes: disabled, physical relay, or an external
  Home Assistant entity.
- Thermal start delay, residual heat purge and minimum ON/OFF cycle guards
  mirroring the firmware protections.
- Bypass zone that opens whenever the circulator runs against a closed circuit.
- Sensor watchdog: a zone whose sensor goes stale is switched off and reported
  as a persistent notification.
- Weekly anti-seize routine, manual air purge and emergency stop, executed on
  the board itself when it exposes the firmware actions.
- Runtime hours and cycle counters per zone.
- Bundled Lovelace card, registered automatically, English and Portuguese.
- Brand icon and logo served from the integration itself (HA 2026.3 and newer).

[1.2.0]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.2.0
[1.1.0]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.1.0
[1.0.2]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.0.2
[1.0.1]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.0.1
[1.0.0]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.0.0
