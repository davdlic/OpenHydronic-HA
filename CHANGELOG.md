# Changelog

All notable changes to this integration are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[semantic versioning](https://semver.org/).

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

[1.0.0]: https://github.com/davdlic/OpenHydronic-HA/releases/tag/v1.0.0
