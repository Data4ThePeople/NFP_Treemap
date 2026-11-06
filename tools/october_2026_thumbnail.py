"""Video thumbnail for the October 2026 reaction video, same layout as video/thumbnail.py.

The explorer at level 3, October 2026, one month, on the viz's light paper beside the headline.
Size matches the video's aspect ratio (1200x842), rendered at 2x, so LinkedIn doesn't crop it.

  .venv/bin/python tools/october_2026_thumbnail.py
  -> posts/october-2026-jobs-report/social/october-2026-levels-thumbnail.jpg
"""
import base64
import io
import json
import sys
import time
from pathlib import Path

import pandas as pd
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "video"))
from build_video import INK, PAPER, VIDEO, Chrome  # noqa: E402

TW, TH, DSF = 1200, 842, 2
OUT = ROOT / "posts" / "october-2026-jobs-report" / "social"
BUILD = OUT / "build"
KICKER_BLUE = "#256abf"


def total_change():
    obs = pd.read_parquet(ROOT / "data" / "ces_observations.parquet")
    s = obs[obs.industry_code == "00000000"].set_index("date")["employees"]
    return int(round((s[pd.Timestamp("2026-10-01")] - s[pd.Timestamp("2026-09-01")]) * 1000))


def treemap_shot(ch):
    ch.cmd("Emulation.setDeviceMetricsOverride", width=980, height=900, deviceScaleFactor=2, mobile=False)
    ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&theme=light&base=2026-10&h=1mo&lvl=3")
    for _ in range(120):
        time.sleep(0.25)
        try:
            if ch.js("!!(window.__treemap && document.querySelector('.tile'))"):
                break
        except Exception:
            pass
    time.sleep(1.5)
    st = ch.js("({lvl: __treemap.state.level, base: __treemap.state.base})")
    assert st == {"lvl": 3, "base": "2026-10"}, st
    r = ch.js("(() => { const r = document.getElementById('treemap').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
    d = ch.cmd("Page.captureScreenshot", format="png",
               clip=dict(x=r[0], y=r[1], width=r[2], height=r[3], scale=1))["data"]
    return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")


def main():
    BUILD.mkdir(parents=True, exist_ok=True)
    total = total_change()
    ch = Chrome(port=9391)
    try:
        treemap_shot(ch).save(BUILD / "thumb-treemap.png")
        logo = f'<img class="logo" src="file://{VIDEO / "assets" / "d4tp-text-dark.svg"}" alt="">'
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;width:{TW}px;height:{TH}px;overflow:hidden;background:{PAPER};color:{INK};
          font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
        .top{{position:absolute;left:50px;right:50px;top:26px;display:flex;align-items:center;justify-content:space-between}}
        .logo{{height:36px;width:auto;display:block}}
        .kicker{{background:{KICKER_BLUE};color:#fff;font-weight:800;font-size:24px;letter-spacing:.12em;
          text-transform:uppercase;padding:7px 16px 5px;border-radius:8px}}
        .head{{position:absolute;left:50px;right:50px;top:78px;display:flex;align-items:center;gap:30px}}
        h1{{font-size:84px;line-height:1;margin:0;font-weight:800;letter-spacing:-.01em;white-space:nowrap}}
        .big{{color:{KICKER_BLUE}}}
        .sub{{font-size:27px;color:#5F6B67;font-weight:600;line-height:1.2}}
        .map{{position:absolute;left:50%;bottom:22px;transform:translateX(-50%);width:1060px;height:auto;
          border-radius:12px;box-shadow:0 14px 40px rgba(0,0,0,.18)}}
        </style></head><body>
        <div class="top"><div class="kicker">October jobs report</div>{logo}</div>
        <div class="head"><h1><span class="big">{total:+,}</span> jobs</h1>
          <div class="sub">Every industry, from the headline down</div></div>
        <img class="map" src="file://{BUILD / 'thumb-treemap.png'}">
        </body></html>"""
        p = BUILD / "thumbnail.html"
        p.write_text(html)
        ch.cmd("Emulation.setDeviceMetricsOverride", width=TW, height=TH, deviceScaleFactor=DSF, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.5)
        out = OUT / "october-2026-levels-thumbnail.jpg"
        ch.shot().save(out, quality=90, optimize=True)
        print("wrote", out.relative_to(ROOT), f"{out.stat().st_size / 1e6:.2f} MB", Image.open(out).size)
    finally:
        ch.close()


if __name__ == "__main__":
    main()
