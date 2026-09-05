"""Assemble the compact payload the browser needs.

Only raw monthly *levels* are shipped. Changes, percentages and anomaly scores
are derived in JS, because precomputing every
(base period x horizon x display level) combination would be far larger than
the levels themselves and would still not cover click-to-drill.
"""
from __future__ import annotations

import json

import pandas as pd

from . import industries as industries_mod
from .config import (
    ANOMALY_LOOKBACK_MONTHS,
    ANOMALY_LOOKBACK_PER_HORIZON,
    ANOMALY_FLAG_P,
    ANOMALY_FLAG_Z,
    ANOMALY_WATCH_P,
    ANOMALY_WATCH_Z,
    ANOMALY_MIN_INDEPENDENT,
    ANOMALY_MIN_SAMPLES,
    DISTORTED_END,
    DISTORTED_START,
    HORIZONS,
    META_JSON,
    OBSERVATIONS_PARQUET,
)

BASE_YEAR, BASE_MONTH = 1939, 1


def month_index(year: int, month: int) -> int:
    return (year - BASE_YEAR) * 12 + (month - BASE_MONTH)


def index_to_label(idx: int) -> str:
    year = BASE_YEAR + (idx + BASE_MONTH - 1) // 12
    month = (idx + BASE_MONTH - 1) % 12 + 1
    return f"{year:04d}-{month:02d}"


def build_payload() -> dict:
    frame = pd.read_parquet(OBSERVATIONS_PARQUET)
    frame["idx"] = (frame["date"].dt.year - BASE_YEAR) * 12 + (
        frame["date"].dt.month - BASE_MONTH
    )
    frame = frame.sort_values(["industry_code", "idx"])

    # CES publishes employment in thousands to one decimal. Storing value*10 as
    # an integer and then delta-encoding shrinks the JSON by roughly half:
    # month-over-month moves are small, so most entries become 1-3 characters.
    series: dict[str, dict] = {}
    for code, group in frame.groupby("industry_code", sort=False):
        values = (group["employees"].to_numpy() * 10).round().astype("int64")
        deltas = [int(values[0])]
        deltas.extend(int(b - a) for a, b in zip(values[:-1], values[1:]))
        series[code] = {"s": int(group["idx"].iloc[0]), "d": deltas}

    rows = industries_mod.load()
    industries = []
    for row in rows:
        payload_series = series.get(row["code"])
        if payload_series is None:
            continue  # no seasonally adjusted all-employees series published
        entry = {
            "c": row["code"],
            "n": row["name"],
            "l": row["level"],
            "p": row["parent_code"],
            "ss": row["supersector_code"],
            "ssn": row["supersector_name"],
            "naics": row["naics"],
            "s": payload_series["s"],
            "d": payload_series["d"],
        }
        # Roll-ups that duplicate their own same-level siblings; hidden by
        # default so the tiles at a level sum to their parent.
        if row.get("composite"):
            entry["dup"] = 1
        industries.append(entry)

    first = min(i["s"] for i in industries)
    last = max(i["s"] + len(i["d"]) - 1 for i in industries)
    meta = json.loads(META_JSON.read_text()) if META_JSON.exists() else {}

    # CES publishes detailed industries a month behind the headline aggregates,
    # so the newest month carries only the aggregates. Default to it anyway:
    # the headline number is the reason anyone opens the page on release day,
    # and the page flags how many industries are still awaiting publication
    # (updateLagNote in treemap.js) rather than silently showing stale data.
    default_base = last

    return {
        "meta": {
            "latest_period": meta.get("latest_period"),
            "last_fetch": meta.get("last_fetch"),
            "observations": meta.get("observations"),
            "series": len(industries),
        },
        "periodStart": first,
        "periodEnd": last,
        "defaultBase": index_to_label(default_base),
        "periodLabels": [index_to_label(i) for i in range(first, last + 1)],
        "horizons": HORIZONS,
        "anomaly": {
            "lookbackFloor": ANOMALY_LOOKBACK_MONTHS,
            "lookbackPerHorizon": ANOMALY_LOOKBACK_PER_HORIZON,
            "minSamples": ANOMALY_MIN_SAMPLES,
            "minIndependent": ANOMALY_MIN_INDEPENDENT,
            "flagP": ANOMALY_FLAG_P,
            "flagZ": ANOMALY_FLAG_Z,
            "watchP": ANOMALY_WATCH_P,
            "watchZ": ANOMALY_WATCH_Z,
            "distortedStart": month_index(
                int(DISTORTED_START[:4]), int(DISTORTED_START[5:])
            ),
            "distortedEnd": month_index(
                int(DISTORTED_END[:4]), int(DISTORTED_END[5:])
            ),
        },
        "industries": industries,
    }


if __name__ == "__main__":  # pragma: no cover
    payload = build_payload()
    blob = json.dumps(payload, separators=(",", ":"))
    print(f"industries : {len(payload['industries'])}")
    print(f"periods    : {len(payload['periodLabels'])} "
          f"({payload['periodLabels'][0]} .. {payload['periodLabels'][-1]})")
    print(f"payload    : {len(blob) / 1e6:.2f} MB")
