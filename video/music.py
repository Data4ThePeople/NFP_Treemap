"""Original background track for the jobs explorer tutorial, synthesized in numpy (no samples, no licensing).

Built from the child poverty map's track (ChildPovertyDistrict/video/music.py) so the two tutorials
sound like a series: the same chill hop, swung boom-bap drums, warm sine bass, vinyl crackle, pads with
a long reverb, and the same arc and loudness. What tells them apart: 88 BPM against 84, D minor
(Dm9 - Bbmaj7 - Fmaj7 - Csus) against A minor, resolving to F(add9) at the logo, and a soft four-note
mallet phrase every other bar.

Pads alone under the intro card; the beat comes in with the treemap at 4 s and drops out at the logo
(40 s); the pads resolve and fade with the picture to black (44.5 to 46 s). Tour section about
-22 dBFS RMS. Writes video/build/music.wav (46 s, stereo)."""
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 46.0
OUT = Path(__file__).resolve().parent / "build" / "music.wav"
rng = np.random.default_rng(34)

BPM = 88
BEAT = 60 / BPM
BAR = 4 * BEAT
SWING = 0.58                       # share of the beat taken by the first 8th note
T_BEAT_IN, T_LOGO, T_FADE0, T_END = 4.0, 40.0, 44.5, 46.0
CHORDS = [  # pads, voiced low and open
    [50, 57, 60, 64, 65],   # Dm9: D A C E F
    [46, 53, 57, 62, 69],   # Bbmaj7
    [41, 48, 52, 57, 64],   # Fmaj7
    [48, 55, 60, 65, 67],   # Csus
]
ROOTS = [38, 34, 29, 36]            # bass: D2 Bb1 F1 C2
LOGO_CHORD = [41, 53, 60, 67, 69, 72]   # F(add9)
MOTIF = [(0, 77), (1, 76), (2, 72), (3, 74)]   # 8th-note slot from beat 3 -> F5 E5 C5 D5


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def onepole(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i, v in enumerate(x):
        acc = (1 - a) * v + a * acc
        y[i] = acc
    return y


def place(buf, start, sig):
    i = int(start * SR)
    j = min(len(buf), i + len(sig))
    if 0 <= i < len(buf):
        buf[i:j] += sig[: j - i]


def pad_voice(notes, length, level):
    n = int(length * SR)
    t = np.arange(n) / SR
    sig = np.zeros(n)
    for m in notes:
        for det in (-0.006, 0.0, 0.007):
            ph = (t * hz(m) * (1 + det) + rng.random()) % 1.0
            sig += (2 * np.abs(2 * ph - 1) - 1) * (0.7 if m < 50 else 0.45)
    env = np.minimum(1, t / 1.4) * np.minimum(1, np.maximum(0, (length - t) / 2.0))
    return sig * env * level / len(notes)


def mallet(note, length=0.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(note)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.03)
    return sig * np.minimum(1, t / 0.002) * np.exp(-t / 0.22)


def reverb(x, seconds=3.6, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = onepole(r.standard_normal(n) * np.exp(-t * 6.9 / seconds), 2500)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]


def kick():
    m = int(0.35 * SR)
    t = np.arange(m) / SR
    f = 48 + 60 * np.exp(-t / 0.035)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.16) * np.minimum(1, t / 0.003)
    return np.tanh(1.6 * s)


def snare():
    m = int(0.28 * SR)
    t = np.arange(m) / SR
    tone = np.sin(2 * np.pi * 185 * t) * np.exp(-t / 0.05)
    nz = rng.standard_normal(m)
    nz = onepole(nz, 5000) - onepole(nz, 700)
    return (0.5 * tone + nz * 1.1) * np.exp(-t / 0.09) * np.minimum(1, t / 0.002)


def hat():
    m = int(0.06 * SR)
    t = np.arange(m) / SR
    nz = rng.standard_normal(m)
    nz = onepole(nz, 9000) - onepole(nz, 5500)
    return nz * np.exp(-t / 0.018)


def main():
    n = int(DUR * SR)
    t = np.arange(n) / SR

    # pads: one chord per bar, overlapping releases
    pads = np.zeros(n)
    k, start = 0, 0.0
    while start < T_LOGO - 0.5:
        place(pads, start, pad_voice(CHORDS[k % 4], BAR + 2.0, 1.0))
        start += BAR
        k += 1
    place(pads, T_LOGO - 0.8, pad_voice(LOGO_CHORD, T_END - (T_LOGO - 0.8), 0.8))
    pads = onepole(pads, 1300)

    air = rng.standard_normal(n)
    air = (onepole(air, 3200) - onepole(air, 250)) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 9.0) ** 2) * 0.035

    # drums and bass, bar-aligned from T_BEAT_IN
    drums, bass, lead = np.zeros(n), np.zeros(n), np.zeros(n)
    K, S, Hh = kick(), snare(), hat()

    def eighth(b, i):              # time of the i-th swung 8th note in bar b
        beat, half = divmod(i, 2)
        return T_BEAT_IN + b * BAR + beat * BEAT + (SWING * BEAT if half else 0.0)

    nbars = int(np.ceil((T_LOGO - T_BEAT_IN) / BAR))
    for b in range(nbars):
        for i in range(8):
            tt = eighth(b, i)
            if tt >= T_LOGO:
                break
            if i in (0, 5) or (i == 3 and b % 2 == 1):          # boom-bap kick pattern
                place(drums, tt, K * (0.85 if i == 0 else 0.6))
            if i in (2, 6):                                     # snare on 2 and 4
                place(drums, tt + 0.012, S * 0.32)              # a little late, laid back
            place(drums, tt, Hh * (0.10 if i % 2 == 0 else 0.065) * (0.85 + 0.3 * rng.random()))
        # bass: root on 1, a soft push on the "and" of 2, the fifth before the next bar
        root = ROOTS[(b + int(T_BEAT_IN / BAR)) % 4]
        for (i, note, ln) in ((0, root, 1.2), (3, root, 0.5), (6, root + 7, 0.6)):
            tt = eighth(b, i)
            if tt >= T_LOGO:
                continue
            m = int(ln * SR)
            x = np.arange(m) / SR
            bs = np.sin(2 * np.pi * hz(note + 12) * x) + 0.3 * np.sin(4 * np.pi * hz(note + 12) * x)
            place(bass, tt, bs * np.minimum(1, x / 0.01) * np.exp(-x / 0.5) * 0.22)
        # the phrase that sets this track apart: four soft mallet notes on beats 3 and 4, every other bar
        if b % 2 == 1:
            for (slot, note) in MOTIF:
                tt = eighth(b, 4 + slot)
                if tt < T_LOGO - 0.2:
                    place(lead, tt, mallet(note) * 0.12)
    drums = onepole(np.tanh(1.3 * drums), 7000)               # lo-fi: soft clip and darken

    # vinyl crackle: sparse clicks and faint hiss
    crackle = np.zeros(n)
    for _ in range(int(DUR * 14)):
        i = rng.integers(0, n - 50)
        crackle[i:i + 30] += rng.standard_normal(30) * np.exp(-np.arange(30) / 6) * rng.uniform(0.02, 0.09)
    crackle += onepole(rng.standard_normal(n), 6000) * 0.006

    beat_env = np.clip((t - T_BEAT_IN + 0.05) / 0.3, 0, 1) * np.clip((T_LOGO + 0.6 - t) / 0.6, 0, 1)
    dry = pads + air
    lead = (0.8 * lead + 0.4 * reverb(lead, 1.8, seed=7)) * np.clip((T_LOGO + 0.6 - t) / 0.6, 0, 1)
    left = 0.5 * dry + 0.7 * reverb(dry, seed=3) + (drums + bass) * beat_env + lead + crackle
    right = 0.5 * dry + 0.7 * reverb(dry, seed=5) + (drums + bass) * beat_env + lead + crackle

    arc = np.interp(t, [0, 3.0, 4.0, 38.0, 40.0, 41.2, T_FADE0, T_END],
                       [0.0, 0.6, 0.7, 0.8, 0.85, 1.0, 0.9, 0.0])
    left *= arc
    right *= arc

    mix = np.stack([left, right], axis=1)
    rms = np.sqrt((mix[int(4 * SR):int(40 * SR)] ** 2).mean())
    mix *= 10 ** (-22 / 20) / rms
    peak = np.abs(mix).max()
    if peak > 10 ** (-2 / 20):
        mix *= 10 ** (-2 / 20) / peak
    OUT.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(OUT), "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((mix * 32767).astype("<i2").tobytes())
    print("wrote", OUT)


if __name__ == "__main__":
    main()
