"""Populate the local observation cache from the BLS API.

    python -m nfp_treemap.fetch --backfill   # full history, ~54 requests
    python -m nfp_treemap.fetch --refresh    # current window, ~17 requests
"""
from __future__ import annotations

import argparse
import datetime as _dt
import json
import sys

import pandas as pd

from . import industries as industries_mod
from .bls_api import BLSError, Client, QuotaExceeded
from .config import (
    META_JSON,
    OBSERVATIONS_PARQUET,
    api_key,
    series_id,
    year_windows,
)

COLUMNS = ["industry_code", "date", "employees"]


def _series_ids() -> list[str]:
    rows = industries_mod.load()
    return [series_id(r["code"]) for r in rows]


def _to_frame(observations) -> pd.DataFrame:
    records = [
        (o.industry_code, _dt.date(o.year, o.month, 1), o.value) for o in observations
    ]
    frame = pd.DataFrame.from_records(records, columns=COLUMNS)
    if not frame.empty:
        frame["date"] = pd.to_datetime(frame["date"])
        frame["employees"] = frame["employees"].astype("float32")
    return frame


def _merge(new: pd.DataFrame) -> pd.DataFrame:
    """Upsert on (industry_code, date) so revisions overwrite prior values."""
    if OBSERVATIONS_PARQUET.exists():
        existing = pd.read_parquet(OBSERVATIONS_PARQUET)
        combined = pd.concat([existing, new], ignore_index=True)
    else:
        combined = new
    combined = combined.drop_duplicates(
        subset=["industry_code", "date"], keep="last"
    ).sort_values(["industry_code", "date"], ignore_index=True)
    return combined


def run(mode: str) -> int:
    if not api_key():
        print(
            "No BLS_API_KEY found. Copy .env.example to .env and add your key.\n"
            "Without one the API allows only 25 series and 25 requests/day, which\n"
            "cannot cover 842 series in a single day.",
            file=sys.stderr,
        )
        return 2

    ids = _series_ids()
    windows = year_windows()
    if mode == "refresh":
        windows = windows[-1:]

    client = Client()
    print(
        f"{len(ids)} series x {len(windows)} window(s), "
        f"batch size {client.batch_size}"
    )

    all_new = []
    try:
        for start, end in windows:
            observations = list(client.fetch_window(ids, start, end))
            print(
                f"  {start}-{end}: {len(observations):>7,} observations "
                f"({client.requests_used} requests used)"
            )
            all_new.append(_to_frame(observations))
    except QuotaExceeded as exc:
        print(f"\nBLS daily quota hit: {exc}", file=sys.stderr)
        if not all_new:
            return 3
        print("Writing the partial results already fetched.", file=sys.stderr)
    except BLSError as exc:
        print(f"\nBLS request failed: {exc}", file=sys.stderr)
        return 3

    new = pd.concat([f for f in all_new if not f.empty], ignore_index=True)
    combined = _merge(new)

    OBSERVATIONS_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(OBSERVATIONS_PARQUET, index=False, compression="zstd")

    latest = combined["date"].max()
    META_JSON.write_text(
        json.dumps(
            {
                "last_fetch": _dt.datetime.now().isoformat(timespec="seconds"),
                "mode": mode,
                "latest_period": latest.strftime("%Y-%m"),
                "series_with_data": int(combined["industry_code"].nunique()),
                "observations": int(len(combined)),
                "requests_used": client.requests_used,
            },
            indent=1,
        )
    )
    print(
        f"\n{len(combined):,} observations across "
        f"{combined['industry_code'].nunique()} series, latest "
        f"{latest.strftime('%Y-%m')}"
    )
    print(f"wrote {OBSERVATIONS_PARQUET}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--backfill", action="store_true", help="full history")
    group.add_argument("--refresh", action="store_true", help="current window only")
    args = parser.parse_args()
    return run("backfill" if args.backfill else "refresh")


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
