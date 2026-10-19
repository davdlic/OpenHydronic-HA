# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Config and options flow.

The board announces itself over mDNS as ``openhydronic-<mac>``; a host typed
by hand works just as well, since only entity ids are needed afterwards.
"""

from __future__ import annotations

import asyncio
import uuid
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.core import callback
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.data_entry_flow import AbortFlow, section
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector

try:  # Home Assistant >= 2025.2
    from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
except ImportError:  # pragma: no cover - older cores
    from homeassistant.components.zeroconf import ZeroconfServiceInfo  # type: ignore

from .board import (
    Board,
    async_get_board,
    free_channels,
    taken_relays,
    unfinished_sections,
    zone_section_key,
    zones_from_form,
)
from .const import (
    CONF_AIR_PURGE_DURATION,
    CONF_ANTI_SEIZE_DURATION,
    CONF_ANTI_SEIZE_ENABLED,
    CONF_ANTI_SEIZE_HOUR,
    CONF_ANTI_SEIZE_MINUTE,
    CONF_ANTI_SEIZE_WEEKDAY,
    CONF_AWAY_TEMP,
    CONF_COMFORT_TEMP,
    CONF_DEVICE_NAME,
    CONF_ECO_TEMP,
    CONF_FW_VERSION,
    CONF_HEAT_PURGE_DELAY,
    CONF_HOST,
    CONF_HYSTERESIS,
    CONF_IS_BYPASS,
    CONF_MAC,
    CONF_MASTER_CHOICE,
    CONF_MASTER_ENTITY,
    CONF_MASTER_MODE,
    CONF_MASTER_START_DELAY,
    CONF_MIN_OFF_TIME,
    CONF_MIN_RUN_TIME,
    CONF_NODE_NAME,
    CONF_PORT,
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
    MASTER_CHOICE_BOARD,
    MASTER_CHOICE_ENTITY,
    MASTER_CHOICE_NONE,
    MASTER_DISABLED,
    MASTER_EXTERNAL,
    MASTER_MODES,
    MASTER_RELAY,
)

# How long to wait for ESPHome to list a board's entities after it is adopted.
WAIT_POLLS = 30

SWITCHABLE_DOMAINS = ["switch", "input_boolean", "light", "fan", "valve"]
SENSOR_DOMAINS = ["sensor", "number", "input_number"]

STEP_USER_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_DEVICE_NAME, default="OpenHydronic"): str,
        vol.Optional(CONF_PORT, default=6053): vol.All(
            vol.Coerce(int), vol.Range(min=1, max=65535)
        ),
    }
)


def _node_name_from_host(host: str) -> str | None:
    """ESPHome node name from a hostname, or None when given an IP."""
    name = host.split(".")[0]
    if not name or name.isdigit():
        return None
    return name


def _relay_selector() -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(domain=SWITCHABLE_DOMAINS)
    )


def _sensor_selector() -> selector.EntitySelector:
    return selector.EntitySelector(
        selector.EntitySelectorConfig(
            domain=SENSOR_DOMAINS, device_class="temperature"
        )
    )


def _temp_selector(minimum: float = 5, maximum: float = 30) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum, max=maximum, step=0.5, unit_of_measurement="°C",
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _seconds_selector(minimum: int, maximum: int) -> selector.NumberSelector:
    return selector.NumberSelector(
        selector.NumberSelectorConfig(
            min=minimum, max=maximum, step=10, unit_of_measurement="s",
            mode=selector.NumberSelectorMode.BOX,
        )
    )


def _zone_schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_ZONE_NAME, default=defaults.get(CONF_ZONE_NAME, "")): str,
            vol.Required(
                CONF_RELAY_ENTITY, default=defaults.get(CONF_RELAY_ENTITY, vol.UNDEFINED)
            ): _relay_selector(),
            vol.Optional(
                CONF_SENSOR_ENTITY,
                description={"suggested_value": defaults.get(CONF_SENSOR_ENTITY)},
            ): _sensor_selector(),
            vol.Optional(
                CONF_COMFORT_TEMP,
                default=defaults.get(CONF_COMFORT_TEMP, DEFAULT_COMFORT_TEMP),
            ): _temp_selector(),
            vol.Optional(
                CONF_ECO_TEMP, default=defaults.get(CONF_ECO_TEMP, DEFAULT_ECO_TEMP)
            ): _temp_selector(),
            vol.Optional(
                CONF_AWAY_TEMP, default=defaults.get(CONF_AWAY_TEMP, DEFAULT_AWAY_TEMP)
            ): _temp_selector(),
            vol.Optional(
                CONF_IS_BYPASS, default=defaults.get(CONF_IS_BYPASS, False)
            ): selector.BooleanSelector(),
        }
    )


def _new_zone_id() -> str:
    return uuid.uuid4().hex[:8]


def _zones_schema(
    board: Board,
    *,
    channels: list[int] | None = None,
    with_master: bool = False,
    previous: dict[str, Any] | None = None,
) -> vol.Schema:
    """One section per relay of the board: a room name and its temperature sensor.

    Nothing is required: a relay that heats no room is simply left empty.
    `previous` is what the user last submitted, put back after an error. Home
    Assistant's own helper does not reach inside sections before 2024.11.
    """
    previous = previous or {}
    fields: dict[Any, Any] = {}
    for channel in sorted(board.zones if channels is None else channels):
        before = previous.get(zone_section_key(channel)) or {}
        fields[vol.Optional(zone_section_key(channel))] = section(
            vol.Schema(
                {
                    vol.Optional(
                        CONF_ZONE_NAME,
                        description={"suggested_value": before.get(CONF_ZONE_NAME)},
                    ): str,
                    vol.Optional(
                        CONF_SENSOR_ENTITY,
                        description={"suggested_value": before.get(CONF_SENSOR_ENTITY)},
                    ): _sensor_selector(),
                }
            ),
            {"collapsed": False},
        )

    if with_master:
        choices = [MASTER_CHOICE_NONE]
        if board.master_local_mode:
            choices.append(MASTER_CHOICE_BOARD)
        choices.append(MASTER_CHOICE_ENTITY)
        fields[
            vol.Required(
                CONF_MASTER_CHOICE,
                default=previous.get(CONF_MASTER_CHOICE, MASTER_CHOICE_NONE),
            )
        ] = (
            selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=choices,
                    translation_key="master_choice",
                    mode=selector.SelectSelectorMode.LIST,
                )
            )
        )
        fields[
            vol.Optional(
                CONF_MASTER_ENTITY,
                description={"suggested_value": previous.get(CONF_MASTER_ENTITY)},
            )
        ] = _relay_selector()

    return vol.Schema(fields)


class OpenHydronicConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle discovery and manual setup of an OpenHydronic board."""

    VERSION = 1

    def __init__(self) -> None:
        self._discovered: dict[str, Any] = {}
        self._manual = False
        self._board: Board | None = None
        self._wait_task: asyncio.Task[None] | None = None
        self._waited = False

    @callback
    def async_remove(self) -> None:
        if self._wait_task is not None:
            self._wait_task.cancel()

    def _lookup_board(self) -> Board | None:
        """The board as the ESPHome integration knows it, read fresh every time."""
        return async_get_board(
            self.hass,
            mac=self._discovered.get(CONF_MAC),
            host=self._discovered.get(CONF_HOST),
            node_name=self._discovered.get(CONF_NODE_NAME),
        )

    def _placeholders(self) -> dict[str, str]:
        return {
            "name": self._discovered.get(CONF_DEVICE_NAME) or "OpenHydronic",
            "host": self._discovered.get(CONF_HOST) or "",
        }

    def _create_entry(self, options: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_create_entry(
            title=self._discovered.get(CONF_DEVICE_NAME) or "OpenHydronic",
            data=self._discovered,
            options=options or _default_options(),
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            # A discovered board is keyed by MAC, so also match on the host to
            # avoid adding the same board twice.
            self._abort_if_host_configured(host)
            self._discovered = {
                CONF_HOST: host,
                CONF_PORT: user_input.get(CONF_PORT, 6053),
                CONF_DEVICE_NAME: user_input.get(CONF_DEVICE_NAME) or "OpenHydronic",
                CONF_NODE_NAME: _node_name_from_host(host),
            }
            self._manual = True

            # An adopted board is keyed by its MAC like a discovered one, so a
            # later discovery completes this entry instead of duplicating it.
            unique_id = host.lower()
            board = self._lookup_board()
            if board is not None and board.mac:
                unique_id = board.mac.replace(":", "")
                self._discovered[CONF_MAC] = unique_id
            # A discovery card for the same board may still be open: this entry
            # replaces it instead of being refused because of it.
            await self.async_set_unique_id(unique_id, raise_on_progress=False)
            self._abort_if_unique_id_configured(updates={CONF_HOST: host})
            return await self.async_step_resolve()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_SCHEMA, errors=errors
        )

    def _entry_for_host(self, host: str) -> ConfigEntry | None:
        """Existing entry pointing at this host, if any."""
        wanted = host.lower().removesuffix(".local")
        for entry in self._async_current_entries():
            known = str(entry.data.get(CONF_HOST, "")).lower().removesuffix(".local")
            if known and known == wanted:
                return entry
        return None

    def _abort_if_host_configured(self, host: str) -> None:
        if self._entry_for_host(host) is not None:
            raise AbortFlow("already_configured")

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        """Handle an ``openhydronic-*`` ESPHome node found over mDNS."""
        properties = discovery_info.properties or {}
        mac = properties.get("mac") or properties.get("macaddress")
        host = discovery_info.host
        name = (discovery_info.hostname or discovery_info.name or "").split(".")[0]

        # Same board added by hand earlier: complete it instead of duplicating.
        if (entry := self._entry_for_host(host)) is not None:
            self.hass.config_entries.async_update_entry(
                entry,
                data={
                    **entry.data,
                    CONF_MAC: mac or entry.data.get(CONF_MAC),
                    CONF_NODE_NAME: name or entry.data.get(CONF_NODE_NAME),
                },
            )
            raise AbortFlow("already_configured")

        unique_id = (mac or host).lower()
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        self._discovered = {
            CONF_HOST: host,
            CONF_PORT: discovery_info.port or 6053,
            CONF_MAC: mac,
            CONF_DEVICE_NAME: properties.get("friendly_name") or name or "OpenHydronic",
            CONF_FW_VERSION: properties.get("version"),
            # Addresses the firmware actions as esphome.<node>_<action>.
            CONF_NODE_NAME: name or None,
        }
        self.context["title_placeholders"] = {
            "name": self._discovered[CONF_DEVICE_NAME],
            "host": host,
        }
        return await self.async_step_discovery_confirm()

    async def async_step_discovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Ask the user to confirm adding the discovered board.

        The board is only looked up once they confirm, so it does not matter
        whether the ESPHome card was handled before or after this one.
        """
        if user_input is not None:
            self._abort_if_host_configured(self._discovered[CONF_HOST])
            return await self.async_step_resolve()

        self._set_confirm_only()
        return self.async_show_form(
            step_id="discovery_confirm",
            description_placeholders=self._placeholders(),
        )

    async def async_step_resolve(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Look the board up in the ESPHome integration and branch on the answer."""
        board = self._lookup_board()

        if self._manual and (board is None or not board.zones):
            # Typed by hand and nothing to read: a Shelly, a Zigbee relay, or
            # any ESPHome board that is not this one.
            return self._create_entry()

        if board is None:
            return await self.async_step_not_adopted()

        if not board.zones:
            # Adopted, but ESPHome has not listed its entities yet.
            if not self._waited:
                return await self.async_step_wait_board()
            return await self.async_step_no_zones()

        self._board = board
        return await self.async_step_zones()

    # A menu's step_id is also a step method: Home Assistant calls it again
    # whenever the dialog is reopened.
    async def async_step_not_adopted(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="not_adopted",
            menu_options=["retry", "skip"],
            description_placeholders=self._placeholders(),
        )

    async def async_step_no_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="no_zones",
            menu_options=["retry", "skip"],
            description_placeholders=self._placeholders(),
        )

    async def _async_wait_for_zones(self) -> None:
        """Give ESPHome time to register the relays after the board is adopted."""
        for _ in range(WAIT_POLLS):
            board = self._lookup_board()
            if board is not None and board.zones:
                return
            await asyncio.sleep(1)

    async def async_step_wait_board(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if self._wait_task is None:
            self._wait_task = self.hass.async_create_task(self._async_wait_for_zones())

        if not self._wait_task.done():
            return self.async_show_progress(
                step_id="wait_board",
                progress_action="wait_board",
                progress_task=self._wait_task,
                description_placeholders=self._placeholders(),
            )

        self._wait_task = None
        self._waited = True
        return self.async_show_progress_done(next_step_id="resolve")

    async def async_step_retry(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        self._waited = False
        return await self.async_step_resolve()

    async def async_step_skip(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Add the board with no zones; they can be mapped later in Configure."""
        return self._create_entry()

    async def async_step_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """One form for every relay of the board, and what drives the boiler."""
        board = self._board
        if board is None:
            return await self.async_step_resolve()
        errors: dict[str, str] = {}

        if user_input is not None:
            # The form may have sat open while the board changed.
            fresh = self._lookup_board()
            if fresh is None or not fresh.zones:
                return await self.async_step_resolve()
            self._board = board = fresh
            outcome = await self._async_submit_zones(board, user_input)
            if isinstance(outcome, str):
                errors["base"] = outcome
            else:
                return outcome

        return self.async_show_form(
            step_id="zones",
            data_schema=_zones_schema(board, with_master=True, previous=user_input),
            errors=errors,
            description_placeholders={
                **self._placeholders(),
                "count": str(len(board.zones)),
            },
        )

    async def _async_submit_zones(
        self, board: Board, user_input: dict[str, Any]
    ) -> ConfigFlowResult | str:
        """The created entry, or the key of the error to show."""
        if unfinished_sections(board, user_input):
            return "sensor_required"
        zones = zones_from_form(board, user_input, new_id=_new_zone_id)
        taken = taken_relays(self._async_current_entries())
        if any(zone[CONF_RELAY_ENTITY] in taken for zone in zones):
            return "relay_in_use"

        options = {**_default_options(), CONF_ZONES: zones}
        choice = user_input.get(CONF_MASTER_CHOICE, MASTER_CHOICE_NONE)
        entity = user_input.get(CONF_MASTER_ENTITY)
        if choice == MASTER_CHOICE_NONE and entity:
            choice = MASTER_CHOICE_ENTITY  # a switch picked says what was meant

        if choice == MASTER_CHOICE_ENTITY:
            if not entity:
                return "master_entity_required"
            if entity in {zone[CONF_RELAY_ENTITY] for zone in zones}:
                return "master_is_zone"
            options[CONF_MASTER_MODE] = (
                MASTER_RELAY if entity in board.zones.values() else MASTER_EXTERNAL
            )
            options[CONF_MASTER_ENTITY] = entity
        elif choice == MASTER_CHOICE_BOARD:
            if not board.master_local_mode:
                return "master_switch_missing"
            # A service call skips an unavailable entity without a word, which
            # would leave the user believing the board runs the master.
            state = self.hass.states.get(board.master_local_mode)
            if state is None or state.state in (STATE_UNAVAILABLE, STATE_UNKNOWN):
                return "master_switch_failed"
            try:
                await self.hass.services.async_call(
                    "switch",
                    "turn_on",
                    {"entity_id": board.master_local_mode},
                    blocking=True,
                )
            except HomeAssistantError:
                return "master_switch_failed"

        return self._create_entry(options)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        return OpenHydronicOptionsFlow(config_entry)


def _default_options() -> dict[str, Any]:
    return {
        CONF_ZONES: [],
        CONF_MASTER_MODE: MASTER_DISABLED,
        CONF_MASTER_ENTITY: None,
        CONF_HYSTERESIS: DEFAULT_HYSTERESIS,
        CONF_MASTER_START_DELAY: DEFAULT_MASTER_START_DELAY,
        CONF_HEAT_PURGE_DELAY: DEFAULT_HEAT_PURGE_DELAY,
        CONF_MIN_RUN_TIME: DEFAULT_MIN_RUN_TIME,
        CONF_MIN_OFF_TIME: DEFAULT_MIN_OFF_TIME,
        CONF_SENSOR_TIMEOUT: DEFAULT_SENSOR_TIMEOUT,
        CONF_AIR_PURGE_DURATION: DEFAULT_AIR_PURGE_DURATION,
        CONF_ANTI_SEIZE_ENABLED: True,
        CONF_ANTI_SEIZE_WEEKDAY: DEFAULT_ANTI_SEIZE_WEEKDAY,
        CONF_ANTI_SEIZE_HOUR: DEFAULT_ANTI_SEIZE_HOUR,
        CONF_ANTI_SEIZE_MINUTE: DEFAULT_ANTI_SEIZE_MINUTE,
        CONF_ANTI_SEIZE_DURATION: DEFAULT_ANTI_SEIZE_DURATION,
    }


class OpenHydronicOptionsFlow(OptionsFlow):
    """Zone mapping, master manager and hydraulic timings."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        # Kept here: Home Assistant only provides self.config_entry from 2024.11,
        # and deprecates handing it in again from 2025.12.
        self._entry = config_entry
        self._options: dict[str, Any] = {}
        self._editing_zone: str | None = None
        self._board: Board | None = None
        self._free: list[int] = []

    # -- helpers -------------------------------------------------------
    @property
    def _zones(self) -> list[dict[str, Any]]:
        return list(self._options.get(CONF_ZONES, []))

    def _zone_labels(self) -> dict[str, str]:
        return {
            zone[CONF_ZONE_ID]: (
                f"{zone[CONF_ZONE_NAME]} ({zone[CONF_RELAY_ENTITY]})"
                + (" [bypass]" if zone.get(CONF_IS_BYPASS) else "")
            )
            for zone in self._zones
        }

    def _save(self) -> ConfigFlowResult:
        return self.async_create_entry(title="", data=self._options)

    # -- menu ----------------------------------------------------------
    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if not self._options:
            self._options = {**_default_options(), **dict(self._entry.options)}

        self._find_free_relays()
        menu = ["import_zones"] if self._free else []
        menu.append("add_zone")
        if self._zones:
            menu += ["edit_zone", "remove_zone"]
        menu += ["master", "timings", "protections"]
        return self.async_show_menu(step_id="init", menu_options=menu)

    # -- zones ---------------------------------------------------------
    def _find_free_relays(self) -> None:
        """Relays of the adopted board that no zone of any entry uses yet."""
        data = self._entry.data
        self._board = async_get_board(
            self.hass,
            mac=data.get(CONF_MAC),
            host=data.get(CONF_HOST),
            node_name=data.get(CONF_NODE_NAME),
        )
        self._free = []
        if self._board is not None:
            taken = taken_relays(self.hass.config_entries.async_entries(DOMAIN))
            self._free = free_channels(self._board, taken)

    async def async_step_import_zones(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Map the relays the board has that no zone uses, in one form."""
        board = self._board
        if board is None or not self._free:
            return await self.async_step_init()
        errors: dict[str, str] = {}

        if user_input is not None:
            created = zones_from_form(
                board, user_input, new_id=_new_zone_id, channels=self._free
            )
            if unfinished_sections(board, user_input, channels=self._free):
                errors["base"] = "sensor_required"
            elif created:
                self._options[CONF_ZONES] = self._zones + created
                return self._save()
            else:
                errors["base"] = "no_zone_selected"

        return self.async_show_form(
            step_id="import_zones",
            data_schema=_zones_schema(board, channels=self._free, previous=user_input),
            errors=errors,
            description_placeholders={
                "name": self._entry.title,
                "count": str(len(self._free)),
            },
        )

    async def async_step_add_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            error = self._validate_zone(user_input, zone_id=None)
            if error:
                errors["base"] = error
            else:
                zones = self._zones
                zones.append({CONF_ZONE_ID: uuid.uuid4().hex[:8], **user_input})
                self._options[CONF_ZONES] = zones
                return self._save()

        return self.async_show_form(
            step_id="add_zone", data_schema=_zone_schema(), errors=errors
        )

    async def async_step_edit_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._editing_zone = user_input[CONF_ZONE_ID]
            return await self.async_step_edit_zone_details()

        return self.async_show_form(
            step_id="edit_zone",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZONE_ID): vol.In(self._zone_labels()),
                }
            ),
        )

    async def async_step_edit_zone_details(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        zone = next(z for z in self._zones if z[CONF_ZONE_ID] == self._editing_zone)
        errors: dict[str, str] = {}

        if user_input is not None:
            error = self._validate_zone(user_input, zone_id=self._editing_zone)
            if error:
                errors["base"] = error
            else:
                zones = [
                    {CONF_ZONE_ID: self._editing_zone, **user_input}
                    if z[CONF_ZONE_ID] == self._editing_zone
                    else z
                    for z in self._zones
                ]
                self._options[CONF_ZONES] = zones
                return self._save()

        return self.async_show_form(
            step_id="edit_zone_details",
            data_schema=_zone_schema(zone),
            errors=errors,
            description_placeholders={"name": zone[CONF_ZONE_NAME]},
        )

    async def async_step_remove_zone(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            removed = set(user_input.get(CONF_ZONES, []))
            self._options[CONF_ZONES] = [
                z for z in self._zones if z[CONF_ZONE_ID] not in removed
            ]
            return self._save()

        return self.async_show_form(
            step_id="remove_zone",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ZONES, default=[]): cv_multi_select(
                        self._zone_labels()
                    )
                }
            ),
        )

    def _validate_zone(
        self, user_input: dict[str, Any], zone_id: str | None
    ) -> str | None:
        """A relay may only belong to one zone, and only one bypass may exist."""
        relay = user_input.get(CONF_RELAY_ENTITY)
        for zone in self._zones:
            if zone[CONF_ZONE_ID] == zone_id:
                continue
            if zone[CONF_RELAY_ENTITY] == relay:
                return "relay_in_use"
            if user_input.get(CONF_IS_BYPASS) and zone.get(CONF_IS_BYPASS):
                return "bypass_exists"
        if not user_input.get(CONF_IS_BYPASS) and not user_input.get(CONF_SENSOR_ENTITY):
            return "sensor_required"
        return None

    # -- master --------------------------------------------------------
    async def async_step_master(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            mode = user_input[CONF_MASTER_MODE]
            entity = user_input.get(CONF_MASTER_ENTITY)
            if mode in (MASTER_RELAY, MASTER_EXTERNAL) and not entity:
                errors["base"] = "master_entity_required"
            elif entity and any(
                z[CONF_RELAY_ENTITY] == entity for z in self._zones
            ):
                errors["base"] = "master_is_zone"
            else:
                self._options[CONF_MASTER_MODE] = mode
                self._options[CONF_MASTER_ENTITY] = entity if mode != MASTER_DISABLED else None
                return self._save()

        current = self._options
        return self.async_show_form(
            step_id="master",
            errors=errors,
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MASTER_MODE,
                        default=current.get(CONF_MASTER_MODE, MASTER_DISABLED),
                    ): selector.SelectSelector(
                        selector.SelectSelectorConfig(
                            options=MASTER_MODES,
                            translation_key="master_mode",
                            mode=selector.SelectSelectorMode.LIST,
                        )
                    ),
                    vol.Optional(
                        CONF_MASTER_ENTITY,
                        description={
                            "suggested_value": current.get(CONF_MASTER_ENTITY)
                        },
                    ): _relay_selector(),
                }
            ),
        )

    # -- timings -------------------------------------------------------
    async def async_step_timings(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(
                {key: int(value) if key != CONF_HYSTERESIS else float(value)
                 for key, value in user_input.items()}
            )
            return self._save()

        current = self._options
        return self.async_show_form(
            step_id="timings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_HYSTERESIS,
                        default=current.get(CONF_HYSTERESIS, DEFAULT_HYSTERESIS),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0.1, max=2.0, step=0.1, unit_of_measurement="°C",
                            mode=selector.NumberSelectorMode.BOX,
                        )
                    ),
                    vol.Required(
                        CONF_MASTER_START_DELAY,
                        default=current.get(
                            CONF_MASTER_START_DELAY, DEFAULT_MASTER_START_DELAY
                        ),
                    ): _seconds_selector(0, 900),
                    vol.Required(
                        CONF_HEAT_PURGE_DELAY,
                        default=current.get(
                            CONF_HEAT_PURGE_DELAY, DEFAULT_HEAT_PURGE_DELAY
                        ),
                    ): _seconds_selector(0, 900),
                    vol.Required(
                        CONF_MIN_RUN_TIME,
                        default=current.get(CONF_MIN_RUN_TIME, DEFAULT_MIN_RUN_TIME),
                    ): _seconds_selector(0, 3600),
                    vol.Required(
                        CONF_MIN_OFF_TIME,
                        default=current.get(CONF_MIN_OFF_TIME, DEFAULT_MIN_OFF_TIME),
                    ): _seconds_selector(0, 3600),
                }
            ),
        )

    # -- protections ---------------------------------------------------
    async def async_step_protections(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            self._options.update(user_input)
            return self._save()

        current = self._options
        return self.async_show_form(
            step_id="protections",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SENSOR_TIMEOUT,
                        default=current.get(
                            CONF_SENSOR_TIMEOUT, DEFAULT_SENSOR_TIMEOUT
                        ),
                    ): _seconds_selector(300, 86400),
                    vol.Required(
                        CONF_AIR_PURGE_DURATION,
                        default=current.get(
                            CONF_AIR_PURGE_DURATION, DEFAULT_AIR_PURGE_DURATION
                        ),
                    ): _seconds_selector(60, 7200),
                    vol.Required(
                        CONF_ANTI_SEIZE_ENABLED,
                        default=current.get(CONF_ANTI_SEIZE_ENABLED, True),
                    ): selector.BooleanSelector(),
                    vol.Required(
                        CONF_ANTI_SEIZE_WEEKDAY,
                        default=current.get(
                            CONF_ANTI_SEIZE_WEEKDAY, DEFAULT_ANTI_SEIZE_WEEKDAY
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=6, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_ANTI_SEIZE_HOUR,
                        default=current.get(
                            CONF_ANTI_SEIZE_HOUR, DEFAULT_ANTI_SEIZE_HOUR
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=23, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_ANTI_SEIZE_MINUTE,
                        default=current.get(
                            CONF_ANTI_SEIZE_MINUTE, DEFAULT_ANTI_SEIZE_MINUTE
                        ),
                    ): selector.NumberSelector(
                        selector.NumberSelectorConfig(
                            min=0, max=59, step=1, mode=selector.NumberSelectorMode.BOX
                        )
                    ),
                    vol.Required(
                        CONF_ANTI_SEIZE_DURATION,
                        default=current.get(
                            CONF_ANTI_SEIZE_DURATION, DEFAULT_ANTI_SEIZE_DURATION
                        ),
                    ): _seconds_selector(60, 1800),
                }
            ),
        )


def cv_multi_select(options: dict[str, str]) -> selector.SelectSelector:
    """Multi-select over the configured zones."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                selector.SelectOptionDict(value=value, label=label)
                for value, label in options.items()
            ],
            multiple=True,
            mode=selector.SelectSelectorMode.LIST,
        )
    )
