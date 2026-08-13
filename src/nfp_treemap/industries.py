"""Build the CES industry hierarchy from ce.industry, annotated with NAICS text."""
from __future__ import annotations

import datetime as _dt
import json
import time
from pathlib import Path

import requests

from . import naics as naics_mod
from .config import (
    AGGREGATE_PARENTS,
    CACHE_DIR,
    CE_INDUSTRY_URL,
    INDUSTRIES_JSON,
    SUPERSECTOR_ALIASES,
    USER_AGENT,
)

_CE_INDUSTRY = CACHE_DIR / "ce.industry"
_MAX_AGE_DAYS = 30  # BLS revises the hierarchy at the annual benchmark


def download_ce_industry(force: bool = False) -> Path:
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if _CE_INDUSTRY.exists() and not force:
        age_days = (time.time() - _CE_INDUSTRY.stat().st_mtime) / 86400
        if age_days < _MAX_AGE_DAYS:
            return _CE_INDUSTRY
    resp = requests.get(
        CE_INDUSTRY_URL, headers={"User-Agent": USER_AGENT}, timeout=120
    )
    resp.raise_for_status()
    _CE_INDUSTRY.write_text(resp.text)
    return _CE_INDUSTRY


def _parse_rows(path: Path) -> list[dict]:
    lines = path.read_text().splitlines()
    rows = []
    for line in lines[1:]:
        parts = line.rstrip("\n").split("\t")
        if len(parts) < 7:
            continue
        rows.append(
            {
                "code": parts[0].strip(),
                "naics_raw": parts[1].strip(),
                "publishing_status": parts[2].strip(),
                "name": parts[3].strip(),
                "level": int(parts[4]),
                "sort": int(parts[6]),
            }
        )
    rows.sort(key=lambda r: r["sort"])
    return rows


def _structural_parent(row: dict, by_code: dict[str, dict]) -> str | None:
    """Derive the parent from the industry code itself.

    A CES code is a 2-digit supersector plus 6 digits that behave like a NAICS
    code right-padded with zeros, so dropping one significant digit at a time
    walks up the tree: 20238110 -> 20238100 -> 20238000.

    Rows whose naics_code reads "part NNNN" are CES's residential /
    nonresidential splits. They carry a 01/02 suffix and sit at the *same*
    display_level as the total they split, so a residential detail row must
    attach to the residential parent rather than to the total.
    """
    code = row["code"]
    supersector, rest = code[:2], code[2:]

    part = rest[-2:] if row["naics_raw"].startswith("part ") else None
    main = f"{supersector}{rest[:-2]}00" if part else code

    significant = main[2:].rstrip("0")
    for length in range(len(significant) - 1, 0, -1):
        candidate = supersector + significant[:length].ljust(6, "0")
        parent = by_code.get(candidate)
        if parent and parent["level"] < row["level"]:
            if part:
                sibling = by_code.get(candidate[:-2] + part)
                if sibling and sibling["level"] < row["level"]:
                    return sibling["code"]
            return candidate

    # Detail with no intermediate parent falls back to its supersector root,
    # following the grouping aliases (wholesale/retail/transport -> trade).
    for prefix in (supersector, SUPERSECTOR_ALIASES.get(supersector, supersector)):
        candidate = prefix + "000000"
        parent = by_code.get(candidate)
        if parent and parent["level"] < row["level"]:
            return candidate
    return None


def _assign_parents(rows: list[dict]) -> None:
    """Parent links, code structure first.

    An earlier version used "nearest preceding row in sort_sequence order with
    a strictly smaller display_level". That reports zero orphans but is quietly
    wrong wherever CES interleaves its part-splits: every level-5 and level-6
    specialty trade contractor row attached to *Nonresidential* specialty trade
    contractors - the last level-4 row before them - instead of to Specialty
    trade contractors. 52 rows were mis-parented. The code structure is
    authoritative, so it is used first and the positional scan is kept only as
    a last resort.
    """
    by_code = {r["code"]: r for r in rows}

    for row in rows:
        row["parent_code"] = AGGREGATE_PARENTS.get(row["code"]) or (
            _structural_parent(row, by_code) if row["level"] > 0 else None
        )

    # Positional fallback for anything the structure could not resolve.
    stack: list[dict] = []
    for row in rows:
        while stack and stack[-1]["level"] >= row["level"]:
            stack.pop()
        if row["level"] > 0 and not row["parent_code"] and stack:
            row["parent_code"] = stack[-1]["code"]
        stack.append(row)

    _assert_acyclic(by_code)


def _assert_acyclic(by_code: dict[str, dict]) -> None:
    for row in by_code.values():
        seen = {row["code"]}
        cur = row.get("parent_code")
        while cur:
            if cur in seen:
                raise ValueError(f"cycle in hierarchy at {row['code']} via {cur}")
            seen.add(cur)
            cur = by_code[cur].get("parent_code")


def _assign_supersectors(rows: list[dict]) -> None:
    by_code = {r["code"]: r for r in rows}
    # Names for the 2-digit supersector prefixes come from the level<=2 rows.
    names: dict[str, str] = {}
    for row in rows:
        if row["level"] <= 2:
            names.setdefault(row["code"][:2], row["name"])

    for row in rows:
        prefix = row["code"][:2]
        group = SUPERSECTOR_ALIASES.get(prefix, prefix)
        row["supersector_code"] = group
        row["supersector_name"] = names.get(group) or names.get(prefix) or row["name"]
        # Level 0/1 rows are overlapping aggregates, not real groups.
        if row["level"] <= 1:
            row["supersector_code"] = row["code"][:2]
            row["supersector_name"] = row["name"]
    assert by_code  # silence unused-var linting in older tooling


def _flag_composites(rows: list[dict]) -> None:
    """Mark rows that duplicate their own same-level siblings.

    CES publishes a few roll-ups at the *same* display_level as the components
    they contain, so a flat level view double-counts them. At level 4, "Health
    care" (NAICS 621,2,3) is exactly Ambulatory + Hospitals + Nursing, and its
    +20.3k is those three added together. Same shape for "Specialty trade
    contractors" (its residential and nonresidential parts) and, at level 5,
    "Motor vehicles and parts".

    Detected structurally rather than by hard-coded code, so a future benchmark
    that adds or removes one is handled without a source change.
    """
    expanded: dict[str, frozenset[str]] = {}
    partial: dict[str, bool] = {}
    for row in rows:
        codes, is_partial = naics_mod.expand_ces_naics(row["naics_raw"])
        expanded[row["code"]] = frozenset(codes)
        partial[row["code"]] = is_partial

    siblings: dict[tuple, list[dict]] = {}
    for row in rows:
        siblings.setdefault((row["parent_code"], row["level"]), []).append(row)

    for row in rows:
        row["composite"] = False
        mine = expanded[row["code"]]
        # A "part N" row is a genuine subdivision, never the roll-up.
        if not mine or partial[row["code"]]:
            continue
        peers = [
            p for p in siblings[(row["parent_code"], row["level"])]
            if p["code"] != row["code"] and expanded[p["code"]]
        ]

        # The row is the total of two or more "part N" splits of itself.
        parts = [p for p in peers if partial[p["code"]] and expanded[p["code"]] == mine]
        if len(parts) >= 2:
            row["composite"] = True
            continue

        # Or its siblings partition its NAICS set exactly, without overlap.
        comps = [
            p for p in peers
            if not partial[p["code"]] and expanded[p["code"]] < mine
        ]
        if len(comps) >= 2:
            union: set[str] = set().union(*(expanded[p["code"]] for p in comps))
            disjoint = sum(len(expanded[p["code"]]) for p in comps) == len(union)
            if union == mine and disjoint:
                row["composite"] = True


def build(force: bool = False) -> list[dict]:
    rows = _parse_rows(download_ce_industry(force=force))
    _assign_parents(rows)
    _assign_supersectors(rows)
    _flag_composites(rows)

    table = naics_mod.load_naics_table(force=force)
    for row in rows:
        row["naics"] = naics_mod.describe(row["naics_raw"], table)
    return rows


def write(force: bool = False) -> list[dict]:
    rows = build(force=force)
    INDUSTRIES_JSON.parent.mkdir(parents=True, exist_ok=True)
    INDUSTRIES_JSON.write_text(
        json.dumps(
            {
                "generated": _dt.datetime.now().isoformat(timespec="seconds"),
                "industries": rows,
            },
            indent=1,
        )
    )
    return rows


def load() -> list[dict]:
    return json.loads(INDUSTRIES_JSON.read_text())["industries"]


if __name__ == "__main__":  # pragma: no cover
    built = write()
    joined = sum(1 for r in built if r["naics"])
    unmatched = sum(
        1
        for r in built
        if r["naics"] and any(c["match"] == "unmatched" for c in r["naics"]["codes"])
    )
    orphans = sum(1 for r in built if r["level"] > 0 and not r["parent_code"])
    print(f"industries      {len(built)}")
    print(f"NAICS joined    {joined}  (aggregates without NAICS: {len(built) - joined})")
    print(f"unmatched NAICS {unmatched}")
    print(f"orphans         {orphans}")
    print(f"wrote           {INDUSTRIES_JSON}")
