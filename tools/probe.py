"""Render interaction states of dist/index.html to PNGs via headless Chrome.

    python tools/probe.py tooltip dark drill

Injects a snippet just before </body> that drives the page, so the shipped
file stays untouched.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "dist" / "index.html"
OUT = ROOT / "dist" / "_probe"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

# Each probe is JS run after the page boots.
PROBES = {
    "tooltip": """
      location.hash = '#base=2026-06&h=1mo&lvl=4&m=abs&pal=accessible';
      const t = [...document.querySelectorAll('.tile')]
        .find(n => n.getAttribute('aria-label').startsWith('Food services'));
      t.dispatchEvent(new FocusEvent('focus'));
    """,
    "dark": """
      document.documentElement.setAttribute('data-theme','dark');
      window.dispatchEvent(new Event('resize'));
    """,
    "drill": """
      const t = [...document.querySelectorAll('.tile')]
        .find(n => n.getAttribute('aria-label').startsWith('Specialty trade contractors'));
      t.dispatchEvent(new MouseEvent('click', {bubbles:true}));
    """,
    "pct": """
      document.querySelector('#metric button[data-metric=pct]').click();
    """,
    "classic": """
      const s = document.querySelector('#palette'); s.value='classic';
      s.dispatchEvent(new Event('change'));
    """,
    "narrow": "",
    "iphone": "",
    "iphone_sm": "",
    "ipad": "",
    "embed": "",
    "deeplink": "",
    "hc3yr": """
      const t = [...document.querySelectorAll('.tile')]
        .find(n => n.getAttribute('aria-label').startsWith('Hospitals'));
      t.dispatchEvent(new FocusEvent('focus'));
    """,
    "level0": "",
    "level1": "",
    # CSV/PNG content is covered by tests/test_frontend.py via buildCsv();
    # clicking the buttons here would block headless Chrome on the download.
    "nomatch": """
      const q = document.querySelector('#q'); q.value='manufact';
      q.dispatchEvent(new Event('input'));
    """,
    "deep": """
      const s = document.querySelector('#level'); s.value='6';
      s.dispatchEvent(new Event('change'));
    """,
    "highlight": """
      const q = document.querySelector('#q'); q.value='hospital';
      q.dispatchEvent(new Event('input'));
    """,
}

SIZES = {
    "narrow": (560, 1000),
    "iphone": (390, 844),      # iPhone 15/16 portrait
    "iphone_sm": (320, 700),   # smallest phone still worth supporting
    "ipad": (768, 1024),       # iPad portrait
    "embed": (900, 700),       # typical article-column iframe
}
# Probes that need state restored from the URL rather than driven by script.
HASHES = {
    "hc3yr": "#base=2026-06&h=3yr&lvl=4&m=abs&pal=accessible&drill=65620000",
    "level0": "#base=2026-06&h=1mo&lvl=0&m=abs&pal=accessible",
    "level1": "#base=2026-06&h=1mo&lvl=1&m=abs&pal=accessible",
    "deeplink": "#base=2009-06&h=12mo&lvl=3&m=pct&pal=classic&q=manufact",
}


def run(name: str) -> Path:
    html = SRC.read_text()
    snippet = (
        "<script>addEventListener('load',()=>{setTimeout(()=>{"
        + PROBES[name]
        + "},60)});</script>"
    )
    target = OUT / f"{name}.html"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(html.replace("</body>", snippet + "</body>"))

    shot = OUT / f"{name}.png"
    width, height = SIZES.get(name, (1800, 1250))
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--virtual-time-budget=9000",
            f"--window-size={width},{height}",
            f"--screenshot={shot}", f"file://{target}{HASHES.get(name, '')}",
        ],
        check=True,
        capture_output=True,
    )
    return shot


if __name__ == "__main__":
    names = sys.argv[1:] or list(PROBES)
    for n in names:
        print(run(n))
