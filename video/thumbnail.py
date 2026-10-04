"""YouTube thumbnail for the tutorial video: 1280x720 PNG -> video/jobs-data-explorer-thumbnail.png.

Screenshots the treemap (August 2026, level 3, one month) from dist/index.html in headless Chrome,
then sets it on the viz's light paper beside a title in the video's type and colors. Same layout as
the child poverty map thumbnail, with the treemap's blue in place of coral.

  .venv/bin/python video/thumbnail.py
"""
import base64
import io
import time

from PIL import Image

from build_video import BUILD, INK, PAPER, ROOT, VIDEO, Chrome

TW, TH = 1280, 720
OUT = VIDEO / "jobs-data-explorer-thumbnail.png"
KICKER_BLUE = "#256abf"                 # the treemap's gain blue, dark enough for white type


def treemap_shot(ch):
    ch.cmd("Emulation.setDeviceMetricsOverride", width=980, height=960, deviceScaleFactor=2, mobile=False)
    ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&theme=light&base=2026-08&lvl=3")
    for _ in range(120):
        time.sleep(0.25)
        try:
            if ch.js("!!(window.__treemap && document.querySelector('.tile'))"):
                break
        except Exception:
            pass
    time.sleep(1.5)
    r = ch.js("(() => { const r = document.getElementById('treemap').getBoundingClientRect(); return [r.x, r.y, r.width, r.height]; })()")
    d = ch.cmd("Page.captureScreenshot", format="png",
               clip=dict(x=r[0], y=r[1], width=r[2], height=r[3], scale=1))["data"]
    return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")


def main():
    ch = Chrome(port=9355)
    try:
        m = treemap_shot(ch)
        m.save(BUILD / "thumb-treemap.png")
        logo = f'<img class="logo" src="file://{VIDEO / "assets" / "d4tp-text-dark.svg"}" alt="">'
        html = f"""<!doctype html><html><head><meta charset="utf-8"><style>
        html,body{{margin:0;width:{TW}px;height:{TH}px;overflow:hidden;background:{PAPER};color:{INK};
          font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
        .map{{position:absolute;right:-30px;top:50%;transform:translateY(-50%) rotate(-2deg);width:700px;height:auto;
          border-radius:14px;box-shadow:0 18px 50px rgba(0,0,0,.22)}}
        .shade{{position:absolute;inset:0;background:linear-gradient(90deg,{PAPER} 0%,{PAPER} 44%,rgba(247,245,239,.7) 50%,rgba(247,245,239,0) 58%)}}
        .txt{{position:absolute;left:64px;top:0;bottom:0;width:780px;display:flex;flex-direction:column;justify-content:center}}
        .logo{{height:44px;width:auto;display:block;margin-bottom:40px;align-self:flex-start}}
        .kicker{{display:inline-block;align-self:flex-start;background:{KICKER_BLUE};color:#fff;font-weight:800;font-size:30px;
          letter-spacing:.12em;text-transform:uppercase;padding:8px 18px 6px;border-radius:8px;margin-bottom:26px}}
        h1{{font-size:96px;line-height:.98;margin:0;font-weight:800;letter-spacing:-.01em}}
        .sub{{font-size:30px;color:#5F6B67;margin-top:26px;font-weight:600}}
        </style></head><body>
        <img class="map" src="file://{BUILD / 'thumb-treemap.png'}">
        <div class="shade"></div>
        <div class="txt">{logo}<div class="kicker">How to use</div>
          <h1>The U.S. Jobs<br>Data Explorer</h1>
          <div class="sub">Every industry in the monthly jobs report</div></div>
        </body></html>"""
        p = BUILD / "thumbnail.html"
        p.write_text(html)
        ch.cmd("Emulation.setDeviceMetricsOverride", width=TW, height=TH, deviceScaleFactor=1, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.5)
        ch.shot().save(OUT, optimize=True)
        print("wrote", OUT)
    finally:
        ch.close()


if __name__ == "__main__":
    main()
