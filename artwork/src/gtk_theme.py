"""Build the Tei GTK theme.

Base: Greybird (GPL-2+/CC-BY-SA-3.0, Shimmer Project) recoloured to the Tei palette,
plus Tei's own overrides (tei.css) for buttons, panel, start menu, tooltips etc.
"""
import colorsys
import os
import re
import shutil
import sys

import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa

# Lightness tone curve for neutral greys (Greybird is darker than the airy Tei look).
GREY_CURVE = [(0.0, 0.0), (0.24, 0.12), (0.30, 0.22), (0.51, 0.63), (0.58, 0.69), (0.66, 0.76),
              (0.75, 0.86), (0.81, 0.935), (0.86, 0.955), (0.90, 0.968), (0.95, 0.985), (0.99, 1.0), (1.0, 1.0)]
TEAL_HUE = 186 / 360.0


def remap(r, g, b):
    """Map an sRGB colour (0-255) from Greybird's palette to Tei's."""
    h, l, s = colorsys.rgb_to_hls(r / 255, g / 255, b / 255)
    if s < 0.12 or l > 0.97:  # neutral grey → tone curve + slight cool tint
        xs, ys = zip(*GREY_CURVE)
        nl = float(np.interp(l, xs, ys))
        nr, ng, nb = colorsys.hls_to_rgb(TEAL_HUE, nl, 0.045 if 0.2 < nl < 0.96 else 0.02)
        return nr * 255, ng * 255, nb * 255
    deg = h * 360
    if 195 <= deg <= 235:  # Greybird blues → Tei teal (selection #398ee7 → #2A8F9A)
        # anchor: Greybird selection L≈0.565 → Tei teal L≈0.363
        nl = max(0.05, min(0.95, 0.363 + (l - 0.565) * 1.05))
        ns = min(1.0, s * 0.72)
        nr, ng, nb = colorsys.hls_to_rgb(TEAL_HUE, nl, ns)
        return nr * 255, ng * 255, nb * 255
    return r, g, b  # keep semantic colours (red/green/orange)


def recolor_css(text):
    def hexrep(m):
        hx = m.group(0)[1:]
        if len(hx) == 3:
            hx = ''.join(c * 2 for c in hx)
        r, g, b = (int(hx[i:i + 2], 16) for i in (0, 2, 4))
        return rgb2hex(remap(r, g, b)).lower()

    def rgbarep(m):
        r, g, b = (float(m.group(i)) for i in (1, 2, 3))
        nr, ng, nb = remap(r, g, b)
        return f"rgba({int(round(nr))}, {int(round(ng))}, {int(round(nb))}, {m.group(4)})"

    text = re.sub(r'#[0-9a-fA-F]{6}\b|#[0-9a-fA-F]{3}\b', hexrep, text)
    text = re.sub(r'rgba\(\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*\)', rgbarep, text)
    return text


def recolor_png(path):
    im = Image.open(path).convert("RGBA")
    a = np.asarray(im, dtype=np.float32)
    out = a.copy()
    flat = a.reshape(-1, 4)
    res = out.reshape(-1, 4)
    for i in range(flat.shape[0]):
        if flat[i, 3] == 0:
            continue
        res[i, :3] = remap(*flat[i, :3])
    Image.fromarray(np.clip(out, 0, 255).astype(np.uint8), "RGBA").save(path)


def build(greybird_dir, out_dir, overrides_css):
    if os.path.exists(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    for sub in ("gtk-3.0", "gtk-2.0", "xfce-notify-4.0", "gtk-4.0"):
        src = os.path.join(greybird_dir, sub)
        if os.path.isdir(src):
            shutil.copytree(src, os.path.join(out_dir, sub), symlinks=True)
    for root, _, files in os.walk(out_dir):
        for f in files:
            p = os.path.join(root, f)
            if os.path.islink(p):
                continue
            if f.endswith((".css", "gtkrc", ".svg", ".rc")):
                t = open(p, encoding="utf-8", errors="surrogateescape").read()
                open(p, "w", encoding="utf-8", errors="surrogateescape").write(recolor_css(t))
            elif f.endswith(".png"):
                recolor_png(p)
    # Tei overrides appended to the recoloured base
    ov = open(overrides_css, encoding="utf-8").read()
    for css in ("gtk-3.0/gtk.css",):
        p = os.path.join(out_dir, css)
        with open(p, "a", encoding="utf-8") as fh:
            fh.write("\n\n/* ===================== Tei OS overrides ===================== */\n")
            fh.write(ov)
    # gtk-dark.css: keep recoloured dark variant (used only by apps that request it)
    with open(os.path.join(out_dir, "index.theme"), "w") as fh:
        fh.write("""[Desktop Entry]
Type=X-GNOME-Metatheme
Name=Tei
Comment=Tei OS — classic, friendly theme (teal & honey)
Encoding=UTF-8

[X-GNOME-Metatheme]
GtkTheme=Tei
MetacityTheme=Tei
IconTheme=Tei
CursorTheme=DMZ-White
ButtonLayout=menu:minimize,maximize,close
""")
    with open(os.path.join(out_dir, "LICENSE-Tei.txt"), "w") as fh:
        fh.write("Tei GTK theme: derived from Greybird (Shimmer Project), GPL-2.0-or-later / CC-BY-SA-3.0.\n"
                 "Recoloured and extended for Tei OS. Window-border (xfwm4) artwork is original.\n")
    print("GTK theme written to", out_dir)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2], sys.argv[3])
