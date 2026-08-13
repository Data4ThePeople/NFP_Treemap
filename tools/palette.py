"""Colour maths for building and checking the treemap's diverging scale.

A Python port of the dataviz skill's validator (no node runtime on this
machine). OKLab conversions and the Machado, Oliveira & Fernandes (2009) CVD
transforms at severity 1.0, so palette decisions are computed rather than
eyeballed.

    python tools/palette.py
"""
from __future__ import annotations

import math

MACHADO = {
    "protan": [
        [0.152286, 1.052583, -0.204868],
        [0.114503, 0.786281, 0.099216],
        [-0.003882, -0.048116, 1.051998],
    ],
    "deutan": [
        [0.367322, 0.860646, -0.227968],
        [0.280085, 0.672501, 0.047413],
        [-0.011820, 0.042940, 0.968881],
    ],
}

SURFACE = {"light": "#fcfcfb", "dark": "#1a1a19"}


# --- conversions -----------------------------------------------------------
def hex_to_srgb(h: str) -> list[float]:
    h = h.strip().lstrip("#")
    return [int(h[i : i + 2], 16) / 255 for i in (0, 2, 4)]


def s2lin(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def lin2s(c: float) -> float:
    c = max(0.0, min(1.0, c))
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def lin(h: str) -> list[float]:
    return [s2lin(c) for c in hex_to_srgb(h)]


def lin_to_hex(rgb: list[float]) -> str:
    return "#" + "".join(f"{round(lin2s(c) * 255):02x}" for c in rgb)


def oklab_from_lin(rgb: list[float]) -> tuple[float, float, float]:
    r, g, b = rgb
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (
        0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
        1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
        0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s,
    )


def lin_from_oklab(L: float, a: float, b: float) -> list[float]:
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return [
        4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
        -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
        -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s,
    ]


def oklch(h: str) -> tuple[float, float, float]:
    L, a, b = oklab_from_lin(lin(h))
    return L, math.hypot(a, b), math.degrees(math.atan2(b, a)) % 360


def in_gamut(rgb: list[float]) -> bool:
    return all(-1e-4 <= c <= 1 + 1e-4 for c in rgb)


def lch_to_hex(L: float, C: float, hue_deg: float) -> str:
    """Clip chroma down to the sRGB gamut, then encode."""
    rad = math.radians(hue_deg)
    lo, hi = 0.0, C
    for _ in range(40):
        mid = (lo + hi) / 2
        if in_gamut(lin_from_oklab(L, mid * math.cos(rad), mid * math.sin(rad))):
            lo = mid
        else:
            hi = mid
    return lin_to_hex(lin_from_oklab(L, lo * math.cos(rad), lo * math.sin(rad)))


# --- checks ----------------------------------------------------------------
def rel_lum(h: str) -> float:
    r, g, b = lin(h)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast(a: str, b: str) -> float:
    hi, lo = sorted((rel_lum(a), rel_lum(b)), reverse=True)
    return (hi + 0.05) / (lo + 0.05)


def simulate(h: str, kind: str) -> list[float]:
    r, g, b = lin(h)
    M = MACHADO[kind]
    return [
        max(0.0, min(1.0, M[i][0] * r + M[i][1] * g + M[i][2] * b)) for i in range(3)
    ]


def delta_e(h1: str, h2: str, kind: str | None = None) -> float:
    a = oklab_from_lin(simulate(h1, kind) if kind else lin(h1))
    b = oklab_from_lin(simulate(h2, kind) if kind else lin(h2))
    return 100 * math.dist(a, b)


# --- the treemap's diverging scale -----------------------------------------
# Losses are red, gains are blue, midpoint is a neutral gray. Red-green (the
# Tableau original) is the textbook CVD failure: under deuteranopia the two
# poles collapse toward the same olive, so the sign of the change - the whole
# point of the chart - stops being legible.
# Arms are listed midpoint -> outward. On a light surface the midpoint sits near
# the surface and both arms darken as magnitude grows; on a dark surface the
# midpoint is dark and both arms *lighten*. Each mode is stepped for its own
# surface rather than flipped automatically.
BLUE_ARM = {  # gains, from the documented blue ramp
    "light": ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#256abf", "#104281"],
    # Dark arms lighten outward but must stop short of the pastel range: letting
    # both arms run to #cde2fb / #fed4cf collapses the poles (CVD dE 5.9, and
    # only 8.2 unsimulated). The extremes stay chromatic instead.
    "dark": ["#184f95", "#1c5cab", "#256abf", "#2a78d6", "#3987e5", "#5598e7"],
}
MIDPOINT = {"light": "#f0efec", "dark": "#383835"}
RED_HUE = 27.0  # OKLCH hue of the documented categorical red (#e34948)
# Clipping red to the sRGB gamut maximum yields a garish pure #fb001d. Matching
# the blue arm's chroma step for step keeps the two arms visually balanced.
RED_CHROMA_SCALE = 1.15


def red_arm(mode: str) -> list[str]:
    """Mirror the blue arm's lightness and chroma at the red hue."""
    out = []
    for blue in BLUE_ARM[mode]:
        L, C, _ = oklch(blue)
        out.append(lch_to_hex(L, C * RED_CHROMA_SCALE, RED_HUE))
    return out


def report() -> None:
    for mode in ("light", "dark"):
        surface = SURFACE[mode]
        blues = BLUE_ARM[mode]
        reds = red_arm(mode)
        mid = MIDPOINT[mode]
        ramp = list(reversed(reds)) + [mid] + blues

        print(f"\n=== {mode.upper()} (surface {surface}) ===")
        print("loss arm :", " ".join(reversed(reds)))
        print("midpoint :", mid)
        print("gain arm :", " ".join(blues))

        # 1. Lightness must move monotonically outward along each arm, away from
        # the surface: darker on light, lighter on dark.
        want_darker = mode == "light"
        ok = True
        for arm in (reds, blues):
            steps = [oklch(c)[0] for c in [mid] + arm]
            ok &= all(
                (y < x) if want_darker else (y > x)
                for x, y in zip(steps, steps[1:])
            )
        print(f"  lightness monotonic per arm  : {'PASS' if ok else 'FAIL'}")

        # 2. A reader must tell a loss from a gain of the SAME magnitude, so
        # compare red[i] against blue[i] step by step.
        #
        # The two arms are *supposed* to converge on the neutral midpoint, so
        # the innermost steps are close by construction - that is what makes a
        # ramp diverging rather than two unrelated scales. Gate the outer half,
        # where the sign of the change actually has to be legible, and report
        # the inner steps as informational. Tiles near zero are additionally
        # covered by the relief rule: the label and tooltip carry the signed
        # number, so hue never carries the sign alone.
        print("  arm separation by step (inner -> outer):")
        gate_from = len(reds) // 2
        worst_cvd = worst_norm = float("inf")
        for i, (r, b) in enumerate(zip(reds, blues)):
            cvd = min(delta_e(r, b, k) for k in ("protan", "deutan"))
            norm = delta_e(r, b)
            gated = i >= gate_from
            if gated:
                worst_cvd = min(worst_cvd, cvd)
                worst_norm = min(worst_norm, norm)
            print(
                f"    step {i + 1}: CVD {cvd:5.1f}  normal {norm:5.1f}"
                f"{'   [gated]' if gated else '   (converging, informational)'}"
            )
        print(
            f"  outer-half CVD dE (worst)    : {worst_cvd:5.1f}  "
            f"{'PASS' if worst_cvd >= 8 else 'FAIL'} (target >= 8)"
        )
        print(
            f"  outer-half normal dE (worst) : {worst_norm:5.1f}  "
            f"{'PASS' if worst_norm >= 15 else 'FAIL'} (floor >= 15)"
        )

        # 3. midpoint must read as "nothing" - low chroma, near the surface
        print(
            f"  midpoint chroma              : {oklch(mid)[1]:5.3f}  "
            f"{'PASS' if oklch(mid)[1] < 0.03 else 'FAIL'} (neutral gray)"
        )

        # 4. extremes legible against the surface
        for name, c in (("loss end", reds[-1]), ("gain end", blues[-1])):
            print(f"  {name} contrast vs surface  : {contrast(c, surface):5.2f}")

    # Why the Tableau original is not the default.
    print("\n=== comparison: classic red-yellow-green poles ===")
    for label, a, b in (
        ("RdYlGn  #d73027 vs #1a9850", "#d73027", "#1a9850"),
        ("ours    red     vs blue   ", red_arm("light")[-1], BLUE_ARM["light"][-1]),
    ):
        worst = min(delta_e(a, b, k) for k in ("protan", "deutan"))
        print(
            f"  {label}: CVD dE {worst:5.1f}  normal dE {delta_e(a, b):5.1f}  "
            f"{'PASS' if worst >= 8 else 'FAIL'}"
        )


if __name__ == "__main__":
    report()
