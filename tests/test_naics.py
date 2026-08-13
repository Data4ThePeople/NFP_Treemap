"""The CES naics_code shorthand and its join to the Census NAICS table."""
from __future__ import annotations

import pytest

from nfp_treemap import naics


@pytest.mark.parametrize(
    "raw,expected,partial",
    [
        ("722", ["722"], False),
        ("-", [], False),
        ("", [], False),
        ("part 238", ["238"], True),
        ("part 2382", ["2382"], True),
        # Each fragment replaces the trailing digits of the PREVIOUS code.
        ("21221,3,9", ["21221", "21223", "21229"], False),
        ("212311,3,9", ["212311", "212313", "212319"], False),
        ("3274,9", ["3274", "3279"], False),
        # Semicolon behaves like a comma. Expanding relative to the base
        # instead of the previous code would give 332209 here, not 332999.
        ("332200;991,9", ["332200", "332991", "332999"], False),
        # Inclusive ranges.
        (
            "334512,4,6-9",
            ["334512", "334514", "334516", "334517", "334518", "334519"],
            False,
        ),
        (
            "221111,3-8",
            ["221111", "221113", "221114", "221115", "221116", "221117", "221118"],
            False,
        ),
    ],
)
def test_expand_ces_naics(raw, expected, partial):
    codes, is_partial = naics.expand_ces_naics(raw)
    assert codes == expected
    assert is_partial is partial


def test_trilateral_marker_stripped_only_after_lowercase():
    assert naics._clean_title("Food Services and Drinking PlacesT") == (
        "Food Services and Drinking Places"
    )
    # A trailing capital preceded by another capital is part of the name.
    assert naics._clean_title("Widgets NAFTA") == "Widgets NAFTA"


@pytest.fixture(scope="module")
def table():
    return naics.load_naics_table()


def test_table_shape(table):
    assert len(table) > 2000
    # Every description is populated: the 154 literal "NULL" rows must have
    # been resolved by walking down to a child that has text.
    assert all(entry["description"] for entry in table.values())


def test_null_description_resolves_from_child(table):
    # 7225 ships as NULL in the source; 72251 carries the text.
    assert table["7225"]["description"]
    assert table["7225"]["description"] == table["72251"]["description"]


@pytest.mark.parametrize(
    "code,expected,match",
    [
        ("722", "722", "exact"),
        ("5250", "525", "rolled_up"),   # CES zero-pads to a uniform width
        ("3160", "316", "rolled_up"),
        ("334518", "33451", "rolled_up"),  # discontinued in the 2022 revision
    ],
)
def test_resolve_code(table, code, expected, match):
    resolved, kind = naics.resolve_code(code, table)
    assert (resolved, kind) == (expected, match)


def test_describe_partial_flags_and_titles(table):
    described = naics.describe("part 238", table)
    assert described["partial"] is True
    assert described["codes"][0]["title"] == "Specialty Trade Contractors"
    assert described["description"]

    assert naics.describe("-", table) is None
