"""Shared paths, constants and small helpers."""
from __future__ import annotations

import datetime as _dt
import os
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "data"
DIST_DIR = ROOT / "dist"
CACHE_DIR = DATA_DIR / "raw"

INDUSTRIES_JSON = DATA_DIR / "industries.json"
OBSERVATIONS_PARQUET = DATA_DIR / "ces_observations.parquet"
META_JSON = DATA_DIR / "meta.json"

# --- Source URLs -----------------------------------------------------------
# ce.industry is the ONLY flat file we touch. The BLS API has no metadata
# endpoint (catalog=true is disabled), so display_level / sort_sequence /
# naics_code are unavailable any other way. Every observation comes from the API.
CE_INDUSTRY_URL = "https://download.bls.gov/pub/time.series/ce/ce.industry"
NAICS_DESCRIPTIONS_URL = (
    "https://www.census.gov/naics/2022NAICS/2022_NAICS_Descriptions.xlsx"
)
BLS_API_URL = "https://api.bls.gov/publicAPI/v2/timeseries/data/"

# download.bls.gov 403s anything without a browser-like prefix (a bare
# "NFP_Treemap/1.0" or "python-requests/2.32" is rejected), but BLS guidance
# asks callers to identify themselves with a contact address. Do both.
CONTACT_EMAIL = os.environ.get("NFP_TREEMAP_CONTACT", "eric@asaltollc.com")
USER_AGENT = f"Mozilla/5.0 NFP_Treemap/1.0 ({CONTACT_EMAIL})"

# --- CES series construction ----------------------------------------------
SERIES_PREFIX = "CES"  # CES = seasonally adjusted, CEU = not seasonally adjusted
DATA_TYPE_ALL_EMPLOYEES = "01"

# API limits with a registration key.
MAX_SERIES_PER_REQUEST = 50
MAX_YEARS_PER_REQUEST = 20
DAILY_REQUEST_LIMIT = 500

CES_HISTORY_START = 1939  # supersectors reach back this far; most detail starts 1990

# --- Hosted page metadata --------------------------------------------------
# The build is served from GitHub Pages and embedded in articles on more than
# one site. Both levers below default to EMPTY deliberately.
#
# Do not set ROBOTS to noindex. The only controlled test of how Googlebot
# treats iframes (Grimm, 2022) found that a parent page can rank for content
# that exists only in the framed URL, and that a noindex on the framed URL
# removes that ability. Noindexing this file would strip the tool's content
# from every article that embeds it.
#
# Do not set CANONICAL_URL to an embedding article either. A 164-word tool and
# a 3,800-word article are not equivalent pages, and Google ignores canonicals
# between URLs that are not equivalent. The levers exist for a future
# consolidation, not for this one.
META_DESCRIPTION = (
    "Free interactive treemap of US nonfarm payroll employment by industry. "
    "Every industry the BLS Current Employment Statistics survey publishes, "
    "from total nonfarm down to six-digit NAICS detail, with any base month "
    "and horizons from one month to twenty years."
)
# The article this tool belongs to. Rendered as a credit line in the footnotes,
# which the embedded layout hides - so the link appears on the standalone hosted
# page (where it is a real cross-domain link from a page we control) and not
# inside the iframe on the article itself, where it would only link to itself.
SOURCE_URL = os.environ.get(
    "NFP_TREEMAP_SOURCE_URL",
    "https://www.data4thepeople.com/p/nonfarm-payrolls-by-industry",
).strip()
SOURCE_TITLE = os.environ.get(
    "NFP_TREEMAP_SOURCE_TITLE", "Nonfarm Payrolls by Industry"
).strip()
SOURCE_PUBLISHER = os.environ.get(
    "NFP_TREEMAP_SOURCE_PUBLISHER", "Data 4 The People"
).strip()

CANONICAL_URL = os.environ.get("NFP_TREEMAP_CANONICAL", "").strip()
ROBOTS = os.environ.get("NFP_TREEMAP_ROBOTS", "").strip()

# Where a brand logo is picked up from, if present. Embedded as a data URI at
# build time, since the published page may not fetch external assets.
LOGO_DIR = ROOT / "logo"
LOGO_SUFFIXES = (".svg", ".png", ".jpg", ".jpeg", ".webp")

# Comparison horizons offered in the UI, in months.
HORIZONS = {
    "1mo": 1,
    "1yr": 12,
    "2yr": 24,
    "3yr": 36,
    "5yr": 60,
    "10yr": 120,
    "20yr": 240,
}

# --- Anomaly scoring -------------------------------------------------------
# The sample is the same industry's own history of same-length changes.
#
# The lookback has to scale with the horizon. A fixed 120 months holds 120
# independent 1-month changes but only ~3 independent 3-year windows, and with
# overlapping windows the score is then driven by whichever single episode they
# all share. For Total nonfarm at a 3-year horizon that produced a confident
# nonsense: every sample was measured off the 2020 trough, so all 79 were large
# gains (+3.0M to +14.7M) and an ordinary +2.8M scored z = -3.5, "extreme".
# 20 years, so the reference distribution spans at least one full business
# cycle. A 10-year floor looks reasonable but, once the pandemic window is
# excluded, contains no downturn at all: every 12-month change in it is an
# expansion-year change, so an ordinary slowdown (+403k for Total nonfarm)
# scored z = -4.05, "extreme". Widening it puts 2008-09 back in scope.
ANOMALY_LOOKBACK_MONTHS = 240  # floor, for short horizons
ANOMALY_LOOKBACK_PER_HORIZON = 10  # months of lookback per month of horizon
ANOMALY_MIN_SAMPLES = 24
# Overlapping windows are not independent; require enough non-overlapping ones
# that the score means something, and say "insufficient history" otherwise.
ANOMALY_MIN_INDEPENDENT = 6

# Flagging an anomaly on the tile itself, rather than only in the tooltip, is a
# stronger claim than scoring one, so it takes two tests that must both pass.
#
# ANOMALY_FLAG_P is rank-based: the share of this industry's own history lying
# at least as far from its median as the current change. Distribution free,
# which matters because monthly payroll changes are heavy-tailed - measured
# over 2013-2026, |z| >= 3 fires roughly ten times more often than a normal
# distribution predicts, so a normal-theory p-value would badly overstate how
# surprising a move is. The floor is 1/n, so the test never claims more
# resolution than the sample holds.
#
# ANOMALY_FLAG_Z is the scale guard. An industry with a nearly flat history
# sets a record whenever it twitches, and the rarest 1% of a flat series is
# still a trivial move. Rarity alone would flag those; magnitude alone would
# flag ordinary months in heavy-tailed industries.
#
# Calibrated against every month from 2013 to 2026 so the marker stays rare
# enough to mean something: about 1 flagged industry per view at level 4 and
# 2 to 3 at level 5, never a wall of dots.
ANOMALY_FLAG_P = 0.01
ANOMALY_FLAG_Z = 3.0

# Payroll levels were distorted from the collapse until they regained their
# February 2020 peak in June 2022. A change window with EITHER endpoint inside
# that span is not a draw from the same process. Excluding only the acute
# months (Mar-Aug 2020) was not enough: a 3-year window starting September 2020
# still measures from deep in the hole.
DISTORTED_START = "2020-03"
DISTORTED_END = "2022-06"

# Supersector code -> the code its detail rolls up to for group labelling.
SUPERSECTOR_ALIASES = {"31": "30", "32": "30", "41": "40", "42": "40", "43": "40"}

# The CES aggregate structure above the supersectors is a lattice, not a tree:
# Total nonfarm = Total private + Government, and also = Goods-producing +
# Service-providing, and Private service-providing is a subset of both Total
# private and Service-providing. Nothing in the industry codes encodes these
# relationships, so the tree used for drill-down is stated explicitly. The
# level-1 rows are CES's own overlapping aggregates and all hang off the root;
# below that the tree partitions cleanly.
AGGREGATE_PARENTS = {
    "05000000": "00000000",  # Total private
    "06000000": "00000000",  # Goods-producing
    "07000000": "00000000",  # Service-providing
    "08000000": "00000000",  # Private service-providing
    "10000000": "06000000",  # Mining and logging
    "20000000": "06000000",  # Construction
    "30000000": "06000000",  # Manufacturing
    "31000000": "30000000",  # Durable goods
    "32000000": "30000000",  # Nondurable goods
    "40000000": "08000000",  # Trade, transportation, and utilities
    "42000000": "40000000",  # Retail trade
    "43000000": "40000000",  # Transportation and warehousing
    "50000000": "08000000",  # Information
    "55000000": "08000000",  # Financial activities
    "60000000": "08000000",  # Professional and business services
    "65000000": "08000000",  # Private education and health services
    "70000000": "08000000",  # Leisure and hospitality
    "80000000": "08000000",  # Other services
    "90000000": "07000000",  # Government (service-providing, but not private)
}


def api_key() -> str | None:
    """BLS registration key from the environment or a local .env file."""
    load_dotenv(ROOT / ".env")
    key = os.environ.get("BLS_API_KEY", "").strip()
    return key or None


def year_windows(end_year: int | None = None) -> list[tuple[int, int]]:
    """Chunk CES history into <=20-year request windows."""
    end_year = end_year or _dt.date.today().year
    windows: list[tuple[int, int]] = []
    start = CES_HISTORY_START
    while start <= end_year:
        stop = min(start + MAX_YEARS_PER_REQUEST - 1, end_year)
        windows.append((start, stop))
        start = stop + 1
    return windows


def series_id(industry_code: str, seasonal: str = "S") -> str:
    prefix = SERIES_PREFIX if seasonal == "S" else "CEU"
    return f"{prefix}{industry_code}{DATA_TYPE_ALL_EMPLOYEES}"


def industry_code_from_series(sid: str) -> str:
    """CES0000000001 -> 00000000"""
    return sid[3:-2]
