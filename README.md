# Bancreek U.S. Employment Data Treemap

A self-contained HTML treemap of BLS Current Employment Statistics: one tile per
industry, **area = absolute change in employees**, **colour = signed change**,
grouped by supersector, with click-to-drill, an anomaly score, and official NAICS
definitions in the tooltip.

Rebuilds the Tableau Public version from the **BLS API** rather than the flat
text files, and outputs a single file you can host anywhere.

```
python -m nfp_treemap.fetch --backfill   # full history, 85 API requests
python -m nfp_treemap.build              # -> dist/index.html  (1.8 MB, no server)
```

## Setup

```bash
python3.12 -m venv .venv
.venv/bin/pip install -r requirements.txt
cp .env.example .env        # add your BLS registration key
```

Get a free key at <https://data.bls.gov/registrationEngine/>. It lifts the API to
50 series and 20 years per request and 500 requests/day; without one you are
capped at 25 series and 25 requests/day, which cannot cover 842 series in a day.

## Refreshing after a jobs report

```bash
python -m nfp_treemap.fetch --refresh    # 17 requests, current window only
python -m nfp_treemap.build
```

`--refresh` upserts on `(industry_code, date)`, so **revisions to prior months
overwrite the cached values**. This matters: CES revises the two preceding months
every release and up to five years of seasonally adjusted data at each annual
benchmark. The June 2026 figure for Food Services read −32.9k when the Tableau
version was captured and −12.1k afterwards — same series, different vintage.

## How it works

| Stage | Module | Output |
|---|---|---|
| Industry hierarchy + NAICS text | `industries.py`, `naics.py` | `data/industries.json` |
| Observations from the API | `bls_api.py`, `fetch.py` | `data/ces_observations.parquet` |
| Browser payload | `transform.py` | in-memory |
| Page render | `build.py` | `dist/index.html` |

The browser receives **raw monthly levels only** — changes, percentages and
anomaly scores are computed in JS on demand. Precomputing every
(base period × horizon × display level) combination would dwarf the levels
themselves and still would not cover click-to-drill. Values ship delta-encoded at
10×, which halves the payload to 1.8 MB for 400,673 observations.

### Where the data comes from

Every observation comes from the BLS API. Two metadata files are fetched once and
cached, because the API cannot supply them:

- **`ce.industry`** — the API has no metadata endpoint (`catalog=true` is
  disabled), so `display_level`, `sort_sequence` and `naics_code` exist nowhere
  else.
- **Census `2022_NAICS_Descriptions.xlsx`** — official industry definitions.
  Parsed with the standard library; an `.xlsx` is a zip of XML, so `openpyxl` is
  not a dependency.

`download.bls.gov` rejects any User-Agent without a browser-like prefix, so
requests identify as `Mozilla/5.0 NFP_Treemap/1.0 (<contact>)`. Override the
contact with `NFP_TREEMAP_CONTACT`.

## Three things that are easy to get wrong

**The industry tree is not the sort order.** The obvious rule — "parent is the
nearest preceding row with a smaller `display_level`" — reports zero orphans and
is quietly wrong. CES interleaves its residential/nonresidential part-splits at
the *same* level as the total they split, so all 52 specialty-trade-contractor
rows attach to *Nonresidential specialty trade contractors* instead of to
*Specialty trade contractors*. Parents are derived from the industry code
instead (`20238110` → `20238100` → `20238000`), with an explicit map for the
top-level aggregates, whose relationships the codes do not encode.

**The `naics_code` field has five undocumented syntaxes.** Plain (`722`),
comma shorthand (`21221,3,9` → 21221, 21223, 21229), semicolons
(`332200;991,9`), ranges (`334512,4,6-9`) and `part N`. Each fragment replaces
the trailing digits of the **previous** code, not the first — expanding relative
to the base turns `332200;991,9` into `332209` instead of `332999`. All 813
non-aggregate industries resolve; see `tests/test_naics.py`.

**Some CES roll-ups sit at the same display level as their own components.** At
level 4, "Health care" (NAICS 621,2,3) is exactly Ambulatory + Hospitals +
Nursing, so a flat level-4 view counted it twice: the children of Health care
and social assistance summed to **61.3k against a true 41.0k**. Three rows do
this — Health care, Specialty trade contractors, Motor vehicles and parts — and
they are detected structurally (a row whose NAICS set is the union of its
same-level siblings) rather than hard-coded, then hidden by default. Append
`&dupes=1` to show them.

**Anomaly scoring needs a lookback that scales with the horizon.** A fixed
120-month window holds 120 independent 1-month changes but only ~3 independent
3-year windows, so the score gets driven by whatever single episode they all
share. Total nonfarm's 3-year change scored **z = −3.66, "extreme", 0th
percentile — on a gain of +2.81M**, because all 79 samples were measured off the
2020 trough and were therefore large gains (+3.0M to +14.7M). Three fixes:

- Lookback is `max(240, 10 × horizon)` months, and a minimum of 6 *independent*
  (non-overlapping) windows is required — otherwise it reports insufficient
  history rather than a confident wrong number. The 20-year floor matters
  independently: a 10-year window minus the pandemic contains **no downturn at
  all**, so every sample is an expansion-year change and an ordinary +403k year
  for Total nonfarm scored z = −4.05, "extreme". At 20 years the sample reaches
  back through 2008–09 and the same year reads z = −2.31, "unusual".
- The tooltip reports the span **actually covered**, not the lookback
  requested: a 10-year horizon asks for 100 years and no series has that
  (Total nonfarm starts 1939, most industries 1990).
- The excluded span is **Mar 2020 – Jun 2022** (collapse until payrolls regained
  their Feb 2020 peak), and a window is dropped if *either* endpoint falls
  inside it. Excluding only the acute months left long windows starting from
  deep in the hole. A window that itself straddles the disruption is not scored
  at all.
- The score is a robust z (median and MAD, scaled by 0.6745). Mean/SD had Food
  Services at a "typical" −0.81 while sitting at the 5th percentile.

The same episode also produced a wording bug: rank direction is not the sign of
the change, and a +2.81M gain was described as a "larger drop than 100% of"
comparable windows. The tooltip now states the value and where it ranks, and
never calls a gain a drop.

## Embedding (iframe / Prismic)

The page detects that it is framed and switches to a compact layout: the
masthead and footnotes are dropped, the controls get denser, and the treemap is
sized to whatever height is left so a fixed-height iframe does not scroll.

```html
<iframe src="…/index.html" width="100%" height="620" style="border:0"
        title="Bancreek U.S. Employment Data Treemap"></iframe>
```

### Prismic (Data 4 The People)

Verified against the live constraints: **879px content column, 830px container
breakpoint, fixed height via oEmbed** (no parent-side JS, no auto-resize).
879 × 640, 1200 and 1300 all fit without scrolling, and the chart *fills* the
height it is given rather than leaving dead space. Covered by
`tests/test_responsive.py`.

**The layout keys off the container, not the viewport** — inside the oEmbed the
viewport does not describe the space the page actually gets, so viewport media
queries misfire. `body` carries `container: page / inline-size` and every
responsive rule is an `@container page (…)` query; a test asserts no layout
`@media` query survives. The container is on `body` rather than `.wrap` because
an element cannot query itself, and `.wrap`'s own padding has to respond too —
`.wrap` still declares `container-type` as well. JS measures the element
(`.wrap` width, a `ResizeObserver`) instead of `window.innerWidth` for the same
reason.

**Minimum frame heights** (measured). Narrower frames need *more* height,
because the controls wrap onto more rows:

| Frame width | Minimum height |
|---|---|
| ≥ 900px | 500px |
| 830–900px (incl. Prismic's 879) | 560px |
| 600–830px | 560px |
| < 600px | page scrolls — expected on a phone |

Below the minimum the treemap holds a 140px readability floor and the frame
scrolls rather than squashing the chart into a stripe.

Override the auto-detection with `#embed=0` (force the full layout inside a
frame) or `#embed=1` (force the compact layout standalone). All the other
deep-link parameters compose with it:
`…/index.html#embed=1&lvl=2&h=1yr&base=2026-06`.

**Theme.** Light and dark are both selected palettes, validated separately
against their own surface — the dark arms are re-stepped, not flipped. By
default the page follows the viewer's OS setting, which is right standalone and
wrong in an embed: a dark-mode visitor would get a dark chart inside a light
article. Pin it with `#theme=light` or `#theme=dark`.

**Auto-height.** An iframe cannot resize itself, so the page posts its content
height to the parent after every render. A host that wants an auto-sizing embed
can listen:

```js
addEventListener('message', (e) => {
  if (e.data?.type === 'nfp-treemap:height') iframe.height = e.data.height;
});
```

Hosts that set a fixed height can ignore the message — the compact layout
already fits.

## Branding

Drop an image in `logo/` and rebuild — the first `.svg/.png/.jpg/.webp` found
is inlined as a data URI (the published page cannot fetch external assets).
It renders in the masthead standalone and moves to the footer when embedded,
where the masthead is hidden but the branding should still travel. It is a
single element relocated by JS, not two copies: duplicating it would inline the
whole data URI twice and add ~140KB for nothing. A logo with black type on an
opaque background sits on its own light plate so it stays legible in dark mode
without being recoloured.

## Colour

The palette is computed, not chosen. `tools/palette.py` builds the diverging ramp
and validates it with OKLab and the Machado (2009) CVD transforms:

```bash
python tools/palette.py
```

Two deliberate departures from the Tableau original:

- **Red↔blue, not red↔green.** The original's red-yellow-green poles measure a
  CVD ΔE of **5.1** against a target of 8 — under deuteranopia gains and losses
  collapse toward the same olive, so the sign of the change stops being legible.
  Red↔blue measures 17.9. The original palette is still available in the Palette
  dropdown, labelled as such.
- **The scale is symmetric around zero.** The original spans the raw min→max
  (−32.90 → 25.10), which puts zero off the colour midpoint so a −20k loss and a
  +20k gain render at different intensities — a bias the eye reads as data.

Missing observations render as a **hatch**, not a flat grey: BLS publishes
detailed industries a month behind the headline aggregates, and a grey tile sits
close enough to the neutral midpoint (indistinguishable in dark mode) that a
missing value would read as a real zero change.

## Development

```bash
.venv/bin/python -m pytest              # 48 tests
python tools/palette.py                 # palette validation report
python tools/probe.py                   # render interaction states to dist/_probe/*.png
```

`tests/test_frontend.py` drives the real shipped JS in headless Chrome through
the `window.__treemap` seam, so the treemap layout and anomaly maths are tested
as they ship rather than as a Python reimplementation.
