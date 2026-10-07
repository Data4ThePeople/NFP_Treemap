"""Charts and numbers for the post september-2026-jobs-report.

Writes PNGs to posts/september-2026-jobs-report/images/ in the dark house palette, and the numbers
behind each chart to posts/september-2026-jobs-report/numbers/*.csv for the tie-out. Inputs:
  - data/ces_observations.parquet (CES, current vintage, refreshed 2026-10-02)
  - QCEW 2025 annual averages, U.S. totals, fetched from data.bls.gov/cew/data/api/2025/a/industry/
  - dist/index.html (the explorer) for the two screenshots, in its dark theme

  PYTHONPATH=src .venv/bin/python tools/september_2026_charts.py
"""
from __future__ import annotations

# Contact address for the User-Agent: read at run time, never hardcoded in the repo.
# Set D4TP_CONTACT_EMAIL in the environment or in ~/.claude/d4tp-process/.env.
import os as _os


def _d4tp_contact():
    v = _os.environ.get("D4TP_CONTACT_EMAIL")
    if v:
        return v
    try:
        with open(_os.path.expanduser("~/.claude/d4tp-process/.env"), encoding="utf-8") as fh:
            for line in fh:
                if line.strip().startswith("D4TP_CONTACT_EMAIL="):
                    return line.split("=", 1)[1].strip().strip("'\"")
    except OSError:
        pass
    return ""


D4TP_CONTACT = _d4tp_contact()


import base64
import io
import sys
import time
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd
import requests

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "video"))
POST = ROOT / "posts" / "september-2026-jobs-report"
OUT, NUM = POST / "images", POST / "numbers"
QCEW_URL = "https://data.bls.gov/cew/data/api/2025/a/industry/{}.csv"
UA = {"User-Agent": f"Mozilla/5.0 (Macintosh) Data4ThePeople research {D4TP_CONTACT}"}
BG, INK, MUTED, GRID = "#181A1B", "#BBBDC0", "#8C9094", "#2A2E31"
CORAL, BLUE = "#f37952", "#5598e7"
CI = 122.0          # BLS: 90% confidence interval on the monthly change in total nonfarm, +/- 122,000
CES_SOURCE = "Data 4 The People  ·  Source: BLS Current Employment Statistics, seasonally adjusted, as of October 2, 2026"

plt.rcParams.update({"text.parse_math": False, "font.family": "DejaVu Sans", "axes.facecolor": BG,
                     "figure.facecolor": BG, "text.color": INK, "axes.labelcolor": INK, "xtick.color": INK,
                     "ytick.color": INK, "axes.edgecolor": GRID})


def fig(title, sub, h=7.5, legend=None):
    """Title, subtitle and an optional legend row of colored words (same as the child poverty takeaways)."""
    f = plt.figure(figsize=(12, h), dpi=150)
    px = 1 / (h * 150)
    f.text(0.04, 1 - 22 * px, title, fontsize=20, fontweight="bold", va="top")
    y = 1 - 75 * px
    for line in sub.split("\n"):
        f.text(0.04, y, line, fontsize=12.5, color=MUTED, va="top")
        y -= 30 * px
    if legend:
        y -= 8 * px
        x = 0.04
        r = f.canvas.get_renderer()
        for word, color in legend:
            t = f.text(x, y, word, fontsize=12, fontweight="bold", color=color, va="top")
            x += t.get_window_extent(renderer=r).width / f.bbox.width + 0.025
        y -= 30 * px
    return f, y - 22 * px


def finish(f, ax, name, source):
    for s in ("top", "right", "left"):
        ax.spines[s].set_visible(False)
    ax.tick_params(length=0)
    f.text(0.04, 0.02, source, fontsize=10, color=MUTED)
    f.savefig(OUT / name, facecolor=BG)
    plt.close(f)
    print("wrote", name)


def ces():
    d = pd.read_parquet(ROOT / "data" / "ces_observations.parquet")
    return d.pivot(index="date", columns="industry_code", values="employees")


def qcew(naics, own="5"):
    """2025 annual average pay, total wages and jobs, U.S. total, for one ownership code."""
    r = requests.get(QCEW_URL.format(naics), headers=UA, timeout=60)
    r.raise_for_status()
    d = pd.read_csv(io.StringIO(r.text), dtype=str)
    row = d[(d.area_fips == "US000") & (d.own_code == own)].iloc[0]
    return {"naics": naics, "own_code": own, "avg_annual_pay": int(row.avg_annual_pay),
            "total_annual_wages": int(row.total_annual_wages), "jobs": int(row.annual_avg_emplvl)}


# 1. The margin of error on the last 12 months
def c1_table(w):
    s = w["00000000"].diff().loc["2025-10-01":"2026-09-01"]
    t = pd.DataFrame({"month": s.index.strftime("%Y-%m"), "change": s.values,
                      "low": s.values - CI, "high": s.values + CI})
    t["range_includes_zero"] = (t.low < 0) & (t.high > 0)
    t["range_all_gains"] = t.low > 0
    t.to_csv(NUM / "01-margin-of-error.csv", index=False)
    return t


def mix(a, b, k):
    """Blend two hex colors; k=0 gives a, k=1 gives b."""
    a, b = matplotlib.colors.to_rgb(a), matplotlib.colors.to_rgb(b)
    return tuple(x + (y - x) * k for x, y in zip(a, b))


def c1_draw(t, grow=1.0, color=1.0, dpi=150):
    """The chart at one moment: bars `grow` of the way out from each dot, colors `color` of the way
    from neutral gray to blue/orange. grow=1, color=1 is the finished chart."""
    n_gain = int(t.range_all_gains.sum())
    f, top = fig(f"Only {n_gain} of the last 12 months clearly added jobs",
                 "Monthly change in U.S. nonfarm payroll jobs, with the BLS 90% range of plus or minus 122,000.\n"
                 "Current estimates for October 2025 to September 2026; September is the first estimate.",
                 legend=[("Range is all gains", BLUE), ("Range includes losses", CORAL)])
    f.set_dpi(dpi)
    ax = f.add_axes([0.08, 0.13, 0.88, top - 0.13])
    x = np.arange(len(t))
    half = CI * grow
    for i, r in t.iterrows():
        c = mix(MUTED, BLUE if r.range_all_gains else CORAL, color)
        if half > 0:
            ax.vlines(i, r.change - half, r.change + half, color=c, lw=6, alpha=0.35, zorder=1)
        ax.scatter(i, r.change, s=120, color=c, zorder=3)
        if r.change >= 0:
            ax.text(i, r.change + max(half, 18) + 12, f"{r.change:+,.0f}k", ha="center", va="bottom", fontsize=10.5, color=INK)
        else:
            ax.text(i, r.change - max(half, 18) - 12, f"{r.change:+,.0f}k", ha="center", va="top", fontsize=10.5, color=INK)
    ax.axhline(0, color=MUTED, lw=1)
    ax.set_xticks(x)
    ax.set_xticklabels(pd.to_datetime(t.month).dt.strftime("%b\n%Y"), fontsize=10.5)
    ax.set_ylim(-340, 400)
    ax.set_yticks([-300, -200, -100, 0, 100, 200, 300])
    ax.set_yticklabels(["-300k", "-200k", "-100k", "0", "+100k", "+200k", "+300k"])
    ax.grid(axis="y", color=GRID)
    for sp in ("top", "right", "left", "bottom"):
        ax.spines[sp].set_visible(False)
    ax.tick_params(length=0)
    f.text(0.04, 0.02, CES_SOURCE + "; margin of error from the BLS technical note", fontsize=10, color=MUTED)
    return f


def c1(w):
    t = c1_table(w)
    f = c1_draw(t)
    f.savefig(OUT / "01-margin-of-error.png", facecolor=BG)
    plt.close(f)
    print("wrote 01-margin-of-error.png")
    c1_gif(t)
    return t


def c1_gif(t, dpi=100):
    """Animated version: the monthly estimates alone, then the margin of error grows out of each
    dot, the colors resolve, it holds, and it loops."""
    from PIL import Image

    def frame(grow, color):
        f = c1_draw(t, grow, color, dpi=dpi)
        f.canvas.draw()
        im = Image.frombuffer("RGBA", f.canvas.get_width_height(), f.canvas.buffer_rgba()).convert("RGB")
        plt.close(f)
        return im

    ease = lambda a: a * a * (3 - 2 * a)
    frames, ms = [frame(0, 0)], [1400]                       # the point estimates alone
    for k in range(1, 31):                                   # bars grow out, 1.5 s
        frames.append(frame(ease(k / 30), 0)); ms.append(50)
    for k in range(1, 11):                                   # colors resolve, 0.5 s
        frames.append(frame(1, ease(k / 10))); ms.append(50)
    ms[-1] = 3500                                            # hold the finished chart, then loop
    pal = frames[-1].quantize(colors=128, method=Image.Quantize.MEDIANCUT)
    q = [im.quantize(palette=pal, dither=Image.Dither.NONE) for im in frames]
    q[0].save(OUT / "01-margin-of-error.gif", save_all=True, append_images=q[1:], duration=ms, loop=0,
              optimize=True, disposal=1)
    print("wrote 01-margin-of-error.gif", len(q), "frames")


# 3. What the two industries pay
def c3():
    food, local_ed, total = qcew("722"), qcew("611", own="3"), qcew("10", own="0")
    both_w = food["total_annual_wages"] + local_ed["total_annual_wages"]
    both_j = food["jobs"] + local_ed["jobs"]
    rest = {"avg_annual_pay": (total["total_annual_wages"] - both_w) / (total["jobs"] - both_j)}
    rows = [("All other industries", rest["avg_annual_pay"], BLUE),
            ("The two industries combined", both_w / both_j, CORAL),
            ("Local government, education", local_ed["avg_annual_pay"], CORAL),
            ("Food services and drinking places", food["avg_annual_pay"], CORAL)]
    pd.DataFrame([{"group": g, "avg_annual_pay": round(v)} for g, v, _ in rows]).to_csv(NUM / "03-pay.csv", index=False)
    f, top = fig("August's two biggest gainers pay about half what other jobs pay",
                 "Average annual pay per job in 2025. Food services and drinking places and local government education\n"
                 "added 83,100 of August's 133,000 jobs.",
                 legend=[("Led August's gains", CORAL), ("Everyone else", BLUE)], h=6.4)
    ax = f.add_axes([0.30, 0.13, 0.58, top - 0.13])
    y = np.arange(len(rows))[::-1]
    for yy, (g, v, c) in zip(y, rows):
        ax.barh(yy, v, height=0.62, color=c)
        ax.text(v + 1200, yy, f"${v:,.0f}", va="center", fontsize=12, fontweight="bold", color=INK)
    ax.set_yticks(y)
    ax.set_yticklabels([g for g, _, _ in rows], fontsize=12)
    ax.set_xlim(0, 100000)
    ax.set_xticks([0, 25000, 50000, 75000, 100000])
    ax.set_xticklabels(["$0", "$25k", "$50k", "$75k", "$100k"])
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_visible(False)
    finish(f, ax, "03-pay.png", "Data 4 The People  ·  Source: BLS Quarterly Census of Employment and Wages, 2025 annual averages")


# 5. Where three years of health care growth went, and what it pays
HC_ROWS = [  # CES code, QCEW NAICS, short name (non-overlapping industries)
    ("65624120", "624120", "Services for the elderly and persons with disabilities"),
    ("65622100", "6221", "General medical and surgical hospitals"),
    ("65621600", "6216", "Home health care services"),
    ("65621300", "6213", "Offices of other health practitioners"),
    ("65623100", "6231", "Skilled nursing care facilities"),
    ("65621100", "6211", "Offices of physicians"),
    ("65621400", "6214", "Outpatient care centers"),
    ("65623300", "6233", "Assisted living and retirement communities"),
]


def c5(w):
    a, b = pd.Timestamp("2023-08-01"), pd.Timestamp("2026-08-01")
    us = qcew("10", own="0")["avg_annual_pay"]
    rows = []
    for code, naics, name in HC_ROWS:
        q = qcew(naics)
        rows.append({"industry": name, "ces_code": code, "naics": naics,
                     "jobs_added_3yr_thousands": round(float(w.loc[b, code] - w.loc[a, code]), 1),
                     "avg_annual_pay_2025": q["avg_annual_pay"]})
    t = pd.DataFrame(rows).sort_values("jobs_added_3yr_thousands", ascending=False)
    t.to_csv(NUM / "05-health-care-growth-and-pay.csv", index=False)
    f, top = fig("Health care's biggest job gains are in some of its lowest-paying work",
                 "Jobs added, August 2023 to August 2026, in the largest health care and social assistance industries,\n"
                 f"with average annual pay per job in 2025. The U.S. average across all industries was ${us:,.0f}.",
                 legend=[(f"Pays below ${us:,.0f}", CORAL), (f"Pays above ${us:,.0f}", BLUE)], h=8.2)
    ax = f.add_axes([0.37, 0.10, 0.40, top - 0.10])
    y = np.arange(len(t))[::-1]
    for yy, r in zip(y, t.itertuples()):
        c = CORAL if r.avg_annual_pay_2025 < us else BLUE
        ax.barh(yy, r.jobs_added_3yr_thousands, height=0.62, color=c)
        ax.text(r.jobs_added_3yr_thousands + 8, yy, f"+{r.jobs_added_3yr_thousands * 1000:,.0f}",
                va="center", fontsize=11.5, fontweight="bold", color=INK)
        ax.text(960, yy, f"${r.avg_annual_pay_2025:,.0f}", va="center", ha="right", fontsize=11.5, color=INK, clip_on=False)
    ax.text(960, y[0] + 0.75, "Avg. pay, 2025", ha="right", fontsize=10.5, color=MUTED, clip_on=False)
    ax.set_yticks(y)
    ax.set_yticklabels(t.industry, fontsize=11)
    ax.set_xlim(0, 760)
    ax.set_xticks([0, 200, 400, 600])
    ax.set_xticklabels(["0", "200k", "400k", "600k"])
    ax.grid(axis="x", color=GRID)
    ax.set_axisbelow(True)
    ax.spines["bottom"].set_visible(False)
    finish(f, ax, "05-health-care-growth-and-pay.png",
           "Data 4 The People  ·  Sources: BLS Current Employment Statistics (seasonally adjusted, as of October 2, 2026); "
           "QCEW 2025, private")


# 2 and 4. The explorer itself, in its dark theme
def screenshots():
    from build_video import Chrome
    ch = Chrome(port=9356)
    try:
        for name, frag in (("02-explorer-august-level-4.png", "base=2026-08&lvl=4"),
                           ("04-explorer-three-years-level-3.png", "base=2026-08&h=3yr&lvl=3")):
            ch.cmd("Emulation.setDeviceMetricsOverride", width=1400, height=880, deviceScaleFactor=2, mobile=False)
            ch.cmd("Page.navigate", url="about:blank")     # a hash-only change would not reload the page
            time.sleep(0.5)
            ch.cmd("Page.navigate", url=f"file://{ROOT / 'dist' / 'index.html'}#embed=1&theme=dark&{frag}")
            for _ in range(120):
                time.sleep(0.25)
                try:
                    if ch.js("!!(window.__treemap && document.querySelector('.tile'))"):
                        break
                except Exception:
                    pass
            time.sleep(1.5)
            bottom = ch.js("document.querySelector('.legend-row').getBoundingClientRect().bottom") + 14
            d = ch.cmd("Page.captureScreenshot", format="png",
                       clip=dict(x=0, y=0, width=1400, height=min(880, bottom), scale=1))["data"]
            (OUT / name).write_bytes(base64.b64decode(d))
            print("wrote", name)
    finally:
        ch.close()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    NUM.mkdir(parents=True, exist_ok=True)
    w = ces()
    c1(w)
    c3()
    c5(w)
    screenshots()


if __name__ == "__main__":
    main()
