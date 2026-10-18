"""Tei OS sound theme — original synthesised event sounds (no samples)."""
import os
import subprocess
import sys
import wave

import numpy as np

SR = 44100


def note(freq, dur, amp=0.5, decay=3.0, partials=((1, 1.0), (2, 0.42), (3, 0.18), (4.17, 0.10), (5.4, 0.05)), attack=0.006):
    t = np.arange(int(SR * dur)) / SR
    sig = np.zeros_like(t)
    for mult, a in partials:
        sig += a * np.sin(2 * np.pi * freq * mult * t) * np.exp(-t * decay * (1 + 0.6 * (mult - 1)))
    env = np.minimum(1, t / attack)
    return amp * sig * env


def pad(freqs, dur, amp=0.18, fade_in=0.25):
    t = np.arange(int(SR * dur)) / SR
    sig = np.zeros_like(t)
    for f in freqs:
        for det in (-0.8, 0.8):
            sig += np.sin(2 * np.pi * (f + det) * t) + 0.3 * np.sin(2 * np.pi * 2 * (f + det) * t)
    env = np.minimum(1, t / fade_in) * np.exp(-t * 1.6)
    return amp * sig / (len(freqs) * 2) * env


def place(buf, sig, at):
    i = int(SR * at)
    end = min(len(buf), i + len(sig))
    buf[i:end] += sig[:end - i]


def reverb(x, mix=0.22):
    out = x.copy()
    for d, g in ((0.029, 0.5), (0.037, 0.45), (0.041, 0.4), (0.053, 0.35)):
        n = int(SR * d)
        y = np.zeros_like(x)
        for k in range(1, 6):
            if n * k < len(x):
                y[n * k:] += x[:-n * k] * (g ** k)
        out += y * mix / 2
    return out


def stereo(x, width_ms=0.7):
    n = int(SR * width_ms / 1000)
    left = x
    right = np.concatenate([np.zeros(n), x[:-n]]) if n else x
    return np.stack([left, right], axis=1)


def save(name, sig, out):
    sig = reverb(sig)
    peak = np.max(np.abs(sig)) or 1
    sig = sig / peak * 0.72
    fade = int(SR * 0.03)
    sig[-fade:] *= np.linspace(1, 0, fade)
    st = stereo(sig)
    wav = os.path.join(out, name + ".wav")
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((st * 32767).astype("<i2").tobytes())
    subprocess.run(["oggenc", "-Q", "-q", "4", "-o", os.path.join(out, name + ".oga"), wav], check=True)
    os.remove(wav)


def hz(n):  # MIDI note → Hz
    return 440.0 * 2 ** ((n - 69) / 12)


def build(out):
    os.makedirs(out, exist_ok=True)
    # login: rising G-major arpeggio over a soft pad
    b = np.zeros(int(SR * 3.0))
    for i, m in enumerate((67, 74, 79, 83)):
        place(b, note(hz(m), 2.4, 0.5 - i * 0.05, 2.2), 0.05 + i * 0.13)
    place(b, pad([hz(55), hz(62), hz(71)], 2.6), 0.0)
    place(b, note(hz(86), 1.6, 0.18, 2.6), 0.62)
    save("desktop-login", b, out)
    # logout: gentle descending figure
    b = np.zeros(int(SR * 2.0))
    for i, m in enumerate((83, 79, 74, 67)):
        place(b, note(hz(m), 1.6, 0.45, 3.0), i * 0.12)
    place(b, pad([hz(55), hz(62)], 1.6, 0.12), 0.1)
    save("desktop-logout", b, out)
    # notification / information
    b = np.zeros(int(SR * 1.0))
    place(b, note(hz(81), 0.9, 0.5, 5.0), 0)
    place(b, note(hz(88), 0.8, 0.4, 5.0), 0.09)
    save("dialog-information", b, out)
    save("message-new-instant", b.copy(), out)
    # question: rising
    b = np.zeros(int(SR * 0.9))
    place(b, note(hz(76), 0.7, 0.45, 6.0), 0)
    place(b, note(hz(83), 0.7, 0.45, 5.0), 0.11)
    save("dialog-question", b, out)
    # warning: two mid tones
    b = np.zeros(int(SR * 0.9))
    place(b, note(hz(69), 0.7, 0.55, 5.5), 0)
    place(b, note(hz(69), 0.7, 0.55, 5.5), 0.16)
    save("dialog-warning", b, out)
    # error: low falling pair
    b = np.zeros(int(SR * 1.0))
    place(b, note(hz(64), 0.8, 0.6, 5.0, ((1, 1), (2, 0.5), (3, 0.35), (4, 0.2))), 0)
    place(b, note(hz(57), 0.8, 0.6, 5.0, ((1, 1), (2, 0.5), (3, 0.35), (4, 0.2))), 0.13)
    save("dialog-error", b, out)
    # bell: short tick
    b = np.zeros(int(SR * 0.35))
    place(b, note(hz(93), 0.3, 0.4, 14.0), 0)
    save("bell", b, out)
    # complete: bright two-tone
    b = np.zeros(int(SR * 0.9))
    place(b, note(hz(79), 0.8, 0.45, 5.0), 0)
    place(b, note(hz(86), 0.8, 0.45, 4.5), 0.1)
    save("complete", b, out)
    # devices
    b = np.zeros(int(SR * 0.6))
    place(b, note(hz(72), 0.5, 0.45, 8.0), 0)
    place(b, note(hz(79), 0.5, 0.45, 7.0), 0.07)
    save("device-added", b, out)
    b = np.zeros(int(SR * 0.6))
    place(b, note(hz(79), 0.5, 0.45, 8.0), 0)
    place(b, note(hz(72), 0.5, 0.45, 7.0), 0.07)
    save("device-removed", b, out)
    save("power-plug", np.copy(np.zeros(1)) if False else b[::-1].copy() * 0 + b, out)
    b2 = np.zeros(int(SR * 0.6))
    place(b2, note(hz(67), 0.5, 0.45, 8.0), 0)
    save("power-unplug", b2, out)
    # battery low
    b = np.zeros(int(SR * 1.0))
    for i in range(2):
        place(b, note(hz(62), 0.4, 0.5, 7.0), i * 0.25)
    save("battery-low", b, out)
    # trash: filtered noise swish
    n = int(SR * 0.5)
    noise = np.random.RandomState(4).randn(n)
    k = np.exp(-np.linspace(0, 6, n)) * np.minimum(1, np.linspace(0, 12, n))
    kern = np.ones(40) / 40
    sw = np.convolve(noise, kern, mode="same") * k * 0.8
    save("trash-empty", sw, out)
    with open(os.path.join(out, "..", "index.theme"), "w") as fh:
        fh.write("[Sound Theme]\nName=Tei\nComment=Tei OS — original event sounds\nInherits=freedesktop\nDirectories=stereo\n\n[stereo]\nOutputProfile=stereo\n")
    print("sounds written to", out)


if __name__ == "__main__":
    build(sys.argv[1])
