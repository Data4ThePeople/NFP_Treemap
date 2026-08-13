"""Batched client for the BLS public API v2."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Iterable, Iterator

import requests

from .config import (
    BLS_API_URL,
    DAILY_REQUEST_LIMIT,
    MAX_SERIES_PER_REQUEST,
    USER_AGENT,
    api_key,
)


class BLSError(RuntimeError):
    pass


class QuotaExceeded(BLSError):
    pass


@dataclass
class Observation:
    industry_code: str
    year: int
    month: int
    value: float


@dataclass
class Client:
    key: str | None = field(default_factory=api_key)
    max_retries: int = 4
    requests_used: int = 0

    def __post_init__(self) -> None:
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": USER_AGENT, "Content-Type": "application/json"}
        )
        # Without a key the API silently applies much tighter limits.
        self.batch_size = MAX_SERIES_PER_REQUEST if self.key else 25

    def _post(self, payload: dict) -> dict:
        delay = 2.0
        last_error: str = ""
        for attempt in range(self.max_retries):
            try:
                resp = self.session.post(BLS_API_URL, json=payload, timeout=180)
                self.requests_used += 1
                if resp.status_code == 200:
                    body = resp.json()
                    status = body.get("status")
                    if status == "REQUEST_SUCCEEDED":
                        return body
                    messages = " | ".join(body.get("message", []))
                    # Quota problems are terminal; retrying only burns the budget.
                    if "threshold" in messages.lower() or "daily" in messages.lower():
                        raise QuotaExceeded(messages)
                    last_error = f"{status}: {messages}"
                else:
                    last_error = f"HTTP {resp.status_code}"
            except QuotaExceeded:
                raise
            except requests.RequestException as exc:
                last_error = str(exc)
            if attempt < self.max_retries - 1:
                time.sleep(delay)
                delay *= 2
        raise BLSError(f"BLS request failed after {self.max_retries} attempts: {last_error}")

    def fetch_window(
        self, series_ids: list[str], start_year: int, end_year: int
    ) -> Iterator[Observation]:
        """Yield monthly observations for one year window, batching series."""
        for i in range(0, len(series_ids), self.batch_size):
            batch = series_ids[i : i + self.batch_size]
            if self.requests_used >= DAILY_REQUEST_LIMIT:
                raise QuotaExceeded(
                    f"local guard: {self.requests_used} requests already issued "
                    f"(daily limit {DAILY_REQUEST_LIMIT})"
                )
            payload = {
                "seriesid": batch,
                "startyear": str(start_year),
                "endyear": str(end_year),
                "annualaverage": False,
            }
            if self.key:
                payload["registrationkey"] = self.key
            body = self._post(payload)
            yield from _parse(body)


def _parse(body: dict) -> Iterator[Observation]:
    for series in body.get("Results", {}).get("series", []):
        sid = series.get("seriesID", "").strip()
        if len(sid) < 13:
            continue
        industry_code = sid[3:-2]
        for point in series.get("data", []):
            period = point.get("period", "")
            # M13 is the annual average; annualaverage=False should exclude it
            # but the API is not consistent about that.
            if not period.startswith("M") or period == "M13":
                continue
            raw = point.get("value", "").strip().replace(",", "")
            if not raw or raw == "-":
                continue
            try:
                value = float(raw)
            except ValueError:
                continue
            yield Observation(
                industry_code=industry_code,
                year=int(point["year"]),
                month=int(period[1:]),
                value=value,
            )


def chunked(items: Iterable[str], size: int) -> Iterator[list[str]]:
    bucket: list[str] = []
    for item in items:
        bucket.append(item)
        if len(bucket) == size:
            yield bucket
            bucket = []
    if bucket:
        yield bucket
