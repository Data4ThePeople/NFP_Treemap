"""The CES industry tree and its join to the observation cache."""
from __future__ import annotations

import pytest

from nfp_treemap import industries as industries_mod
from nfp_treemap.config import OBSERVATIONS_PARQUET


@pytest.fixture(scope="module")
def rows():
    return industries_mod.build()


@pytest.fixture(scope="module")
def by_code(rows):
    return {r["code"]: r for r in rows}


def test_row_count_and_levels(rows):
    assert len(rows) == 850
    levels = {}
    for row in rows:
        levels[row["level"]] = levels.get(row["level"], 0) + 1
    assert levels[0] == 1
    assert levels[4] == 84


def test_no_orphans_and_single_root(rows):
    roots = [r for r in rows if r["parent_code"] is None]
    assert [r["code"] for r in roots] == ["00000000"]


def test_no_cycles_and_every_row_reaches_root(by_code):
    for row in by_code.values():
        seen = {row["code"]}
        cur = row["parent_code"]
        while cur:
            assert cur not in seen, f"cycle at {row['code']}"
            seen.add(cur)
            cur = by_code[cur]["parent_code"]
        assert "00000000" in seen or row["code"] == "00000000"


def test_parent_level_is_always_shallower(by_code):
    for row in by_code.values():
        if row["parent_code"]:
            assert by_code[row["parent_code"]]["level"] < row["level"]


@pytest.mark.parametrize(
    "code,parent_name",
    [
        # The part-splits are the case a positional scan gets wrong: these
        # level-5 rows follow "Nonresidential specialty trade contractors" in
        # sort order but belong to the totals and to the matching part.
        ("20238100", "Specialty trade contractors"),
        ("20238101", "Residential specialty trade contractors"),
        ("20238102", "Nonresidential specialty trade contractors"),
        ("20238110", "Foundation, structure, and building exterior contractors"),
        ("20238210", "Building equipment contractors"),
        # A level skip: Logging is level 5 directly under level-2.
        ("10113300", "Mining and logging"),
        # Explicit aggregate map.
        ("90000000", "Service-providing"),
        ("42000000", "Trade, transportation, and utilities"),
        ("31000000", "Manufacturing"),
    ],
)
def test_known_parents(by_code, code, parent_name):
    assert by_code[by_code[code]["parent_code"]]["name"] == parent_name


def test_naics_join_is_complete(rows):
    joined = [r for r in rows if r["naics"]]
    aggregates = [r for r in rows if not r["naics"]]
    assert len(joined) == 813
    assert len(aggregates) == 37
    unmatched = [
        r["code"]
        for r in joined
        if any(c["match"] == "unmatched" for c in r["naics"]["codes"])
    ]
    assert unmatched == []


@pytest.mark.skipif(
    not OBSERVATIONS_PARQUET.exists(), reason="run nfp_treemap.fetch --backfill first"
)
def test_totals_reconcile_against_total_nonfarm():
    """Goods-producing + Private service-providing + Government = Total nonfarm.

    Guards against a mangled hierarchy or a bad fetch: these three partition
    the survey, so their sum must match the headline series.
    """
    import pandas as pd

    frame = pd.read_parquet(OBSERVATIONS_PARQUET)
    latest = frame["date"].max()
    snapshot = frame[frame["date"] == latest].set_index("industry_code")["employees"]

    total = snapshot["00000000"]
    parts = snapshot[["06000000", "08000000", "90000000"]].sum()
    assert abs(total - parts) < 1.0, f"{total} vs {parts}"


def test_composite_rollups_are_flagged(rows):
    """CES publishes a few roll-ups at the same level as their own components."""
    flagged = {r["code"]: r["name"] for r in rows if r.get("composite")}
    assert flagged == {
        "20238000": "Specialty trade contractors",
        "31336001": "Motor vehicles and parts",
        "65620001": "Health care",
    }


def test_part_splits_are_not_flagged_as_composites(by_code):
    """A 'part N' row is a genuine subdivision, not a duplicate roll-up."""
    for code in ("20238001", "20238002", "20238101", "20238102"):
        assert by_code[code]["composite"] is False, code


@pytest.mark.skipif(
    not OBSERVATIONS_PARQUET.exists(), reason="run nfp_treemap.fetch --backfill first"
)
def test_dropping_composites_stops_the_double_count(by_code):
    """Excluding the roll-up must put the children's total back on its parent.

    Compared on employment LEVELS, not month-over-month changes. A change is a
    small difference of large numbers, and with each series stored to one
    decimal the rounding noise across six or seven children (+-0.35) is the
    same size as the parent's whole move - which made the comparison flip sign
    for Transportation equipment even though including the roll-up
    double-counts 956.6k of employment.
    """
    import pandas as pd

    frame = pd.read_parquet(OBSERVATIONS_PARQUET)
    # Not frame["date"].max(): CES publishes detailed industries a month behind
    # the aggregates, so the newest month has the parents but none of the
    # children. Use the newest month every series actually reports.
    counts = frame.groupby("date")["industry_code"].nunique()
    latest = counts[counts == counts.max()].index.max()
    level = frame[frame["date"] == latest].set_index("industry_code")["employees"]

    composites = [r for r in by_code.values() if r["composite"]]
    assert composites

    for comp in composites:
        siblings = [
            r for r in by_code.values()
            if r["parent_code"] == comp["parent_code"]
            and r["level"] == comp["level"]
            and r["code"] in level.index
        ]
        parent = level[comp["parent_code"]]
        without = sum(level[r["code"]] for r in siblings if not r["composite"])
        with_rollup = sum(level[r["code"]] for r in siblings)

        # Without the roll-up the children reconcile to within CES's own
        # rounding and independent seasonal adjustment.
        assert abs(without - parent) <= 1.0, (
            f"{comp['name']}: children {without:.1f} vs parent {parent:.1f}"
        )
        # With it they overshoot by roughly the roll-up's own size.
        assert with_rollup - parent > 0.5 * level[comp["code"]], comp["name"]


@pytest.mark.skipif(
    not OBSERVATIONS_PARQUET.exists(), reason="run nfp_treemap.fetch --backfill first"
)
def test_health_care_reconciles_exactly(by_code):
    """The case that surfaced this: 61.3k double-counted vs a true 41.0k."""
    import pandas as pd

    frame = pd.read_parquet(OBSERVATIONS_PARQUET)
    months = pd.to_datetime(["2026-05-01", "2026-06-01"])
    snap = frame[frame["date"].isin(months)].pivot(
        index="industry_code", columns="date", values="employees"
    )
    change = snap[months[1]] - snap[months[0]]

    kids = [
        r for r in by_code.values()
        if r["parent_code"] == "65620000" and r["level"] == 4
    ]
    assert round(sum(change[r["code"]] for r in kids), 1) == 61.3
    kept = [r for r in kids if not r["composite"]]
    assert round(sum(change[r["code"]] for r in kept), 1) == 41.0
    assert round(float(change["65620000"]), 1) == 41.0
