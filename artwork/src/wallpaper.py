"""WinLow XP wallpapers — procedurally generated, original artwork (no photos)."""
import io
import math
import os
import random
import subprocess
import sys

import numpy as np
from PIL import Image, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa
from logo import LEAF_PATH, STEM  # noqa


def rgb(h):
    return np.array(hex2rgb(h), dtype=np.float32)


def leaf_sprite(px, color="#FFFFFF", veins=True):
    """Rasterise a leaf silhouette (optionally with veins cut out) to RGBA."""
    from logo import VEINS, MIDRIB
    v = ""
    if veins:
        v = "".join(f'<path d="{d}" fill="none" stroke="#000" stroke-width="4" stroke-linecap="round"/>' for d in VEINS + [MIDRIB])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{px}" height="{px}" viewBox="0 0 256 256">
      <defs><mask id="m"><rect width="256" height="256" fill="#fff"/>{v}</mask></defs>
      <g mask="url(#m)"><path d="{STEM}" fill="none" stroke="{color}" stroke-width="8" stroke-linecap="round"/>
      <path d="{LEAF_PATH}" fill="{color}"/></g></svg>'''
    png = subprocess.run(["rsvg-convert"], input=svg.encode(), capture_output=True, check=True).stdout
    return Image.open(io.BytesIO(png)).convert("RGBA")


def blend_layer(base, layer):
    """Alpha-composite an RGBA PIL layer onto a float32 HxWx3 array."""
    arr = np.asarray(layer, dtype=np.float32) / 255.0
    a = arr[..., 3:4]
    return base * (1 - a) + arr[..., :3] * 255.0 * a


def gradient_base(w, h, c_bl, c_tr, glow_xy, glow_col, glow_r, glow_k):
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    t = np.clip((x / w) * 0.62 + (1 - y / h) * 0.38, 0, 1)
    t = t * t * (3 - 2 * t)
    img = rgb(c_bl)[None, None, :] * (1 - t[..., None]) + rgb(c_tr)[None, None, :] * t[..., None]
    gx, gy = glow_xy
    d = np.sqrt(((x - gx * w) / w) ** 2 + ((y - gy * h) / w) ** 2)
    g = np.exp(-(d / glow_r) ** 2)[..., None] * glow_k
    img = img * (1 - g) + rgb(glow_col)[None, None, :] * g
    return img


def screen(img, color, k):
    """Screen-blend a colour with per-pixel strength k (HxWx1) — brightens without greying."""
    c = rgb(color)[None, None, :] / 255.0
    return 255.0 - (255.0 - img) * (1.0 - c * k)


def ribbons(w, h, specs):
    """Silky light ribbons: list of (y0, amp, freq, phase, slope, width, alpha, col_left, col_right)."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    xn, yn = x / w, y / h
    out = []
    for (y0, amp, freq, ph, slope, width, alpha, cl, cr) in specs:
        yc = y0 + amp * np.sin(freq * xn * 2 * np.pi + ph) + slope * xn
        d = (yn - yc) / width
        core = np.exp(-d * d)
        edge = np.exp(-((d - 0.55) / 0.18) ** 2) * 0.55  # bright glossy edge
        k = np.clip((core * 0.55 + edge) * alpha, 0, 1)[..., None]
        t = xn[..., None]
        col = rgb(cl)[None, None, :] * (1 - t) + rgb(cr)[None, None, :] * t
        out.append((k, col))
    return out


def rays(w, h, origin, color, n, seed, strength):
    rnd = random.Random(seed)
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    ox, oy = origin[0] * w, origin[1] * h
    ang = np.arctan2(y - oy, x - ox)
    dist = np.sqrt((x - ox) ** 2 + (y - oy) ** 2) / w
    acc = np.zeros((h, w), np.float32)
    for _ in range(n):
        a0 = rnd.uniform(math.radians(100), math.radians(175))
        width = rnd.uniform(0.010, 0.035)
        acc += np.exp(-((ang - a0) / width) ** 2) * rnd.uniform(0.4, 1.0)
    acc *= np.exp(-dist * 1.6) * strength
    return np.clip(acc, 0, 1)[..., None] * rgb(color)[None, None, :], np.clip(acc, 0, 1)[..., None]


def bokeh(w, h, center, spread, count, colors, seed, rmin, rmax, amin, amax, blur):
    rnd = random.Random(seed)
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    from PIL import ImageDraw
    d = ImageDraw.Draw(layer)
    for _ in range(count):
        cx = rnd.gauss(center[0], spread[0]) * w
        cy = rnd.gauss(center[1], spread[1]) * h
        r = rnd.uniform(rmin, rmax) * w
        c = hex2rgb(rnd.choice(colors))
        a = int(255 * rnd.uniform(amin, amax))
        d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=c + (a,))
        # slightly brighter rim like a real lens highlight
        d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=c + (min(255, a + 30),), width=max(1, int(r * 0.06)))
    return layer.filter(ImageFilter.GaussianBlur(blur))


def leaves_layer(w, h, specs, color):
    layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    for (cx, cy, size, rot, alpha, blur) in specs:
        px = int(size * w)
        spr = leaf_sprite(px, color)
        spr = spr.rotate(rot, resample=Image.BICUBIC, expand=True)
        a = np.asarray(spr, dtype=np.float32)
        a[..., 3] *= alpha
        spr = Image.fromarray(a.astype(np.uint8), "RGBA")
        if blur:
            spr = spr.filter(ImageFilter.GaussianBlur(blur * w / 3840))
        layer.alpha_composite(spr, (int(cx * w - spr.width / 2), int(cy * h - spr.height / 2)))
    return layer


def finish(img, seed=1, vignette=0.28):
    h, w = img.shape[:2]
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    d = np.sqrt(((x - w / 2) / (w / 2)) ** 2 + ((y - h / 2) / (h / 2)) ** 2)
    img = img * (1 - vignette * np.clip(d - 0.55, 0, 1)[..., None] ** 1.5)
    rs = np.random.RandomState(seed)
    img = img + rs.uniform(-1.6, 1.6, img.shape).astype(np.float32)  # dither against banding
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8), "RGB")


def wp_tei(w, h):
    """Default wallpaper: dark charcoal with an ember-orange glow and silky light ribbons."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    img = gradient_base(w, h, "#0A0908", "#3A1B05", (0.82, 0.12), "#FFFFFF", 0.4, 0.0)
    d = np.sqrt(((x / w - 0.80) ** 2) + ((y / h - 0.12) * h / w) ** 2)
    img = screen(img, "#FF7208", (np.exp(-(d / 0.34) ** 2) * 0.78)[..., None])
    img = screen(img, "#FFC27A", (np.exp(-(d / 0.09) ** 2) * 0.40)[..., None])
    for k, col in ribbons(w, h, [
        (0.64, 0.07, 0.55, 0.6, -0.20, 0.060, 0.66, ORANGE_500, ORANGE_300),
        (0.70, 0.06, 0.48, 1.4, -0.24, 0.035, 0.55, ORANGE_400, "#FFE9CC"),
        (0.76, 0.05, 0.62, 2.1, -0.18, 0.090, 0.32, ORANGE_600, ORANGE_400),
    ]):
        img = 255.0 - (255.0 - img) * (1.0 - col / 255.0 * k)
    b = bokeh(w, h, (0.80, 0.18), (0.10, 0.10), 34, [ORANGE_300, ORANGE_200, ORANGE_400], 3,
              0.002, 0.014, 0.06, 0.24, w / 1100)
    img = blend_layer(img, b)
    return finish(img, 1, 0.38)


def wp_miere(w, h):
    img = gradient_base(w, h, HONEY_800, HONEY_300, (0.25, 0.25), "#FFF7E3", 0.6, 0.45)
    specs = [(0.78, 0.62, 0.50, -32, 0.09, 14), (0.18, 0.92, 0.22, 40, 0.07, 22), (0.40, 0.30, 0.10, 15, 0.09, 2)]
    img = blend_layer(img, leaves_layer(w, h, specs, "#FFF8E6"))
    b = bokeh(w, h, (0.28, 0.30), (0.2, 0.18), 40, ["#FFFFFF", HONEY_100, HONEY_200], 5, 0.004, 0.03, 0.05, 0.22, w / 900)
    img = blend_layer(img, b)
    return finish(img, 2)


def wp_noapte(w, h):
    img = gradient_base(w, h, "#061E23", TEAL_800, (0.75, 0.25), TEAL_300, 0.5, 0.25)
    specs = [(0.30, 0.62, 0.46, 18, 0.07, 10), (0.80, 0.86, 0.24, -50, 0.06, 20), (0.66, 0.34, 0.10, -20, 0.08, 2)]
    img = blend_layer(img, leaves_layer(w, h, specs, TEAL_200))
    b = bokeh(w, h, (0.72, 0.28), (0.18, 0.18), 50, [TEAL_200, HONEY_300, "#FFFFFF"], 9, 0.002, 0.018, 0.06, 0.30, w / 1200)
    img = blend_layer(img, b)
    return finish(img, 3, 0.35)


def wp_clasic(w, h):
    img = np.zeros((h, w, 3), np.float32) + rgb("#3B3430")
    return finish(img, 4, 0.0)


def wp_login(w, h):
    """Login / boot-menu background: calmer variant of the default."""
    y, x = np.mgrid[0:h, 0:w].astype(np.float32)
    img = gradient_base(w, h, "#0A0908", "#2A1406", (0.5, 0.0), "#FFFFFF", 0.4, 0.0)
    d = np.sqrt(((x / w - 0.5) ** 2) + ((y / h + 0.05) * h / w) ** 2)
    img = screen(img, "#FF7208", (np.exp(-(d / 0.40) ** 2) * 0.50)[..., None])
    for k, col in ribbons(w, h, [
        (0.78, 0.05, 0.50, 0.9, -0.10, 0.06, 0.46, ORANGE_500, ORANGE_300),
        (0.83, 0.04, 0.60, 2.0, -0.12, 0.03, 0.38, ORANGE_400, "#FFE9CC"),
    ]):
        img = 255.0 - (255.0 - img) * (1.0 - col / 255.0 * k)
    return finish(img, 5, 0.36)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    W, H = (int(sys.argv[2]), int(sys.argv[3])) if len(sys.argv) > 3 else (3840, 2160)
    for name, fn in [("tei", wp_tei), ("miere", wp_miere), ("noapte", wp_noapte), ("clasic", wp_clasic), ("login", wp_login)]:
        im = fn(W, H)
        im.save(os.path.join(out, f"{name}.jpg"), quality=92, subsampling=0, optimize=True)
        print("wrote", name)
