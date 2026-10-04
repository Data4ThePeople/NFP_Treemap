"""Original background track for the jobs explorer tutorial, synthesized in numpy (no samples, no licensing).

A sibling of the child poverty map's chill hop (ChildPovertyDistrict/video/music.py): same family, same
arc and loudness, so the two sit together on a channel, but a different piece. That one is 84 BPM,
swung, A minor, pads and vinyl. This one moves forward rather than sways: 92 BPM, nearly straight,
D major (Dmaj9 - Bm7 - Gmaj7 - A7sus), soft electric-piano chords on the off-beats, a four-note mallet
motif every two bars as its hook, a rim click instead of a snare, a quiet 16th-note shaker like a
ticker, and a slight tape wobble instead of vinyl crackle.

Pads alone under the intro card; the beat comes in with the treemap at 4 s and drops out at the logo
(40 s); the pads resolve to D(add9) and fade with the picture to black (44.5 to 46 s). Tour section
about -22 dBFS RMS. Writes video/build/music.wav (46 s, stereo)."""
import wave
from pathlib import Path

import numpy as np

SR = 44100
DUR = 46.0
OUT = Path(__file__).resolve().parent / "build" / "music.wav"
rng = np.random.default_rng(34)

BPM = 92
BEAT = 60 / BPM
BAR = 4 * BEAT
SWING = 0.53                       # share of the beat taken by the first 8th note: barely swung
T_BEAT_IN, T_LOGO, T_FADE0, T_END = 4.0, 40.0, 44.5, 46.0
CHORDS = [  # pads, voiced low and open
    [50, 57, 61, 64, 66],   # Dmaj9: D A C# E F#
    [47, 54, 57, 62, 66],   # Bm7: B F# A D F#
    [43, 50, 54, 59, 62],   # Gmaj7: G D F# B D
    [45, 52, 55, 59, 62],   # A7sus: A E G B D
]
EP = [  # electric piano, mid register
    [61, 64, 66, 69],       # C# E F# A
    [62, 66, 69, 71],       # D F# A B
    [59, 62, 66, 69],       # B D F# A
    [59, 62, 64, 67],       # B D E G
]
ROOTS = [38, 35, 31, 33]            # bass: D2 B1 G1 A1
MOTIF = [(0, 78), (1, 76), (2, 73), (3, 74)]   # 8th-note slot -> note: F#5 E5 C#5 D5, starting on beat 3
LOGO_CHORD = [38, 50, 57, 64, 66, 69]          # D(add9)


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


def wobble(n, start):
    """Tape wobble: a slow, slightly irregular pitch drift, as a phase multiplier."""
    t = (np.arange(n) + int(start * SR)) / SR
    return 1 + 0.0022 * np.sin(2 * np.pi * 0.55 * t) + 0.0011 * np.sin(2 * np.pi * 1.7 * t + 1.3)


def pad_voice(notes, length, level, start):
    n = int(length * SR)
    t = np.arange(n) / SR
    wob = wobble(n, start)
    sig = np.zeros(n)
    for m in notes:
        for det in (-0.005, 0.0, 0.006):
            ph = (np.cumsum(np.full(n, hz(m) * (1 + det))) * wob / SR + rng.random()) % 1.0
            sig += (2 * np.abs(2 * ph - 1) - 1) * (0.7 if m < 50 else 0.45)
    env = np.minimum(1, t / 1.4) * np.minimum(1, np.maximum(0, (length - t) / 2.0))
    return sig * env * level / len(notes)


def ep_chord(notes, length, start):
    """Rhodes-like: sine with a little bell partial, quick attack, soft decay, gentle tremolo."""
    n = int(length * SR)
    t = np.arange(n) / SR
    wob = wobble(n, start)
    sig = np.zeros(n)
    for m in notes:
        f = hz(m) * wob
        ph = 2 * np.pi * np.cumsum(f) / SR
        sig += np.sin(ph + 0.6 * np.sin(ph) * np.exp(-t / 0.08)) + 0.12 * np.sin(ph * 4.0) * np.exp(-t / 0.05)
    env = np.minimum(1, t / 0.004) * np.exp(-t / 0.55) * (1 + 0.12 * np.sin(2 * np.pi * 4.5 * t))
    return sig * env / len(notes)


def mallet(note, length=0.5):
    n = int(length * SR)
    t = np.arange(n) / SR
    f = hz(note)
    sig = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(2 * np.pi * f * 3.98 * t) * np.exp(-t / 0.03)
    return sig * np.minimum(1, t / 0.002) * np.exp(-t / 0.22)


def reverb(x, seconds=3.0, seed=3):
    r = np.random.default_rng(seed)
    n = int(seconds * SR)
    t = np.arange(n) / SR
    ir = onepole(r.standard_normal(n) * np.exp(-t * 6.9 / seconds), 2800)
    ir[: int(0.012 * SR)] = 0
    ir /= np.sqrt((ir ** 2).sum())
    m = len(x) + n
    return np.fft.irfft(np.fft.rfft(x, m) * np.fft.rfft(ir, m), m)[: len(x)]


def kick():
    m = int(0.32 * SR)
    t = np.arange(m) / SR
    f = 52 + 70 * np.exp(-t / 0.03)
    s = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13) * np.minimum(1, t / 0.003)
    return np.tanh(1.5 * s)


def rim():
    m = int(0.09 * SR)
    t = np.arange(m) / SR
    tone = np.sin(2 * np.pi * 820 * t) + 0.6 * np.sin(2 * np.pi * 1630 * t)
    nz = rng.standard_normal(m)
    nz = onepole(nz, 8000) - onepole(nz, 2000)
    return (0.8 * tone + 0.5 * nz) * np.exp(-t / 0.018) * np.minimum(1, t / 0.001)


def shaker():
    m = int(0.07 * SR)
    t = np.arange(m) / SR
    nz = rng.standard_normal(m)
    nz = onepole(nz, 11000) - onepole(nz, 6500)
    return nz * np.minimum(1, t / 0.012) * np.exp(-t / 0.025)


def main():
    n = int(DUR * SR)
    t = np.arange(n) / SR

    # pads: one chord per bar, overlapping releases
    pads = np.zeros(n)
    k, start = 0, 0.0
    while start < T_LOGO - 0.5:
        place(pads, start, pad_voice(CHORDS[k % 4], BAR + 2.0, 0.85, start))
        start += BAR
        k += 1
    place(pads, T_LOGO - 0.8, pad_voice(LOGO_CHORD, T_END - (T_LOGO - 0.8), 0.8, T_LOGO - 0.8))
    pads = onepole(pads, 1500)

    air = rng.standard_normal(n)
    air = (onepole(air, 3600) - onepole(air, 300)) * (0.5 + 0.5 * np.sin(2 * np.pi * t / 7.0) ** 2) * 0.025

    drums, bass, keys, lead = np.zeros(n), np.zeros(n), np.zeros(n), np.zeros(n)
    K, R, Sh = kick(), rim(), shaker()

    def eighth(b, i):              # time of the i-th lightly swung 8th note in bar b
        beat, half = divmod(i, 2)
        return T_BEAT_IN + b * BAR + beat * BEAT + (SWING * BEAT if half else 0.0)

    nbars = int(np.ceil((T_LOGO - T_BEAT_IN) / BAR))
    for b in range(nbars):
        chord = (b + int(T_BEAT_IN / BAR)) % 4
        for i in range(8):
            tt = eighth(b, i)
            if tt >= T_LOGO:
                break
            if i in (0, 3) or (i == 5 and b % 2 == 0):          # kick: 1, the "and" of 2, sometimes 3-and
                place(drums, tt, K * (0.8 if i == 0 else 0.55))
            if i in (2, 6):                                     # rim click on 2 and 4
                place(drums, tt + 0.006, R * 0.22)
            if i in (1, 5):                                     # electric piano on the off-beats of 1 and 3
                place(keys, tt, ep_chord(EP[chord], 0.9, tt) * (0.30 if i == 1 else 0.24))
        for s16 in range(16):                                   # shaker, straight 16ths, accents on the 8ths
            tt = T_BEAT_IN + b * BAR + s16 * BEAT / 4
            if tt < T_LOGO:
                place(drums, tt, Sh * (0.07 if s16 % 2 == 0 else 0.04) * (0.85 + 0.3 * rng.random()))
        # bass: root on 1, a pickup on the "and" of 2, the fifth on 3, an approach note into the next bar
        root = ROOTS[chord]
        nxt = ROOTS[(chord + 1) % 4]
        for (i, note, ln) in ((0, root, 0.9), (3, root, 0.35), (4, root + 7, 0.6), (7, nxt + (1 if nxt < root else -1), 0.3)):
            tt = eighth(b, i)
            if tt >= T_LOGO:
                continue
            m = int(ln * SR)
            x = np.arange(m) / SR
            bs = np.sin(2 * np.pi * hz(note + 12) * x) + 0.25 * np.sin(4 * np.pi * hz(note + 12) * x)
            place(bass, tt, bs * np.minimum(1, x / 0.01) * np.exp(-x / 0.45) * 0.22)
        # the hook: four mallet notes on beats 3 and 4 of every other bar
        if b % 2 == 1:
            for (slot, note) in MOTIF:
                tt = eighth(b, 4 + slot)
                if tt < T_LOGO - 0.2:
                    place(lead, tt, mallet(note) * 0.16)
    drums = onepole(np.tanh(1.3 * drums), 8000)

    # tape hiss, quieter and smoother than vinyl
    hiss = onepole(rng.standard_normal(n), 7000) * 0.004

    beat_env = np.clip((t - T_BEAT_IN + 0.05) / 0.3, 0, 1) * np.clip((T_LOGO + 0.6 - t) / 0.6, 0, 1)
    dry = pads + air
    wet_keys = keys + lead
    left = (0.5 * dry + 0.7 * reverb(dry, seed=3) + (drums + bass) * beat_env
            + (0.8 * wet_keys + 0.35 * reverb(wet_keys, 1.8, seed=7)) * beat_env + hiss)
    right = (0.5 * dry + 0.7 * reverb(dry, seed=5) + (drums + bass) * beat_env
             + (0.8 * wet_keys + 0.35 * reverb(wet_keys, 1.8, seed=9)) * beat_env + hiss)

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
