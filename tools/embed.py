"""Render the treemap inside an iframe at a given size and screenshot it.

Headless Chrome clamps its window to a 500px minimum, so `--window-size=390`
silently renders at 500 and crops - which looks like an overflow bug that is
not there. An iframe establishes its own viewport at any width, so this is both
the real phone-width test and the embed (Prismic) test.

    python tools/embed.py 390x844 768x1024 900x600
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "dist" / "_probe"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

WRAPPER = """<!doctype html><html><head><meta charset="utf-8"><style>
  html,body{{margin:0;background:#8a8a86;font:12px system-ui}}
  .frame{{margin:14px auto;background:#fff;box-shadow:0 2px 12px rgba(0,0,0,.35)}}
  .cap{{color:#fff;text-align:center;padding:6px}}
  iframe{{display:block;border:0;width:{w}px;height:{h}px}}
</style></head><body>
<div class="cap">{label} — iframe viewport {w}x{h}</div>
<div class="frame" style="width:{w}px"><iframe src="{src}"></iframe></div>
</body></html>"""


def run(spec: str, page: str = "index.html") -> Path:
    """spec is WxH, optionally suffixed ":full" to force the non-embed layout.

    The iframe always trips embed auto-detection, so ":full" (which appends
    #embed=0) is how the real phone layout gets tested through this harness.
    """
    full = spec.endswith(":full")
    spec = spec.removesuffix(":full")
    width, height = (int(v) for v in spec.lower().split("x"))
    OUT.mkdir(parents=True, exist_ok=True)
    tag = f"{width}x{height}{'_full' if full else ''}"
    wrapper = OUT / f"embed_{tag}.html"
    wrapper.write_text(
        WRAPPER.format(w=width, h=height,
                       src=f"../{page}" + ("#embed=0" if full else ""),
                       label=page + (" (full layout)" if full else ""))
    )
    shot = OUT / f"embed_{tag}.png"
    subprocess.run(
        [
            CHROME, "--headless=new", "--disable-gpu", "--no-sandbox",
            "--hide-scrollbars", "--allow-file-access-from-files",
            "--virtual-time-budget=9000",
            f"--window-size={max(520, width + 40)},{height + 90}",
            f"--screenshot={shot}", f"file://{wrapper}",
        ],
        check=True,
        capture_output=True,
    )
    return shot


if __name__ == "__main__":
    specs = sys.argv[1:] or ["390x844", "768x1024", "900x600"]
    for spec in specs:
        print(run(spec))
