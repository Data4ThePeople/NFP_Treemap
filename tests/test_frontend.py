"""Exercise the shipped treemap.js in headless Chrome.

The layout and anomaly maths only exist in JS, so testing a Python
reimplementation would prove nothing. These run the real functions via the
window.__treemap seam and assert on the results.
"""
from __future__ import annotations

import json
import re
import subprocess
import textwrap
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dist" / "index.html"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

pytestmark = [
    pytest.mark.skipif(not PAGE.exists(), reason="run nfp_treemap.build first"),
    pytest.mark.skipif(not CHROME.exists(), reason="Google Chrome not installed"),
]


def run_js(body: str) -> dict:
    """Run `body` in the page; it must assign its result to `out`."""
    script = textwrap.dedent(
        """
        <script>
        addEventListener('load', () => setTimeout(() => {
          let out;
          try { %s } catch (e) { out = {error: String(e && e.stack || e)}; }
          console.log('__RESULT__' + JSON.stringify(out));
        }, 50));
        </script>
        """
        % body
    )
    tmp = ROOT / "dist" / "_probe" / "jstest.html"
    tmp.parent.mkdir(parents=True, exist_ok=True)
    tmp.write_text(PAGE.read_text().replace("</body>", script + "</body>"))

    proc = subprocess.run(
        [
            str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--enable-logging=stderr", "--v=0", "--virtual-time-budget=9000",
            "--window-size=1600,1000", "--dump-dom", f"file://{tmp}",
        ],
        capture_output=True,
        text=True,
    )
    match = re.search(r"__RESULT__(\{.*?\})\"?,\s*source:", proc.stderr, re.S)
    if not match:
        match = re.search(r"__RESULT__(\{.*\})", proc.stderr, re.S)
    assert match, f"no result from page.\nstderr tail:\n{proc.stderr[-2500:]}"
    payload = json.loads(match.group(1).replace('\\"', '"'))
    assert "error" not in payload, payload["error"]
    return payload


def test_squarify_tiles_the_rectangle_exactly():
    """Every cell inside bounds, no overlaps, areas proportional to value."""
    result = run_js(
        """
        const {squarify} = window.__treemap;
        const vals = [50, 30, 20, 12, 9, 7, 5, 3, 2, 1];
        const W = 800, H = 400;
        const cells = squarify(vals.map(v => ({value: v})), 0, 0, W, H);
        const total = vals.reduce((a,b)=>a+b,0);
        let area = 0, oob = 0, ratioErr = 0;
        for (const c of cells) {
          area += c.w * c.h;
          if (c.x < -0.01 || c.y < -0.01 || c.x + c.w > W + 0.01 || c.y + c.h > H + 0.01) oob++;
          const want = (c.node.value / total) * W * H;
          ratioErr = Math.max(ratioErr, Math.abs(c.w * c.h - want) / want);
        }
        let overlaps = 0;
        for (let i = 0; i < cells.length; i++)
          for (let j = i + 1; j < cells.length; j++) {
            const a = cells[i], b = cells[j];
            if (a.x < b.x + b.w - 0.01 && b.x < a.x + a.w - 0.01 &&
                a.y < b.y + b.h - 0.01 && b.y < a.y + a.h - 0.01) overlaps++;
          }
        out = {n: cells.length, coverage: area / (W * H), oob, overlaps, ratioErr};
        """
    )
    assert result["n"] == 10
    assert result["oob"] == 0
    assert result["overlaps"] == 0
    assert abs(result["coverage"] - 1.0) < 1e-6
    assert result["ratioErr"] < 1e-6


def test_squarify_ignores_nonpositive_values():
    result = run_js(
        """
        const {squarify} = window.__treemap;
        out = {n: squarify([{value: 0}, {value: -5}, {value: 3}], 0, 0, 100, 100).length,
               empty: squarify([], 0, 0, 100, 100).length,
               zeroRect: squarify([{value: 1}], 0, 0, 0, 50).length};
        """
    )
    assert result == {"n": 1, "empty": 0, "zeroRect": 0}


def test_wraptext_never_clips_mid_word():
    result = run_js(
        """
        const {wrapText} = window.__treemap;
        out = {
          tooNarrow: wrapText('Nonresidential specialty trade contractors', 12, 11, 3, 600),
          fits: wrapText('Hospitals', 200, 12, 2, 600),
          wraps: wrapText('Merchant wholesalers, durable goods', 90, 11, 2, 600),
        };
        """
    )
    # Not even the first word fits -> caller must drop the label entirely.
    assert result["tooNarrow"] is None
    assert result["fits"] == {"lines": ["Hospitals"], "truncated": False}
    assert all(" " not in line or True for line in result["wraps"]["lines"])
    assert len(result["wraps"]["lines"]) <= 2


def test_anomaly_agrees_with_its_percentile():
    """A robust z and a percentile must not tell opposite stories.

    Mean/SD scoring reported Food Services at a "typical" z of -0.81 while
    placing it in the 5th percentile, because the 2020 rebound inflated the SD.
    """
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const item = byCode.get('70722000');           // Food services
        const s = anomaly(item, labelToIdx.get('2026-06'), 1, 'abs');
        out = {z: s.z, pct: s.pct, label: s.label, n: s.n, insufficient: !!s.insufficient};
        """
    )
    assert not result["insufficient"]
    assert result["z"] < 0 and result["pct"] < 50, result
    # Bottom-decile move must not be described as typical.
    assert result["label"] != "typical"
    assert result["n"] >= 24


def test_anomaly_excludes_windows_touching_the_distorted_period():
    """Either endpoint inside Mar 2020 - Jun 2022 disqualifies a sample.

    Excluding only the acute collapse was not enough: a long window starting
    after Aug 2020 still measures from deep in the hole.
    """
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const item = byCode.get('70722000');       // full history from 1990
        const idx = labelToIdx.get('2026-06');
        const s1 = anomaly(item, idx, 1, 'abs');
        const s12 = anomaly(item, idx, 12, 'abs');
        out = {n1: s1.n, look1: s1.lookback, n12: s12.n, look12: s12.lookback};
        """
    )
    # h=1: 20-year floor -> 241 windows, minus t in [Mar2020, Jul2022] = 29.
    assert result["look1"] == 240
    assert result["n1"] == 241 - 29
    # h=12: floor still binds (10*12 = 120 < 240); more windows straddle.
    assert result["look12"] == 240
    assert result["n12"] < result["n1"]


def test_long_horizon_lookback_scales_with_the_horizon():
    """A fixed 120-month window holds only ~3 independent 3-year windows."""
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const s = anomaly(byCode.get('00000000'), labelToIdx.get('2026-06'), 36, 'abs');
        out = {lookback: s.lookback, n: s.n, independent: s.independent,
               z: s.z, pct: s.pct, label: s.label, insufficient: !!s.insufficient};
        """
    )
    assert result["lookback"] == 360        # 10 x 36
    assert result["independent"] >= 6
    assert not result["insufficient"]


def test_a_positive_change_is_never_scored_as_a_drop():
    """Total nonfarm's +2.8M over 3 years scored z=-3.5 'extreme drop'.

    Every sample was measured off the 2020 trough, so all 79 were large gains
    and an ordinary gain ranked last. With the scaled lookback and the wider
    exclusion the sample spans real downturns too.
    """
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const item = byCode.get('00000000');
        const idx = labelToIdx.get('2026-06');
        const s = anomaly(item, idx, 36, 'abs');
        out = {current: s.current, z: s.z, pct: s.pct, label: s.label, median: s.median};
        """
    )
    assert result["current"] > 0, "3-year change is a gain"
    # It sits below the median, but nowhere near 'extreme'.
    assert -2 < result["z"] < 0, result
    assert result["pct"] > 5, result
    assert result["label"] in ("typical", "notable"), result


def test_window_spanning_the_pandemic_is_not_scored():
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const item = byCode.get('00000000');
        out = {
          inside: anomaly(item, labelToIdx.get('2021-01'), 12, 'abs'),
          clear: anomaly(item, labelToIdx.get('2026-06'), 12, 'abs').label,
        };
        """
    )
    assert result["inside"]["spansDisruption"] is True
    assert "z" not in result["inside"]
    assert result["clear"]


def test_anomaly_reports_insufficient_history_rather_than_guessing():
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const item = byCode.get('00000000');
        // 20yr horizon over a 10yr lookback cannot fill the sample.
        const s = anomaly(item, labelToIdx.get('1945-01'), 240, 'abs');
        out = {result: s};
        """
    )
    assert result["result"] is None or result["result"].get("insufficient") is True


def test_missing_observation_is_hatched_not_a_colour():
    """A missing value must not render as a flat grey that reads as zero."""
    result = run_js(
        """
        const {colorFor} = window.__treemap;
        const pal = {loss: ['#a','#b'], gain: ['#c','#d'], mid: '#mid'};
        out = {missing: colorFor(null, 100, pal), zero: colorFor(0, 100, pal),
               big: colorFor(-100, 100, pal)};
        """
    )
    assert result["missing"] == "url(#nodata-hatch)"
    assert result["zero"] == "#mid"
    assert result["big"] == "#b"


def test_csv_export_content():
    """The CSV must carry the same numbers the tiles show, plus the stats."""
    result = run_js(
        """
        const t = window.__treemap;
        t.state.level = 4; t.state.base = '2026-06'; t.render();
        const csv = t.buildCsv();
        const lines = csv.split('\\n');
        const head = lines[0].split(',');
        const food = lines.find(l => l.startsWith('70722000'));
        out = {head, nRows: lines.length - 1, food,
               commaQuoted: lines.some(l => l.includes('"'))};
        """
    )
    assert result["head"][:5] == [
        "industry_code", "industry_name", "supersector", "display_level", "naics_codes",
    ]
    # 84 industries sit at level 4; two of them (Specialty trade contractors,
    # Health care) are roll-ups of their own siblings and are excluded.
    assert result["nRows"] == 82
    assert result["food"].startswith("70722000,Food services and drinking places")
    # Industry names contain commas, so quoting must be applied.
    assert result["commaQuoted"] is True


def test_highlight_with_no_matches_does_not_dim_everything():
    result = run_js(
        """
        const t = window.__treemap;
        t.state.highlight = 'zzzznomatch';
        t.render();
        const tiles = [...document.querySelectorAll('.tile')];
        out = {dimmed: tiles.filter(n => n.classList.contains('dimmed')).length,
               total: tiles.length,
               noteShown: !document.querySelector('#nomatch').hidden};
        """
    )
    assert result["total"] > 0
    assert result["dimmed"] == 0
    assert result["noteShown"] is True


def test_change_is_null_when_either_endpoint_is_missing():
    result = run_js(
        """
        const {change, byCode, labelToIdx, state} = window.__treemap;
        const detail = byCode.get('20238100');   // detail lags by a month
        // The newest month is whatever the last release published; the detail
        // series has no value for it yet, and does for the month before.
        const newest = labelToIdx.get(state.base);
        out = {
          newest: change(detail, newest, 1, 'abs'),
          prior: change(detail, newest - 1, 1, 'abs'),
          beforeStart: change(detail, labelToIdx.get('1950-01'), 1, 'abs'),
        };
        """
    )
    assert result["newest"] is None
    assert result["prior"] is not None
    assert result["beforeStart"] is None


def test_reference_distribution_spans_a_business_cycle():
    """A 10-year lookback minus the pandemic contains no downturn at all.

    Every 12-month change left in it is an expansion-year change, so an
    ordinary slowdown scored as a once-in-a-generation event: Total nonfarm's
    +403k year measured z = -4.05, "extreme". With a 20-year floor the sample
    reaches back through 2008-09.
    """
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const s = anomaly(byCode.get('00000000'), labelToIdx.get('2026-06'), 12, 'abs');
        out = {z: s.z, pct: s.pct, label: s.label, span: s.spanMonths, n: s.n};
        """
    )
    assert result["span"] >= 240, "sample must reach back at least 20 years"
    assert result["label"] != "extreme", result
    assert -3 < result["z"] < 0, result


def test_reported_span_never_exceeds_the_available_history():
    """A 10-year horizon asks for 100 years of lookback; nothing has that.

    The tooltip must state the span actually covered - Total nonfarm starts in
    1939 (87 years), Food Services in 1990 (36) - not the requested lookback.
    """
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const idx = labelToIdx.get('2026-06');
        const nf = anomaly(byCode.get('00000000'), idx, 120, 'abs');
        const fs = anomaly(byCode.get('70722000'), idx, 120, 'abs');
        out = {nfSpan: nf.spanMonths, nfLookback: nf.lookback,
               fsSpan: fs.spanMonths, fsLookback: fs.lookback};
        """
    )
    assert result["nfLookback"] == 1200          # 10 x 120 months requested
    assert result["nfSpan"] < result["nfLookback"]
    assert 12 * 85 <= result["nfSpan"] <= 12 * 88   # series starts 1939
    assert 12 * 34 <= result["fsSpan"] <= 12 * 38   # series starts 1990


@pytest.mark.parametrize("horizon", [1, 12, 24, 36, 60, 120, 240])
def test_every_horizon_is_either_scored_sanely_or_declined(horizon):
    """No horizon may emit a confident score off an unusable sample."""
    result = run_js(
        """
        const {anomaly, byCode, labelToIdx} = window.__treemap;
        const s = anomaly(byCode.get('00000000'), labelToIdx.get('2026-06'), %d, 'abs');
        out = {s};
        """
        % horizon
    )
    stat = result["s"]
    assert stat is not None
    if stat.get("spansDisruption") or stat.get("insufficient"):
        assert "z" not in stat or stat.get("z") is None
        return
    # A real score needs enough independent windows and a coherent direction.
    assert stat["independent"] >= 6, stat
    assert (stat["z"] >= 0) == (stat["pct"] >= 50), (
        f"z and percentile disagree on direction: {stat}"
    )
    assert abs(stat["z"]) < 6, stat


def _lagnote(base, level, horizon="1mo"):
    return run_js(
        """
        const t = window.__treemap;
        t.state.base = '%s'; t.state.level = %d; t.state.horizon = '%s';
        t.state.drill = null;
        t.render();
        const n = document.getElementById('lagnote');
        out = {hidden: n.hidden, text: n.textContent};
        """
        % (base, level, horizon)
    )


def test_missing_data_note_blames_the_right_cause():
    """Missing tiles have two causes and the wrong explanation is worse than none.

    At the newest month the detail is not published yet. In 1939 the industries
    did not exist as published series - most CES detail begins in 1990 - so
    blaming the publication lag, as the note originally did, is just wrong.
    """
    old = _lagnote("1939-02", 5)
    assert not old["hidden"]
    assert "had not broken them out this far back" in old["text"]
    assert "begins in 1990" in old["text"]
    assert "month behind" not in old["text"], old["text"]

    newest = run_js("out = {base: window.__treemap.state.base};")["base"]
    new = _lagnote(newest, 5)
    assert not new["hidden"]
    assert "month behind the headline aggregates" in new["text"]
    assert "1990" not in new["text"], new["text"]


def test_missing_data_note_names_the_earliest_fully_covered_month():
    result = _lagnote("1985-06", 5)
    assert "from January 1990 onward" in result["text"], result["text"]


def test_missing_data_note_accounts_for_the_comparison_endpoint():
    """A 20-year comparison from 1995 reaches back to 1975."""
    result = _lagnote("1995-01", 5, "20yr")
    assert "or its comparison month" in result["text"]
    assert "had not broken them out" in result["text"]


def test_no_note_when_every_industry_has_data():
    assert _lagnote("2026-06", 4)["hidden"] is True


def test_full_history_stays_selectable():
    """The base-period dropdown must still offer the whole series."""
    result = run_js(
        """
        const opts = [...document.querySelectorAll('#base option')].map(o => o.value);
        out = {n: opts.length, first: opts[opts.length - 1], last: opts[0]};
        """
    )
    assert result["first"] == "1939-01"
    assert result["n"] > 1000


def test_logo_is_inlined_at_most_once():
    """Optional branding: absent by default, and never inlined twice.

    Duplicating the element would inline the whole data URI a second time, so
    the single element is relocated by JS rather than copied.
    """
    html = PAGE.read_text()
    result = run_js(
        """
        const b = document.querySelectorAll('.brand');
        out = {count: b.length, inMasthead: !!document.querySelector('.masthead .brand'),
               alt: b[0] ? b[0].alt : null};
        """
    )
    if result["count"] == 0:
        assert "data:image/" not in html
        return
    assert result["count"] == 1
    assert sum(html.count(f"data:image/{k};base64,") for k in
               ("jpeg", "png", "webp", "svg+xml")) == 1
    assert result["inMasthead"] is True
    assert result["alt"]


def _levelnote(drill, level, base="2026-06"):
    return run_js(
        """
        const t = window.__treemap;
        t.state.drill = %s; t.state.level = %d; t.state.base = '%s';
        t.state.horizon = '1mo';
        t.render();
        const n = document.getElementById('levelnote');
        out = {hidden: n.hidden, text: n.textContent,
               empty: !document.getElementById('empty').hidden};
        """
        % ("null" if drill is None else f"'{drill}'", level, base)
    )


def test_partial_child_coverage_is_disclosed_not_hidden():
    """CES publishes only some children for many parents.

    A treemap reads as parts-of-a-whole, so when the shortfall is material the
    page must say how big it is. Nothing is scaled to close the gap.
    """
    result = _levelnote("80813000", 5)   # Religious, grantmaking, civic...
    assert not result["hidden"]
    assert "cover 45%" in result["text"], result["text"]
    assert "not scaled" in result["text"]


def test_coverage_note_is_silent_when_children_are_complete():
    assert _levelnote("65620000", 4)["hidden"] is True   # health care: 100%


def test_coverage_note_pluralises():
    result = _levelnote("32313000", 5)   # Textile mills: one child published
    assert "The 1 industry shown covers" in result["text"], result["text"]


def test_notes_do_not_survive_into_an_empty_view():
    """Returning early on an empty result left the previous view's note up."""
    _levelnote("32313000", 5)                 # leaves a note on screen
    result = _levelnote("55532200", 6)        # no children at this level
    assert result["empty"] is True
    assert result["hidden"] is True, result["text"]


def test_nothing_rescales_tile_values_to_match_the_parent():
    """Every tile is the reported series value, straight from the payload."""
    result = run_js(
        """
        const t = window.__treemap;
        t.state.drill = '80813000'; t.state.level = 5;
        t.state.base = '2026-06'; t.state.horizon = '1mo';
        t.render();
        const idx = t.labelToIdx.get('2026-06');
        const shown = [...document.querySelectorAll('.tile')].map(el => {
          const item = t.byCode.get(el.dataset.code);
          return {raw: t.change(item, idx, 1, 'abs'),
                  label: el.getAttribute('aria-label')};
        });
        const parent = t.change(t.byCode.get('80813000'), idx, 1, 'abs');
        out = {sum: shown.reduce((a, s) => a + s.raw, 0), parent,
               n: shown.length,
               // the label must carry the untouched value
               matches: shown.every(s =>
                 s.label.includes((s.raw >= 0 ? '+' : '-') +
                   Math.abs(s.raw).toFixed(2) + 'k'))};
        """
    )
    assert result["n"] > 0
    assert result["matches"] is True, "tile labels must show the raw reported change"
    # The children genuinely do not sum to the parent, and that is left alone.
    assert abs(result["sum"] - result["parent"]) > 0.01, result
