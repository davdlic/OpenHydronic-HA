# OpenHydronic-HA - Home Assistant integration + Lovelace card for OpenHydronic
# Copyright (C) 2026 David Lopes (https://github.com/davdlic)
# Licensed under the GNU General Public License v3.0 - see LICENSE
"""Every step, error and choice the flows can show has a text, in both languages.

A missing key does not fail anything in Home Assistant: the user just sees the
raw key. So it is checked here.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

COMPONENT = Path(__file__).resolve().parents[1] / "custom_components" / "openhydronic"
STRINGS = json.loads((COMPONENT / "strings.json").read_text(encoding="utf-8"))
EN = json.loads((COMPONENT / "translations" / "en.json").read_text(encoding="utf-8"))
PT = json.loads((COMPONENT / "translations" / "pt.json").read_text(encoding="utf-8"))

CONFIG_STEPS = {"user", "discovery_confirm", "not_adopted", "no_zones", "zones"}
OPTION_STEPS = {
    "init", "add_zone", "edit_zone", "edit_zone_details", "remove_zone",
    "master", "timings", "protections", "import_zones",
}
CONFIG_ERRORS = {
    "relay_in_use", "master_entity_required", "master_is_zone",
    "master_switch_missing", "master_switch_failed", "sensor_required",
}
CONFIG_ABORTS = {"already_configured", "already_in_progress"}
# What the flows hand to description_placeholders, per step.
PLACEHOLDERS = {
    ("config", "discovery_confirm"): {"name", "host"},
    ("config", "not_adopted"): {"name", "host"},
    ("config", "no_zones"): {"name", "host"},
    ("config", "zones"): {"name", "host", "count"},
    ("config", "wait_board"): {"name", "host"},
    ("options", "import_zones"): {"name", "count"},
    ("options", "edit_zone_details"): {"name"},
}


def paths(node, prefix=""):
    out = set()
    for key, value in node.items():
        out.add(prefix + key)
        if isinstance(value, dict):
            out |= paths(value, prefix + key + ".")
    return out


def test_english_translation_is_the_source_file():
    assert EN == STRINGS


def test_portuguese_has_exactly_the_same_keys():
    assert paths(PT) == paths(STRINGS)


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_every_step_the_flows_use_has_a_text(lang):
    assert CONFIG_STEPS <= set(lang["config"]["step"])
    assert OPTION_STEPS <= set(lang["options"]["step"])
    assert "wait_board" in lang["config"]["progress"]
    assert CONFIG_ERRORS <= set(lang["config"]["error"])
    assert CONFIG_ABORTS <= set(lang["config"]["abort"])
    assert "no_zone_selected" in lang["options"]["error"]


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_the_relay_sections_cover_all_eight_channels(lang):
    for steps in (lang["config"]["step"]["zones"], lang["options"]["step"]["import_zones"]):
        assert set(steps["sections"]) == {f"zone_{n}" for n in range(1, 9)}
        for section in steps["sections"].values():
            assert {"name", "sensor_entity"} <= set(section["data"])
            assert set(section["data_description"]) <= set(section["data"])


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_menus_offer_check_again_and_skip(lang):
    for step in ("not_adopted", "no_zones"):
        assert set(lang["config"]["step"][step]["menu_options"]) == {"retry", "skip"}
    assert "import_zones" in lang["options"]["step"]["init"]["menu_options"]


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_the_master_question_has_all_three_answers(lang):
    assert set(lang["selector"]["master_choice"]["options"]) == {"none", "board", "entity"}
    assert {"master_choice", "master_entity"} <= set(lang["config"]["step"]["zones"]["data"])


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_the_reminder_has_a_title_and_a_description(lang):
    issue = lang["issues"]["zones_unmapped"]
    assert issue["title"] and issue["description"]


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_the_password_repair_can_be_filled_in(lang):
    issue = lang["issues"]["default_password"]
    flow = issue["fix_flow"]
    assert issue["title"]
    assert flow["step"]["confirm"]["title"] and flow["step"]["confirm"]["description"]
    assert flow["step"]["confirm"]["data"]["password"]
    assert {"password_short", "password_long", "password_chars", "password_failed"} <= set(flow["error"])
    for text in (issue["title"], flow["step"]["confirm"]["title"], flow["step"]["confirm"]["description"]):
        assert set(re.findall(r"{(\w+)}", text)) <= {"name"}


@pytest.mark.parametrize("lang", [STRINGS, PT], ids=["en", "pt"])
def test_placeholders_are_only_ones_the_flows_provide(lang):
    for (kind, step), allowed in PLACEHOLDERS.items():
        node = lang[kind]["progress"][step] if step == "wait_board" else lang[kind]["step"][step]
        text = node if isinstance(node, str) else node.get("description", "")
        used = set(re.findall(r"{(\w+)}", text))
        assert used <= allowed, (kind, step, used - allowed)
    assert set(re.findall(r"{(\w+)}", lang["issues"]["zones_unmapped"]["title"])) <= {"name"}
    assert set(re.findall(r"{(\w+)}", lang["issues"]["zones_unmapped"]["description"])) <= {"name"}
