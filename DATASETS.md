# Datasets

## Current Employment Statistics, national, seasonally adjusted (BLS)

**What it is.** Monthly employment on nonfarm payrolls, in thousands, by
industry. One value per series per month. The explorer uses 842 seasonally
adjusted "all employees" series (series IDs `CES<8-digit industry code>01`).

**Where it comes from.** BLS Public Data API v2
(`https://api.bls.gov/publicAPI/v2/timeseries/data/`), registered key, 50
series per request. A refresh after a release pulls 2019 to the current year,
about 17 requests. Industry metadata (display level, sort order, parent, NAICS
code) comes from the BLS flat file `ce.industry`, because the API has no
metadata endpoint. Code: `src/nfp_treemap/fetch.py`,
`src/nfp_treemap/industries.py`.

**Version and vintage.** Monthly, first Friday at 8:30 am ET. The API serves
only the current vintage. A refresh upserts on (industry, month), so revised
values overwrite earlier ones and the local cache holds only the newest
vintage. Earlier vintages come from the BLS revision triangles
(`cesvinall.zip`, 113 series, releases from May 2003 to January 2026) via
`src/nfp_treemap/vintage.py` into `data/ces_vintages.parquet`.

**Coverage.** United States, nonfarm payroll jobs. A few aggregates go back to
1939; most industry detail starts in 1990. The figures are survey estimates,
not counts. The survey covers about 119,000 businesses and government agencies
(about 629,000 worksites), and the annual benchmark ties levels to
unemployment-insurance tax records (QCEW). In the first release of a month,
BLS publishes the headline aggregates and the larger industries but not most
detailed industries. Those follow a month later. On November 6, 2026, 175 of
842 series had October 2026 values. At display level 5, 53 of 240 industries
did.

**Changes over time.** Industry codes follow NAICS 2022. BLS reconstructs
history when it reclassifies, so a series is consistent within the current
vintage. The explorer's display levels come from `ce.industry`. Some series are
composites that overlap their siblings. The build drops them from sums and the
treemap marks them (`composite` in `data/industries.json`).

**Suppressed, censored or masked values.** None are suppressed in the national
SA series. Detailed series that BLS doesn't publish seasonally adjusted aren't
in the explorer.

**Missing data.** A missing value means not published. It never means zero.
Detailed industries for the newest month are missing until the next release
fills them in.

**Revisions.** Each month is estimated three times: the first release, then
revised in each of the next two releases. Every February, the annual benchmark
also revises about the last two years of levels (and the seasonal factors
further back). Today's release revised August 2026 from +133,000 to +186,000
and September 2026 from +29,000 to +60,000 (total nonfarm, monthly change).

**Units and rounding.** Thousands of jobs, published to one decimal (the
nearest hundred jobs). Monthly changes are differences of two levels, so each
carries rounding of up to plus or minus 100 jobs.

**Known quirks.**
- Each series is seasonally adjusted on its own, so children don't add up
  exactly to their parent in the SA data. The test
  `test_dropping_composites_stops_the_double_count` allows 1,000 jobs. On
  November 6, 2026, Motor vehicles and parts was off by 1,300 for September
  2026 and the test fails.
- Restaurants and other eating places can move far more than its parent, food
  services. The gap is in the seasonal adjustment; unadjusted, the parts add
  up exactly.
- The pandemic span, March 2020 to June 2022, is left out of the anomaly
  history (see below).

**Uncertainty.** BLS gives a 90% confidence interval of about plus or minus
122,000 for the monthly change in total nonfarm employment. Detailed
industries have wider relative error.

**License and attribution.** Public domain (U.S. government work). Credit
"U.S. Bureau of Labor Statistics, Current Employment Statistics."

### Method: the explorer's anomaly score (used in posts and social copy)

For an industry's change over horizon h (1 month in the social copy):

- **Sample:** the same industry's changes over the same horizon for the prior
  max(240, 10h) months, plus the current one. A change is dropped if either of
  its endpoints falls between March 2020 and June 2022. At least 24 samples and
  6 non-overlapping windows are required.
- **Robust z** = 0.6745 x (change minus the sample median) / the median
  absolute deviation. "Typical month" means the median. "Usual swing" means the
  median absolute deviation divided by 0.6745.
- **Rarity p:** the share of samples at least as far from the median as the
  current change.
- **Tiers:** unusual means p of 0.10 or less and absolute z of 2 or more.
  Anomaly means p of 0.01 or less and absolute z of 3 or more. "Unusual
  increases" counts unusual-tier items with z above 0.
- Source of truth: `anomaly()` in `src/nfp_treemap/static/treemap.js`, with
  constants in `src/nfp_treemap/config.py`.

**Counting unusual increases across months (social copy, November 6, 2026).**
Score every month from January 2013 to October 2026 for the 175 series that
have October 2026 values, leaving out months whose change touches the
pandemic span. Count unusual-tier increases per month and compare October
with the median of the earlier months.

**Breadth.** The share of industries at a display level, composites left out,
whose one-month change is above zero.
