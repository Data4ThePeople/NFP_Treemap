"""Tutorial video for the U.S. Jobs Data Explorer: 1920x1080, 30 fps, about 46 s.

Same engine as the child poverty map tutorial (ChildPovertyDistrict/video/build_video.py). Drives the
built treemap (dist/index.html, embed view, light theme) in headless Chrome through the DevTools
protocol: real mouse moves, clicks and hovers, so tooltips, hatches and drill-downs behave as they do
for readers. Each frame is composited with a drawn cursor, click ripples and a typed caption, between
an intro card and a logo card that fades to black. Frames are piped to ffmpeg with
video/build/music.wav (video/music.py).

  .venv/bin/python video/music.py                  # render the music first -> video/build/music.wav
  .venv/bin/python video/build_video.py            # full render -> video/jobs-data-explorer-tutorial.mp4
  .venv/bin/python video/build_video.py --sheet    # stills only -> video/build/contact-sheet.png

Needs imageio-ffmpeg and websocket-client in .venv (video only, not the site build).
"""
import base64
import io
import json
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
VIDEO = ROOT / "video"
BUILD = VIDEO / "build"
OUT = VIDEO / "jobs-data-explorer-tutorial.mp4"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
FPS, W, H = 30, 1920, 1080
VW, VH, DSF = 1600, 900, 1.2            # viz viewport (CSS px) and scale -> the full 1920 x 1080 frame
INK, PAPER, DARK, MUTED = "#1F2A27", "#F7F5EF", "#181A1B", "#8C9094"
BLUE = "#5598e7"                        # the treemap's gain blue, stepped for a dark background
BLUE_RGB = (85, 152, 231)
SANS = "/System/Library/Fonts/SFNS.ttf"
BASE, LOCAL_GOV = "2026-08", "90930000"


# ---------- Chrome over the DevTools protocol ----------
class Chrome:
    def __init__(self, port=9354):
        self.proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={port}",
                                      f"--remote-allow-origins=http://127.0.0.1:{port}", "--hide-scrollbars",
                                      f"--user-data-dir=/tmp/nfp-video-{port}", "about:blank"],
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        for _ in range(60):
            try:
                tabs = json.load(urllib.request.urlopen(f"http://127.0.0.1:{port}/json"))
                break
            except Exception:
                time.sleep(0.25)
        page = [t for t in tabs if t["type"] == "page"][0]
        import websocket
        self.ws = websocket.create_connection(page["webSocketDebuggerUrl"], timeout=120)
        self.i = 0

    def cmd(self, method, **params):
        self.i += 1
        self.ws.send(json.dumps({"id": self.i, "method": method, "params": params}))
        while True:
            m = json.loads(self.ws.recv())
            if m.get("id") == self.i:
                if "error" in m:
                    raise RuntimeError(f"{method}: {m['error']}")
                return m.get("result", {})

    def js(self, expr):
        r = self.cmd("Runtime.evaluate", expression=expr, awaitPromise=True, returnByValue=True)
        if "exceptionDetails" in r:
            raise RuntimeError(f"JS error: {r['exceptionDetails']}\n{expr[:200]}")
        return r["result"].get("value")

    def frame_done(self):
        self.js("new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)))")

    def shot(self):
        d = self.cmd("Page.captureScreenshot", format="png")["data"]
        return Image.open(io.BytesIO(base64.b64decode(d))).convert("RGB")

    def mouse(self, kind, x, y):
        self.cmd("Input.dispatchMouseEvent", type=kind, x=x, y=y, button="left" if kind != "mouseMoved" else "none",
                 clickCount=1 if kind != "mouseMoved" else 0)

    def close(self):
        self.proc.terminate()


# ---------- cards (HTML rendered by Chrome so the type matches the viz) ----------
def logo_img(light=True):
    name = "d4tp-text-light_3.svg" if light else "d4tp-text-dark.svg"
    return f'<img class="logo" src="file://{VIDEO / "assets" / name}" alt="">'


def card_html(body):
    return f"""<!doctype html><html><head><meta charset="utf-8"><style>
    html,body{{margin:0;width:{W}px;height:{H}px;background:{DARK};color:#E4E2DC;
      font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif}}
    .wrap{{position:absolute;inset:0;display:flex;flex-direction:column;align-items:center;justify-content:center;text-align:center}}
    .logo{{height:76px;width:auto;display:block;margin-bottom:56px}}
    .kicker{{font-size:34px;letter-spacing:.14em;text-transform:uppercase;color:{BLUE};font-weight:600;margin-bottom:22px}}
    h1{{font-size:84px;line-height:1.05;margin:0;font-weight:700;max-width:1500px}}
    .sub{{font-size:34px;color:#BBBDC0;margin-top:30px}}
    .rule{{width:120px;height:6px;background:{BLUE};border-radius:3px;margin:40px auto 0}}
    .big .logo{{height:120px;margin-bottom:46px}}
    .url{{font-size:46px;font-weight:600;color:#E4E2DC}}
    .small{{font-size:28px;color:{MUTED};margin-top:18px}}
    </style></head><body>{body}</body></html>"""


def render_cards(ch):
    logo = logo_img()
    intro = card_html(f"""<div class="wrap">{logo}<div class="kicker">Tutorial</div>
      <h1>How to use the<br>U.S. Jobs Data Explorer</h1>
      <div class="sub">Every industry in the monthly BLS jobs report</div><div class="rule"></div></div>""")
    outro = card_html(f"""<div class="wrap big">{logo}<div class="url">Free at data4thepeople.com</div>
      <div class="small">U.S. Jobs Data Explorer, updated after every jobs report</div></div>""")
    cards = {}
    ch.cmd("Emulation.setDeviceMetricsOverride", width=W, height=H, deviceScaleFactor=1, mobile=False)
    for name, html in (("intro", intro), ("outro", outro)):
        p = BUILD / f"{name}.html"
        p.write_text(html)
        ch.cmd("Page.navigate", url=f"file://{p}")
        time.sleep(1.0)
        cards[name] = ch.shot()
        cards[name].save(BUILD / f"card-{name}.png")
    return cards


# ---------- drawing helpers ----------
def font(size, bold=False):
    f = ImageFont.truetype(SANS, size)
    try:
        f.set_variation_by_name("Bold" if bold else "Regular")
    except Exception:
        pass
    return f


CURSOR = [(0, 0), (0, 34), (9, 26), (15, 40), (21, 37), (15, 24), (27, 24)]


def draw_cursor(img, x, y, ripples, t):
    d = ImageDraw.Draw(img, "RGBA")
    for (rt, rx, ry) in ripples:
        a = (t - rt) / 0.45
        if 0 <= a <= 1:
            r = 10 + 46 * a
            d.ellipse([rx - r, ry - r, rx + r, ry + r], outline=(*BLUE_RGB, int(230 * (1 - a))), width=5)
    s = 1.25
    pts = [(x + px * s, y + py * s) for px, py in CURSOR]
    shadow = [(px + 3, py + 4) for px, py in pts]
    d.polygon(shadow, fill=(0, 0, 0, 70))
    d.polygon(pts, fill=(255, 255, 255, 255), outline=(20, 20, 20, 255))
    d.line(pts + [pts[0]], fill=(20, 20, 20, 255), width=2)


def wrap(text, f, maxw, d):
    words, lines, cur = text.split(), [], ""
    for w_ in words:
        trial = (cur + " " + w_).strip()
        if d.textlength(trial, font=f) > maxw and cur:
            lines.append(cur)
            cur = w_
        else:
            cur = trial
    return lines + [cur]


def draw_caption(img, text, t, t0, t1, anchor, step, nsteps):
    """Caption that types in near the action on a dark rounded box and fades out at the end."""
    f, fs = font(46, bold=True), font(24, bold=True)
    d = ImageDraw.Draw(img, "RGBA")
    lines = wrap(text, f, 860, d)              # wrap the full text so lines never reflow while typing
    shown = int(max(0, t - t0 - 0.15) * 25)    # 25 characters a second
    alpha = min(1.0, (t - t0) / 0.2, max(0.0, (t1 - t) / 0.35))
    if alpha <= 0:
        return
    typed, left = [], shown
    for ln in lines:
        typed.append(ln[:max(0, left)])
        left -= len(ln) + 1
    typing = shown < len(text)
    lh, px, py = 58, 30, 22
    boxw = max(d.textlength(ln, font=f) for ln in lines) + 2 * px
    boxh = 34 + len(lines) * lh + 2 * py - 8
    x, y, align = anchor
    if align == "right":
        x -= boxw
    x, y = max(28, min(W - boxw - 28, x)), max(28, min(H - boxh - 28, y))
    a = int(225 * alpha)
    d.rounded_rectangle([x + 4, y + 6, x + boxw + 4, y + boxh + 6], 20, fill=(0, 0, 0, int(60 * alpha)))
    d.rounded_rectangle([x, y, x + boxw, y + boxh], 20, fill=(24, 26, 27, a))
    d.text((x + px, y + py - 4), f"{step} / {nsteps}", font=fs, fill=(*BLUE_RGB, int(255 * alpha)))
    for k, ln in enumerate(typed):
        d.text((x + px, y + py + 30 + k * lh), ln, font=f, fill=(247, 245, 239, int(255 * alpha)))
    if typing and int(t * 3) % 2 == 0:          # caret while typing
        k = max(0, min(len(typed) - 1, next((i for i, ln in enumerate(typed) if len(ln) < len(lines[i])), len(typed) - 1)))
        cx = x + px + d.textlength(typed[k], font=f) + 4
        cy = y + py + 30 + k * lh
        d.rectangle([cx, cy + 6, cx + 4, cy + 50], fill=(*BLUE_RGB, int(255 * alpha)))


def ease(a):
    a = min(1, max(0, a))
    return a * a * (3 - 2 * a)


# ---------- the tour ----------
def main():
    sheet = "--sheet" in sys.argv
    BUILD.mkdir(parents=True, exist_ok=True)
    month = "August 2026"
    TOPRIGHT = lambda: (W - 40, 236, "right")
    BOTRIGHT = lambda: (W - 40, H - 250, "right")
    steps = [
        (4.0, 10.0, "Each tile is an industry. Size is jobs gained or lost. Blue gained, red lost.", BOTRIGHT),
        (10.0, 16.0, f"Pick any month. Here: {month}, after this week's revision.", TOPRIGHT),
        (16.0, 22.0, "Hover for the score. A hatched tile is unusual for that industry.", BOTRIGHT),
        (22.0, 28.0, "Click any tile to drill down. All industries takes you back.", BOTRIGHT),
        (28.0, 34.0, "Compare 1 month to 20 years, in jobs or percent.", BOTRIGHT),
        (34.0, 40.0, "Copy a link to this exact view, or download a CSV or PNG.", BOTRIGHT),
    ]
    ch = Chrome()
    cards = render_cards(ch)
    ch.cmd("Emulation.setDeviceMetricsOverride", width=VW, height=VH, deviceScaleFactor=DSF, mobile=False)
    ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&theme=light")
    for _ in range(120):
        time.sleep(0.25)
        try:
            if ch.js("!!(window.__treemap && document.querySelector('.tile'))"):
                break
        except Exception:
            pass
    # recording only: the clipboard is unavailable to a headless file:// page, so let Copy link succeed
    ch.js("navigator.clipboard && (navigator.clipboard.writeText = async () => {})")
    assert ch.js("__treemap.state.level") == 3 and ch.js("__treemap.state.horizon") == "1mo"
    time.sleep(1.0)
    rect = lambda sel: ch.js(f"(() => {{ const r = document.querySelector({json.dumps(sel)}).getBoundingClientRect(); return [r.x + r.width / 2, r.y + r.height / 2]; }})()")
    tile = lambda code, fx=0.5, fy=0.5: ch.js(f"(() => {{ const r = document.querySelector('.tile[data-code=\"{code}\"] rect').getBoundingClientRect(); return [r.x + r.width * {fx}, r.y + r.height * {fy}]; }})()")
    pick = lambda sel, val: ch.js(f"(() => {{ const s = document.querySelector({json.dumps(sel)}); s.value = {json.dumps(val)}; s.dispatchEvent(new Event('change')); }})()")
    largest = lambda: ch.js("(() => { const area = t => { const r = t.getBoundingClientRect(); return r.width * r.height; };"
                            " return [...document.querySelectorAll('.tile')].sort((a, b) => area(b) - area(a))[0].dataset.code; })()")

    pos = [VW * 0.62, 12.0]       # start above the controls, off the chart, so nothing is hovered
    moves, events, ripples = [], [], []

    def move(t0, t1, target):
        moves.append([t0, t1, target, None, None])

    def click(t):
        def fn():
            x, y = pos
            ch.mouse("mousePressed", x, y)
            ch.mouse("mouseReleased", x, y)
            ripples.append((t, x * DSF, y * DSF))
        events.append((t, fn))

    def at(t, fn):
        events.append((t, fn))

    # beat 1: the legend says what the colors mean
    move(4.4, 5.4, lambda: rect("#legendbar"))
    move(7.6, 8.4, lambda: [VW * 0.30, 30.0])
    # beat 2: base period -> August 2026
    move(10.0, 10.6, lambda: rect("#base"))
    click(10.7)
    at(11.1, lambda: pick("#base", BASE))
    move(12.4, 13.4, lambda: [VW * 0.55, 30.0])
    # beat 3: hover Local government
    move(16.0, 16.9, lambda: tile(LOCAL_GOV, 0.35, 0.35))
    move(17.2, 20.8, lambda: tile(LOCAL_GOV, 0.45, 0.45))     # drift a little so the tooltip feels live
    # beat 4: drill in, look at local government education, then back to all industries
    click(22.4)
    move(23.0, 23.9, lambda: tile(largest(), 0.4, 0.4))
    # Up climbs one level at a time (Local government -> Government -> Service-providing), so go
    # straight back with the first crumb
    move(25.4, 26.2, lambda: rect("#crumbs .crumb"))
    click(26.4)
    # beat 5: one-year comparison, then percent
    move(28.0, 28.6, lambda: rect("#horizon"))
    click(28.7)
    at(29.0, lambda: pick("#horizon", "1yr"))
    move(30.2, 30.9, lambda: rect("#metric button[data-metric='pct']"))
    click(31.0)
    move(31.8, 32.8, lambda: rect("#legendbar"))
    # beat 6: copy link, then point at CSV and PNG
    move(34.1, 34.8, lambda: rect("#link"))
    click(34.9)
    # the page restores the button after 2.2 s of wall time, and a frame takes longer than a frame to
    # render, so hold the confirmation on the video clock instead. It ends before the cursor heads
    # for CSV: "Link copied" is wider and pushes the buttons around while it shows.
    hold = (34.95, 36.4, "document.getElementById('link').textContent = 'Link copied'")
    move(36.5, 37.1, lambda: rect("#csv"))
    move(37.9, 38.5, lambda: rect("#png"))
    events.sort(key=lambda e: e[0])
    anchors = {}

    def anchor_for(i, spec):
        if i not in anchors:
            anchors[i] = spec()
        return anchors[i]

    stills = {5.5: None, 9.0: None, 13.0: None, 19.0: None, 24.5: None, 30.0: None, 33.0: None, 36.0: None}
    ff = None
    if not sheet:
        ff = subprocess.Popen([imageio_ffmpeg.get_ffmpeg_exe(), "-y", "-loglevel", "error",
                               "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                               "-i", str(BUILD / "music.wav"), "-c:v", "libx264", "-preset", "medium", "-crf", "18",
                               "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-shortest",
                               "-movflags", "+faststart", str(OUT)], stdin=subprocess.PIPE)

    nframes = int(46.0 * FPS)
    ei = 0
    last_viz = None
    t_start = time.time()
    for f in range(nframes):
        t = f / FPS
        if t < 3.6:                                  # intro card: fade up from black, slow push-in
            k = 1.04 - 0.04 * ease(t / 3.6)
            c = cards["intro"].resize((int(W * k), int(H * k)))
            c = c.crop(((c.width - W) // 2, (c.height - H) // 2, (c.width - W) // 2 + W, (c.height - H) // 2 + H))
            frame = Image.blend(Image.new("RGB", (W, H), "black"), c, ease(t / 0.9))
        elif t < 40.8:
            while ei < len(events) and events[ei][0] <= t:
                events[ei][1]()
                ei += 1
            for m in moves:                        # cursor position
                t0, t1, target = m[0], m[1], m[2]
                if t0 <= t <= t1 or (t > t1 and m[4] is None and t0 <= t):
                    if m[3] is None:
                        m[3] = list(pos)
                        m[4] = target()
                    a = ease((t - t0) / (t1 - t0))
                    pos[0] = m[3][0] + (m[4][0] - m[3][0]) * a
                    pos[1] = m[3][1] + (m[4][1] - m[3][1]) * a
            want = not sheet or any(abs(t - s) < 0.5 / FPS for s in stills) or t < 3.7
            if t < 40.0:
                if hold[0] <= t < hold[1]:
                    ch.js(hold[2])
                elif hold[1] <= t < hold[1] + 0.05:
                    ch.js("document.getElementById('link').textContent = 'Copy link'")
                ch.mouse("mouseMoved", pos[0], pos[1])
                if want:
                    ch.frame_done()
                    last_viz = ch.shot()
            viz = last_viz
            frame = viz.copy()
            draw_cursor(frame, pos[0] * DSF, pos[1] * DSF, ripples, t)
            for k_, (s0, s1, text, spec) in enumerate(steps):
                if s0 <= t < s1:
                    draw_caption(frame, text, t, s0, s1, anchor_for(k_, spec), k_ + 1, len(steps))
            if t < 4.0:                            # crossfade from the intro card
                frame = Image.blend(cards["intro"], frame, ease((t - 3.6) / 0.4))
            if t >= 40.0:                          # crossfade to the logo card
                frame = Image.blend(frame, cards["outro"], ease((t - 40.0) / 0.8))
        elif t < 44.5:
            frame = cards["outro"]
        else:                                      # minimal ending: fade to black
            frame = Image.blend(cards["outro"], Image.new("RGB", (W, H), "black"), ease((t - 44.5) / 1.4))
        for st in stills:
            if stills[st] is None and abs(t - st) < 0.5 / FPS:
                stills[st] = frame.copy()
                frame.save(BUILD / f"still-{st:04.1f}.png")
        if ff:
            ff.stdin.write(frame.tobytes())
        if f % 150 == 0:
            print(f"  t={t:5.1f}s  frame {f}/{nframes}  {time.time() - t_start:5.0f}s elapsed", flush=True)
    ch.close()
    if ff:
        ff.stdin.close()
        ff.wait()
        print("wrote", OUT)
    th = [im.resize((640, 360)) for im in stills.values() if im is not None]
    sheet_im = Image.new("RGB", (640 * 4, 360 * ((len(th) + 3) // 4)), "black")
    for i, im in enumerate(th):
        sheet_im.paste(im, ((i % 4) * 640, (i // 4) * 360))
    sheet_im.save(BUILD / "contact-sheet.png")
    print("wrote", BUILD / "contact-sheet.png")


if __name__ == "__main__":
    main()
