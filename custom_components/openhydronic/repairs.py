# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Repairs that end in a form: setting the board's own password.

The password travels through the ESPHome integration, over its encrypted API,
to the board's `Board Password` entity. The board is never contacted from here.
"""

from __future__ import annotations

import asyncio

import voluptuous as vol
from homeassistant.components.repairs import RepairsFlow
from homeassistant.const import STATE_OFF, STATE_UNAVAILABLE
from homeassistant.core import Event, HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import selector
from homeassistant.helpers.event import async_track_state_change_event

from . import ISSUE_DEFAULT_PASSWORD
from .board import async_get_board
from .const import CONF_HOST, CONF_MAC, CONF_NODE_NAME

CONF_PASSWORD = "password"
# The board answers before it checks and drops the rest, so refuse here.
MIN_PASSWORD = 8
MAX_PASSWORD = 64  # bytes; printable ASCII, so also characters
# How long to wait for the board to say it left the public password.
CONFIRM_SECONDS = 5


def password_problem(password: str) -> str | None:
    """The error key for a password the board would drop, or None."""
    if any(not 0x20 <= ord(char) <= 0x7E for char in password):
        return "password_chars"
    if len(password) < MIN_PASSWORD:
        return "password_short"
    if len(password) > MAX_PASSWORD:
        return "password_long"
    return None


class DefaultPasswordRepairFlow(RepairsFlow):
    """Asks for a password and hands it to the board."""

    def __init__(self, entry_id: str) -> None:
        self._entry_id = entry_id

    async def async_step_init(self, user_input: dict[str, str] | None = None) -> FlowResult:
        return await self.async_step_confirm()

    async def async_step_confirm(self, user_input: dict[str, str] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        entry = self.hass.config_entries.async_get_entry(self._entry_id)

        if user_input is not None:
            password = user_input[CONF_PASSWORD]
            if problem := password_problem(password):
                errors["base"] = problem
            elif not await self._async_send(password):
                errors["base"] = "password_failed"
            else:
                return self.async_create_entry(data={})

        return self.async_show_form(
            step_id="confirm",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_PASSWORD): selector.TextSelector(
                        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
                    )
                }
            ),
            errors=errors,
            description_placeholders={"name": entry.title if entry else "OpenHydronic"},
        )

    async def _async_send(self, password: str) -> bool:
        """True once the board says it has left the public password."""
        entry = self.hass.config_entries.async_get_entry(self._entry_id)
        if entry is None:
            return False
        board = async_get_board(
            self.hass,
            mac=entry.data.get(CONF_MAC),
            host=entry.data.get(CONF_HOST),
            node_name=entry.data.get(CONF_NODE_NAME),
        )
        if board is None or not board.password_text:
            return False

        # Unknown is normal, the board never publishes it. Unavailable means offline.
        state = self.hass.states.get(board.password_text)
        if state is None or state.state == STATE_UNAVAILABLE:
            return False

        # Listen before sending: the sensor can flip before the call returns.
        left = asyncio.Event()
        stop = None
        sensor = board.default_password
        current = self.hass.states.get(sensor) if sensor else None
        if current is None or current.state == STATE_OFF:
            left.set()
        else:

            @callback
            def _changed(event: Event) -> None:
                new = event.data.get("new_state")
                if new is not None and new.state == STATE_OFF:
                    left.set()

            stop = async_track_state_change_event(self.hass, [sensor], _changed)

        try:
            try:
                await self._async_hand_over(board.password_text, password)
            except (HomeAssistantError, ValueError):
                # Swallow it: Home Assistant's validation error quotes the password.
                return False
            try:
                async with asyncio.timeout(CONFIRM_SECONDS):
                    await left.wait()
            except TimeoutError:
                # The board took it in silence, or is not listening.
                return False
            return True
        finally:
            if stop is not None:
                stop()

    async def _async_hand_over(self, entity_id: str, password: str) -> None:
        """Hand the value to the entity: a service call would put it in the recorder."""
        from homeassistant.helpers import entity_platform

        for platform in entity_platform.async_get_platforms(self.hass, "esphome"):
            entity = platform.entities.get(entity_id)
            if entity is not None:
                if not entity.available:
                    raise HomeAssistantError("The board is not available")
                await entity.async_set_value(password)
                return

        # Not reachable that way: use the service.
        await self.hass.services.async_call(
            "text",
            "set_value",
            {"entity_id": entity_id, "value": password},
            blocking=True,
        )


async def async_create_fix_flow(
    hass: HomeAssistant, issue_id: str, data: dict[str, str | int | float | None] | None
) -> RepairsFlow:
    """The flow behind a fixable repair of this integration."""
    if issue_id.startswith(f"{ISSUE_DEFAULT_PASSWORD}_") and data and "entry_id" in data:
        return DefaultPasswordRepairFlow(str(data["entry_id"]))
    raise ValueError(f"No fix flow for {issue_id}")
