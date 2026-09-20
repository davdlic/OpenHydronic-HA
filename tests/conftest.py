# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Minimal Home Assistant stand-ins.

The decision core is pure Python, so the tests run without installing Home
Assistant. Only the names imported at module level need to exist.
"""

from __future__ import annotations

import sys
import types
from datetime import datetime, timezone
from pathlib import Path
from typing import Generic, TypeVar
from unittest.mock import MagicMock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

_T = TypeVar("_T")


def _module(name: str, **attrs) -> types.ModuleType:
    module = types.ModuleType(name)
    for key, value in attrs.items():
        setattr(module, key, value)
    sys.modules[name] = module
    return module


class _DataUpdateCoordinator(Generic[_T]):
    def __init__(self, hass, logger, name=None, update_interval=None, **kwargs):
        self.hass = hass
        self.logger = logger
        self.name = name
        self.update_interval = update_interval
        self.data = None

    async def async_request_refresh(self) -> None:
        return None

    async def async_config_entry_first_refresh(self) -> None:
        return None


def _install() -> None:
    if "homeassistant" in sys.modules:
        return

    _module("voluptuous", **{"__getattr__": lambda name: MagicMock()})
    sys.modules["voluptuous"] = MagicMock()

    homeassistant = _module("homeassistant")

    _module("homeassistant.config_entries", ConfigEntry=type("ConfigEntry", (), {}))
    _module(
        "homeassistant.const",
        ATTR_ENTITY_ID="entity_id",
        SERVICE_TURN_ON="turn_on",
        SERVICE_TURN_OFF="turn_off",
        STATE_ON="on",
        STATE_OFF="off",
        STATE_UNAVAILABLE="unavailable",
        STATE_UNKNOWN="unknown",
    )
    _module(
        "homeassistant.core",
        Event=type("Event", (), {}),
        HomeAssistant=type("HomeAssistant", (), {}),
        ServiceCall=type("ServiceCall", (), {}),
        callback=lambda func: func,
    )

    components = _module("homeassistant.components")
    persistent_notification = _module(
        "homeassistant.components.persistent_notification",
        async_create=lambda *args, **kwargs: None,
        async_dismiss=lambda *args, **kwargs: None,
    )
    components.persistent_notification = persistent_notification

    helpers = _module("homeassistant.helpers")
    _module(
        "homeassistant.helpers.event",
        async_track_state_change_event=lambda *args, **kwargs: (lambda: None),
        async_track_time_change=lambda *args, **kwargs: (lambda: None),
    )
    _module("homeassistant.helpers.storage", Store=MagicMock())
    _module(
        "homeassistant.helpers.update_coordinator",
        DataUpdateCoordinator=_DataUpdateCoordinator,
        CoordinatorEntity=object,
    )
    helpers.config_validation = MagicMock()
    sys.modules["homeassistant.helpers.config_validation"] = helpers.config_validation
    helpers.typing = MagicMock()
    sys.modules["homeassistant.helpers.typing"] = helpers.typing

    util = _module(
        "homeassistant.util",
        slugify=lambda value: str(value).lower().replace("-", "_").replace(".", "_"),
    )
    dt_module = _module(
        "homeassistant.util.dt",
        utcnow=lambda: datetime.now(timezone.utc),
        as_local=lambda value: value,
    )
    util.dt = dt_module
    homeassistant.helpers = helpers
    homeassistant.util = util
    homeassistant.components = components


_install()
