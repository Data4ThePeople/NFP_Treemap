"""Layout at phone widths and inside a fixed-height iframe.

Headless Chrome clamps its own window to 500px wide, so `--window-size=390`
renders at 500 and crops - which reads as an overflow bug that isn't there, and
hides real ones. An iframe gets its own viewport at any size, so these load the
page in one and measure from the (same-origin) parent.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "dist" / "index.html"
OUT = ROOT / "dist" / "_probe"
CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")

pytestmark = [
    pytest.mark.skipif(not PAGE.exists(), reason="run nfp_treemap.build first"),
    pytest.mark.skipif(not CHROME.exists(), reason="Google Chrome not installed"),
]

WRAPPER = """<!doctype html><meta charset="utf-8">
<style>html,body{margin:0}iframe{border:0;width:%(w)dpx;height:%(h)dpx;display:block}</style>
<iframe id="f" src="../index.html%(hash)s"></iframe>
<script>
/* The chart sizes itself from the space left below the notes, and the legend
   height it needs is only real after the first paint - so there is a reflow
   shortly after load. Sampling at a fixed delay raced it and failed on a
   different frame size each run. Wait for the layout to stop moving instead:
   two identical samples in a row, then measure. */
addEventListener('load', () => {
  const f = document.getElementById('f');
  let last = null, stable = 0, waited = 0;
  const probe = () => {
    const d = f.contentDocument;
    const legend = d && d.querySelector('.legend-row');
    const svg = d && d.getElementById('treemap');
    if (!legend || !svg) return null;
    return Math.round(legend.getBoundingClientRect().bottom) + ':' +
           Math.round(svg.getBoundingClientRect().height);
  };
  const tick = () => {
    const now = probe();
    stable = (now !== null && now === last) ? stable + 1 : 0;
    last = now;
    waited += 100;
    if ((stable >= 2 && waited >= 300) || waited >= 5000) return measureNow();
    setTimeout(tick, 100);
  };
  setTimeout(tick, 100);

  function measureNow() {
  let out;
  try {
    const d = f.contentDocument, w = f.contentWindow;
    const de = d.documentElement;
    const svg = d.getElementById('treemap');
    const legend = d.querySelector('.legend-row');
    out = {
      innerWidth: w.innerWidth,
      scrollWidth: de.scrollWidth,
      clientWidth: de.clientWidth,
      contentHeight: de.scrollHeight,
      frameHeight: %(h)d,
      embed: de.classList.contains('embed'),
      theme: de.dataset.theme || null,
      bodyBg: w.getComputedStyle(d.body).backgroundColor,
      level: d.getElementById('level').value,
      tiles: d.querySelectorAll('.tile').length,
      wrapWidth: Math.round(d.querySelector('.wrap').getBoundingClientRect().width),
      chartHeight: Math.round(svg.getBoundingClientRect().height),
      controlCols: w.getComputedStyle(d.querySelector('.controls'))
        .gridTemplateColumns.split(' ').filter(Boolean).length,
      svgBottom: Math.round(svg.getBoundingClientRect().bottom),
      legendBottom: Math.round(legend.getBoundingClientRect().bottom),
      overflowing: [...d.querySelectorAll('.wrap *')]
        .filter(el => el.getBoundingClientRect().right > w.innerWidth + 1).length,
    };
  } catch (e) { out = {error: String(e && e.stack || e)}; }
  console.log('__R__' + JSON.stringify(out));
  }
});
</script>"""


def measure(width: int, height: int, hash_: str = "") -> dict:
    OUT.mkdir(parents=True, exist_ok=True)
    name = f"t_{width}x{height}{'_' + hash_.strip('#').replace('=', '') if hash_ else ''}.html"
    wrapper = OUT / name
    wrapper.write_text(WRAPPER % {"w": width, "h": height, "hash": hash_})

    proc = subprocess.run(
        [
            str(CHROME), "--headless=new", "--disable-gpu", "--no-sandbox",
            "--allow-file-access-from-files", "--enable-logging=stderr", "--v=0",
            "--virtual-time-budget=9000",
            f"--window-size={max(520, width + 40)},{height + 80}",
            "--dump-dom", f"file://{wrapper}",
        ],
        capture_output=True,
        text=True,
    )
    match = re.search(r"__R__(\{.*?\})\"?,\s*source:", proc.stderr, re.S) or re.search(
        r"__R__(\{.*\})", proc.stderr, re.S
    )
    assert match, f"no measurement.\nstderr tail:\n{proc.stderr[-2000:]}"
    result = json.loads(match.group(1).replace('\\"', '"'))
    assert "error" not in result, result["error"]
    return result


@pytest.mark.parametrize("width", [320, 390, 430, 768])
def test_no_horizontal_overflow_at_phone_widths(width):
    """Nothing may extend past the viewport at any supported width."""
    result = measure(width, 900, "#embed=0")
    assert result["innerWidth"] == width
    assert result["scrollWidth"] <= result["clientWidth"] + 1, result
    assert result["overflowing"] == 0, result


def test_phone_opens_at_a_readable_level():
    """Even the level-3 sectors crowd a phone; open shallower."""
    narrow = measure(390, 900, "#embed=0")
    wide = measure(1200, 900, "#embed=0")
    assert int(narrow["level"]) < int(wide["level"])
    assert int(wide["level"]) == 3


def test_explicit_level_in_the_url_beats_the_narrow_default():
    result = measure(390, 900, "#embed=0&lvl=4")
    assert result["level"] == "4"


# Measured minimum frame heights. Narrower frames wrap the controls onto more
# rows, so they need more height, not less: at 600px wide the chrome alone is
# ~545px. Below these the chart would have to shrink past the 140px floor, so
# the frame scrolls instead. Documented in the README for the embed host.
SUPPORTED_EMBEDS = [(600, 560), (900, 500), (900, 620), (1100, 520), (1100, 700)]


@pytest.mark.parametrize("size", SUPPORTED_EMBEDS)
def test_embedded_content_fits_the_frame(size):
    """At or above the documented minimums, a fixed-height iframe never scrolls."""
    width, height = size
    result = measure(width, height)
    assert result["embed"] is True, "iframe should auto-detect embed mode"
    assert result["legendBottom"] <= height + 2, result
    assert result["contentHeight"] <= height + 2, result
    assert result["overflowing"] == 0, result


def test_short_narrow_frame_scrolls_rather_than_squashing_the_chart():
    """Below the minimum the chart holds its 140px floor and the frame scrolls.

    Asserted so the trade-off stays deliberate: a 600x500 embed is undersized,
    and the fix is a taller frame, not an unreadable stripe of a treemap.
    """
    result = measure(600, 500)
    assert result["contentHeight"] > 500
    assert result["overflowing"] == 0  # vertical only; never horizontal


def test_embed_mode_can_be_forced_either_way():
    assert measure(900, 620, "#embed=0")["embed"] is False
    assert measure(900, 620, "#embed=1")["embed"] is True


def test_level_zero_renders_total_nonfarm_alone():
    result = measure(1000, 800, "#embed=0&lvl=0")
    assert result["level"] == "0"
    assert result["tiles"] == 1


# --- Prismic embed (Data 4 The People) -------------------------------------
# Measured on the live page: 879px content column, 830px container breakpoint,
# fixed iframe heights (~640 for single-chart tools, 1200-1300 for larger).
# Prismic embeds via oEmbed, so there is no parent-side JS and no auto-resize.
PRISMIC_WIDTH = 879
PRISMIC_BREAKPOINT = 830


@pytest.mark.parametrize("height", [640, 1200, 1300])
def test_prismic_embed_fits_its_fixed_height(height):
    result = measure(PRISMIC_WIDTH, height)
    assert result["embed"] is True
    assert result["contentHeight"] <= height + 2, result
    assert result["overflowing"] == 0, result


@pytest.mark.parametrize("height", [640, 1200, 1300])
def test_prismic_embed_uses_the_height_it_was_given(height):
    """A fixed-height embed should fill its frame, not leave dead space.

    Clamping the chart to min(natural, available) left ~450px blank at
    879x1200, which is the whole point of allocating 1200px.
    """
    result = measure(PRISMIC_WIDTH, height)
    assert result["contentHeight"] >= height - 60, result


def test_layout_switches_at_the_container_breakpoint():
    """Above 830px the controls spread out; below they go two-up.

    Measured with the full layout (#embed=0). In embed mode the denser
    `.embed .controls` rule deliberately overrides the breakpoint, so this
    would report 4 columns on both sides and prove nothing.
    """
    wide = measure(PRISMIC_BREAKPOINT + 60, 900, "#embed=0")
    narrow = measure(PRISMIC_BREAKPOINT - 60, 900, "#embed=0")
    assert wide["controlCols"] > narrow["controlCols"], (wide, narrow)
    assert narrow["controlCols"] == 2


def test_responsive_layout_uses_container_queries_not_media_queries():
    """Viewport media queries misfire inside the oEmbed, so the layout must not
    depend on them.

    Asserted against the CSS source: in this harness the iframe's viewport and
    the page's container are always the same width, so no behavioural test can
    tell the two mechanisms apart. This checks the mechanism directly.
    """
    css = (ROOT / "src" / "nfp_treemap" / "static" / "treemap.css").read_text()
    assert "container: page / inline-size" in css
    assert f"@container page (max-width: {PRISMIC_BREAKPOINT}px)" in css
    # Only colour-scheme media queries are allowed; none may carry layout.
    layout_media = [
        block for block in re.findall(r"@media\s*\(([^)]*)\)", css)
        if "prefers-color-scheme" not in block
    ]
    assert layout_media == [], layout_media


def test_prismic_width_gets_the_desktop_layout():
    """879px sits above the 830px breakpoint."""
    result = measure(PRISMIC_WIDTH, 640)
    assert result["controlCols"] > 2
    assert int(result["level"]) == 3


def test_embedded_defaults_to_light_and_can_still_be_pinned():
    """Embedded, the host page's theme governs and the page cannot read it.

    The host (Data 4 The People) is light, so an embed defaults to light
    rather than letting a dark-mode visitor get a dark chart in a light
    article. Standalone still follows the viewer's OS setting.
    """
    embedded = measure(900, 700)
    standalone = measure(900, 700, "#embed=0")
    dark = measure(900, 700, "#theme=dark")
    light = measure(900, 700, "#theme=light")

    assert embedded["theme"] == "light"     # pinned for the host
    assert standalone["theme"] is None      # no stamp: follows prefers-color-scheme
    assert dark["theme"] == "dark"          # explicit pin still wins inside a frame
    assert light["theme"] == "light"
    # The pin must actually repaint, not just set an attribute.
    assert dark["bodyBg"] != light["bodyBg"]
    assert standalone["bodyBg"] == light["bodyBg"]   # harness runs in light mode
