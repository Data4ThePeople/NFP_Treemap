"""Social GIF and MP4: the U.S. Jobs Data Explorer stepping from level 0 to level 5, October 2026.

Drives the built explorer (dist/index.html, embed view, light theme) in headless Chrome through
the Chrome class in video/build_video.py, switches the Display level menu 0..5, and screenshots
each level. Each frame gets a caption strip on top. Levels hold, crossfade, the last one holds
longer, then the GIF loops.

  .venv/bin/python tools/october_2026_level_gif.py
  -> posts/october-2026-jobs-report/social/october-2026-levels.gif  (and .mp4, contact-sheet.png)

Caption counts are read from the page and from data/ces_observations.parquet at run time.
"""
import json
import sys
import time
from pathlib import Path

import imageio_ffmpeg
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "video"))
from build_video import Chrome  # noqa: E402

OUT = ROOT / "posts" / "october-2026-jobs-report" / "social"
BASE, PREV = "2026-10", "2026-09"
VW, VH, DSF = 1200, 750, 1.5       # page viewport (CSS px); screenshot is VW*DSF wide
W = 1200                           # output width
STRIP = 92                         # caption strip height
INK, PAPER, MUTED = "#1F2A27", "#F7F5EF", "#5C6166"
SANS = "/System/Library/Fonts/SFNS.ttf"
FPS = 20
HOLD, FADE, LAST = 1.6, 0.4, 5.0   # seconds


def font(size, bold=False):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


def counts():
    """Captions from the data, not typed in."""
    ind = pd.DataFrame(json.load(open(ROOT / "data" / "industries.json"))["industries"]).set_index("code")
    obs = pd.read_parquet(ROOT / "data" / "ces_observations.parquet")
    w = obs.pivot(index="industry_code", columns="date", values="employees")
    chg = (w[pd.Timestamp(BASE + "-01")] - w[pd.Timestamp(PREV + "-01")]).round(1)
    ind = ind.join(chg.rename("chg"))
    total = int(round(ind.loc["00000000", "chg"] * 1000))
    lv = lambda n: ind[(ind.level == n) & (~ind.composite)]
    return {
        "total": total,
        "l2_n": len(lv(2)), "l2_up": int((lv(2).chg > 0).sum()),
        "l3_n": len(lv(3)), "l3_up": int((lv(3).chg > 0).sum()),
    }


def caption(level, c, tiles, gap_text):
    title = {
        0: f"Level 0: Total nonfarm, {c['total']:+,} jobs",
        1: f"Level 1: {tiles} broad groups, which overlap",
        2: f"Level 2: {c['l2_n']} sectors, {c['l2_up']} added jobs",
        3: f"Level 3: {c['l3_n']} industries, {c['l3_up']} added jobs",
        4: f"Level 4: {tiles} industries",
        5: f"Level 5: {gap_text}",
    }[level]
    return title


def strip(img, text):
    out = Image.new("RGB", (W, img.height + STRIP), PAPER)
    out.paste(img, (0, STRIP))
    d = ImageDraw.Draw(out)
    d.text((28, 14), "October 2026 jobs report, first estimate", font=font(22), fill=MUTED)
    d.text((28, 44), text, font=font(30, bold=True), fill=INK)
    d.line([(0, STRIP - 1), (W, STRIP - 1)], fill="#D9D6CC", width=1)
    return out


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    c = counts()
    ch = Chrome(port=9381)
    shots = []
    try:
        ch.cmd("Emulation.setDeviceMetricsOverride", width=VW, height=VH, deviceScaleFactor=DSF, mobile=False)
        ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&base={BASE}&h=1mo&lvl=0&m=abs&theme=light")
        for _ in range(120):
            time.sleep(0.25)
            try:
                if ch.js("!!(window.__treemap && document.querySelector('.tile'))"):
                    break
            except Exception:
                pass
        time.sleep(0.8)
        for level in range(6):
            ch.js(f"(() => {{ const s = document.querySelector('#level'); s.value = '{level}';"
                  " s.dispatchEvent(new Event('change')); })()")
            ch.frame_done()
            time.sleep(0.6)
            st = ch.js("({lvl: __treemap.state.level, base: __treemap.state.base, h: __treemap.state.horizon})")
            assert st == {"lvl": level, "base": BASE, "h": "1mo"}, st
            tiles = ch.js("document.querySelectorAll('.tile').length")
            gap = ch.js("(() => { const m = document.body.innerText.match(/(\\d+) of (\\d+) industries have no value/);"
                        " return m ? [+m[1], +m[2]] : null; })()")
            gap_text = ""
            if level == 5:
                assert gap, "expected the page's unpublished-industries note at level 5"
                missing, n = gap
                gap_text = f"{n} detailed industries, {n - missing} with October numbers so far"
            img = ch.shot().resize((W, round(VH * W / VW)), Image.LANCZOS)
            shots.append(strip(img, caption(level, c, tiles, gap_text)))
            print(f"level {level}: {tiles} tiles  {caption(level, c, tiles, gap_text)}")
    finally:
        ch.close()

    # Timeline: hold, crossfade to the next, ..., long hold on the last.
    frames, durs = [], []
    nfade = max(1, round(FADE * FPS))
    for i, s in enumerate(shots):
        last = i == len(shots) - 1
        frames.append(s)
        durs.append(LAST if last else HOLD)
        if not last:
            for k in range(1, nfade + 1):
                frames.append(Image.blend(s, shots[i + 1], k / (nfade + 1)))
                durs.append(1 / FPS)

    # GIF: one shared palette built from all six levels, so colors don't shimmer between frames.
    ref = Image.new("RGB", (W, shots[0].height * len(shots)))
    for i, s in enumerate(shots):
        ref.paste(s, (0, i * s.height))
    pal = ref.quantize(colors=256, method=Image.Quantize.MEDIANCUT)
    q = [f.quantize(palette=pal, dither=Image.Dither.NONE) for f in frames]
    gif = OUT / "october-2026-levels.gif"
    q[0].save(gif, save_all=True, append_images=q[1:], duration=[round(d * 1000) for d in durs],
              loop=0, optimize=True, disposal=1)
    print(f"wrote {gif.relative_to(ROOT)}  {gif.stat().st_size / 1e6:.2f} MB  {len(q)} frames  {sum(durs):.1f} s")

    # MP4 for LinkedIn: same timeline at a constant 30 fps, H.264, even dimensions.
    mp4 = OUT / "october-2026-levels.mp4"
    h = shots[0].height + shots[0].height % 2
    writer = imageio_ffmpeg.write_frames(str(mp4), (W, h), fps=30, codec="libx264", pix_fmt_out="yuv420p",
                                         macro_block_size=1, output_params=["-crf", "18", "-movflags", "+faststart"])
    writer.send(None)
    for f, d in zip(frames, durs):
        canvas = Image.new("RGB", (W, h), PAPER)
        canvas.paste(f, (0, 0))
        buf = np.asarray(canvas).tobytes()
        for _ in range(max(1, round(d * 30))):
            writer.send(buf)
    writer.close()
    print(f"wrote {mp4.relative_to(ROOT)}  {mp4.stat().st_size / 1e6:.2f} MB")

    # Contact sheet for review.
    th = [s.resize((W // 2, s.height // 2), Image.LANCZOS) for s in shots]
    sheet = Image.new("RGB", (W, th[0].height * 3), "white")
    for i, t in enumerate(th):
        sheet.paste(t, ((i % 2) * (W // 2), (i // 2) * t.height))
    sheet.save(OUT / "contact-sheet.png")


if __name__ == "__main__":
    main()
