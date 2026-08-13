"""Payload encoding and API request planning."""
from __future__ import annotations

import pytest

from nfp_treemap import transform
from nfp_treemap.config import MAX_YEARS_PER_REQUEST, OBSERVATIONS_PARQUET, year_windows


def test_year_windows_cover_history_without_exceeding_the_api_limit():
    windows = year_windows(2026)
    assert windows[0][0] == 1939
    assert windows[-1][1] == 2026
    for start, end in windows:
        assert end - start + 1 <= MAX_YEARS_PER_REQUEST
    # contiguous, no gaps or overlaps
    for (_, end), (start, _) in zip(windows, windows[1:]):
        assert start == end + 1


def test_month_index_round_trips():
    for label in ("1939-01", "1990-01", "2020-03", "2026-07"):
        year, month = int(label[:4]), int(label[5:])
        assert transform.index_to_label(transform.month_index(year, month)) == label


@pytest.mark.skipif(
    not OBSERVATIONS_PARQUET.exists(), reason="run nfp_treemap.fetch --backfill first"
)
class TestPayload:
    @staticmethod
    @pytest.fixture(scope="class")
    def payload():
        return transform.build_payload()

    def test_shape(self, payload):
        assert payload["meta"]["series"] == len(payload["industries"]) == 842
        assert payload["periodLabels"][0] == "1939-01"
        assert len(payload["periodLabels"]) == (
            payload["periodEnd"] - payload["periodStart"] + 1
        )

    def test_delta_encoding_round_trips(self, payload):
        """Values ship as cumulative deltas at 10x; decoding must be exact."""
        import pandas as pd

        frame = pd.read_parquet(OBSERVATIONS_PARQUET)
        for code in ("00000000", "70722000", "20238100"):
            item = next(i for i in payload["industries"] if i["c"] == code)
            running = 0
            decoded = []
            for delta in item["d"]:
                running += delta
                decoded.append(running / 10)
            expected = (
                frame[frame["industry_code"] == code]
                .sort_values("date")["employees"]
                .round(1)
                .tolist()
            )
            assert decoded == pytest.approx(expected, abs=0.05)

    def test_default_base_avoids_the_detail_publication_lag(self, payload):
        """The newest month only carries the aggregates, so it is a bad default."""
        default_idx = payload["periodLabels"].index(payload["defaultBase"])
        default_idx += payload["periodStart"]
        covered = sum(
            1
            for i in payload["industries"]
            if i["s"] <= default_idx < i["s"] + len(i["d"])
        )
        assert covered >= 0.95 * len(payload["industries"])
        assert payload["defaultBase"] != payload["periodLabels"][-1]

    def test_every_industry_carries_hierarchy_and_naics_fields(self, payload):
        for item in payload["industries"]:
            assert item["ss"] and item["ssn"]
            assert item["l"] >= 0
            if item["c"] != "00000000":
                assert item["p"]
