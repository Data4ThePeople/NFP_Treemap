"""Join CES industries to official Census 2022 NAICS titles and descriptions.

CES publishes a ``naics_code`` field with five distinct syntaxes and no
documentation of the shorthand. This module decodes all of them and resolves
each to entries in the Census 2022 NAICS description table.

The .xlsx is parsed with the standard library (an .xlsx is a zip of XML), so
openpyxl is not a dependency.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

import requests

from .config import CACHE_DIR, NAICS_DESCRIPTIONS_URL, USER_AGENT

_NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
_NAICS_XLSX = CACHE_DIR / "2022_NAICS_Descriptions.xlsx"


def download_naics(force: bool = False) -> Path:
    """Cache the Census description workbook locally."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    if _NAICS_XLSX.exists() and not force:
        return _NAICS_XLSX
    resp = requests.get(
        NAICS_DESCRIPTIONS_URL, headers={"User-Agent": USER_AGENT}, timeout=120
    )
    resp.raise_for_status()
    _NAICS_XLSX.write_bytes(resp.content)
    return _NAICS_XLSX


def _read_xlsx_rows(path: Path) -> list[list[str]]:
    """Minimal xlsx reader: first worksheet, resolving shared strings."""
    with zipfile.ZipFile(path) as zf:
        shared: list[str] = []
        if "xl/sharedStrings.xml" in zf.namelist():
            root = ET.fromstring(zf.read("xl/sharedStrings.xml"))
            shared = [
                "".join(t.text or "" for t in si.iter(f"{_NS}t"))
                for si in root.findall(f"{_NS}si")
            ]
        sheet = ET.fromstring(zf.read("xl/worksheets/sheet1.xml"))

    rows: list[list[str]] = []
    for row in sheet.iter(f"{_NS}row"):
        cells: list[str] = []
        for cell in row.findall(f"{_NS}c"):
            value = cell.find(f"{_NS}v")
            if value is None or value.text is None:
                cells.append("")
            elif cell.get("t") == "s":
                cells.append(shared[int(value.text)])
            else:
                cells.append(value.text)
        while len(cells) < 3:
            cells.append("")
        rows.append(cells)
    return rows


def _clean_title(title: str) -> str:
    """Strip the Census trilateral-agreement marker.

    796 of 2,122 titles end in a bare ``T`` ("Food Services and Drinking
    PlacesT"). Requiring a preceding lowercase letter keeps genuine trailing
    capitals (acronyms) intact.
    """
    return re.sub(r"(?<=[a-z])T$", "", title.strip())


def load_naics_table(force: bool = False) -> dict[str, dict[str, str]]:
    """code -> {title, description}. Descriptions are always populated."""
    rows = _read_xlsx_rows(download_naics(force=force))
    table: dict[str, dict[str, str]] = {}
    for code, title, desc in rows[1:]:
        code = code.strip()
        if not re.fullmatch(r"\d+", code):
            continue
        desc = desc.strip()
        table[code] = {
            "title": _clean_title(title),
            "description": "" if desc.upper() == "NULL" else desc,
        }

    # 154 group codes carry the literal string "NULL" because their text lives
    # at the more detailed level (7225 is NULL; 72251 has the description).
    # Walk down to the first child that has one.
    for code, entry in table.items():
        if entry["description"]:
            continue
        children = sorted(
            child
            for child in table
            if len(child) == len(code) + 1
            and child.startswith(code)
            and table[child]["description"]
        )
        if children:
            entry["description"] = table[children[0]]["description"]
            entry["description_from"] = children[0]
    return table


def expand_ces_naics(raw: str) -> tuple[list[str], bool]:
    """Decode a CES ``naics_code`` value into concrete NAICS codes.

    Syntaxes observed across the 850 CES industries::

        "722"            -> ["722"]
        "part 238"       -> ["238"], partial=True
        "21221,3,9"      -> ["21221", "21223", "21229"]
        "332200;991,9"   -> ["332200", "332991", "332999"]
        "334512,4,6-9"   -> ["334512", "334514", "334516".."334519"]
        "-"              -> [] (aggregate such as Total nonfarm)

    Each fragment replaces the trailing digits of the *previous* code, not of
    the first one. Expanding relative to the base silently yields wrong codes:
    "332200;991,9" would give 332209 instead of 332999.
    """
    raw = (raw or "").strip()
    if not raw or raw == "-":
        return [], False

    partial = raw.startswith("part ")
    if partial:
        raw = raw[len("part ") :].strip()

    codes: list[str] = []
    prev: str | None = None
    for fragment in re.split(r"[,;]", raw):
        fragment = fragment.strip()
        if not fragment:
            continue
        if prev is None:
            codes.append(fragment)
            prev = fragment
            continue
        if "-" in fragment:  # inclusive range, e.g. "6-9" or "3-8"
            low, high = fragment.split("-", 1)
            stem = prev[: len(prev) - len(low)]
            for digit in range(int(low), int(high) + 1):
                codes.append(stem + str(digit).zfill(len(low)))
        else:
            codes.append(prev[: len(prev) - len(fragment)] + fragment)
        prev = codes[-1]
    return codes, partial


def resolve_code(code: str, table: dict[str, dict[str, str]]) -> tuple[str | None, str]:
    """Map an expanded code to a published NAICS entry.

    Returns ``(resolved_code, match)`` where match is ``exact`` or ``rolled_up``.
    CES pads codes to a uniform width (5250 for 525, 3160 for 316) and retains
    some codes discontinued in the 2022 revision (334518). Trimming trailing
    zeros and then single digits recovers the nearest published ancestor.
    """
    if code in table:
        return code, "exact"
    trimmed = code.rstrip("0")
    while len(trimmed) >= 2:
        if trimmed in table:
            return trimmed, "rolled_up"
        trimmed = trimmed[:-1]
    return None, "unmatched"


def describe(raw: str, table: dict[str, dict[str, str]]) -> dict | None:
    """Full NAICS annotation for one CES industry, or None for aggregates."""
    codes, partial = expand_ces_naics(raw)
    if not codes:
        return None

    matches = []
    for code in codes:
        resolved, match = resolve_code(code, table)
        if resolved is None:
            matches.append({"code": code, "title": None, "match": "unmatched"})
            continue
        matches.append(
            {
                "code": code,
                "resolved_code": resolved,
                "title": table[resolved]["title"],
                "match": match,
            }
        )

    primary = next((m for m in matches if m.get("resolved_code")), None)
    return {
        "raw": raw,
        "partial": partial,
        "codes": matches,
        "description": table[primary["resolved_code"]]["description"] if primary else "",
    }
