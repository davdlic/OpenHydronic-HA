# Contributing to OpenHydronic-HA

Thanks for helping out. This integration commands valves and a boiler, so
changes are reviewed with safety first.

## Ground rules

- **All decisions live in `coordinator.py`.** Entities are views; they forward
  commands and never switch a relay themselves. That keeps the cycle guards and
  the master state machine impossible to bypass from the UI.
- **Never weaken a protection by default.** Hysteresis, minimum cycle times,
  the sensor watchdog and the bypass exist to protect hardware. New behaviour
  goes behind an option that is off by default.
- **Local only.** No cloud services, no CDN. The Lovelace card must work with
  the internet down.

## Development

```bash
npm install
npm run build     # minify the card into custom_components/openhydronic/www/
```

`npm run dev` copies the unminified card instead, which is easier to debug.
Always commit the built file: HACS ships it as is.

Point a development Home Assistant at `custom_components/openhydronic` and
enable debug logging:

```yaml
logger:
  logs:
    custom_components.openhydronic: debug
```

## Before opening a pull request

1. `python -m compileall custom_components/openhydronic`
2. `npm run build` and commit the result if you touched the card.
3. Keep comments short and in English. User-visible strings go through
   `strings.json` plus `translations/`, or the `LABELS` table in the card.
4. Update the README and `CHANGELOG.md` when behaviour changes.

## Reporting a problem

Include the Home Assistant version, the integration version, the zone setup
(relay and sensor entities, master mode) and the relevant log lines.

## Security

Report anything security sensitive privately through GitHub's security advisory
form instead of a public issue.
