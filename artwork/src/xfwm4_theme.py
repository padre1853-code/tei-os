"""Generate the Tei xfwm4 window-border theme (original design) at 1x and 2x."""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa

SS = 4  # supersampling factor


def vgrad(w, h, stops):
    """Vertical gradient RGBA array from [(pos, hex, alpha)]."""
    pos = np.array([s[0] for s in stops], np.float32)
    cols = np.array([hex2rgb(s[1]) + (s[2] * 255,) for s in stops], np.float32)
    t = np.linspace(0, 1, h, dtype=np.float32)
    out = np.zeros((h, 4), np.float32)
    for c in range(4):
        out[:, c] = np.interp(t, pos, cols[:, c])
    return np.repeat(out[:, None, :], w, axis=1)


def to_img(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")


def over(dst, src):
    dst.alpha_composite(src)
    return dst


SCHEMES = {
    "active": dict(
        title=[(0, "#5CC0C9", 1), (0.08, "#3FA6B0", 1), (0.5, "#248893", 1), (0.51, "#1C7B86", 1), (1, "#166670", 1)],
        gloss=0.22, top_line=(255, 255, 255, 120), bottom_line=TEAL_900,
        border=TEAL_600, border_out=TEAL_900, border_in=TEAL_400,
        btn_border=(255, 255, 255, 150), btn_fill_top=0.38, btn_fill_bot=0.08, glyph=(255, 255, 255, 255),
        glyph_shadow=(8, 50, 56, 170),
    ),
    "inactive": dict(
        title=[(0, "#C3D6D8", 1), (0.5, "#A9C1C4", 1), (0.51, "#9FB9BC", 1), (1, "#90ABAF", 1)],
        gloss=0.18, top_line=(255, 255, 255, 140), bottom_line="#6F8E92",
        border="#9DB6B9", border_out="#6F8E92", border_in="#C7D8DA",
        btn_border=(255, 255, 255, 120), btn_fill_top=0.30, btn_fill_bot=0.06, glyph=(246, 250, 250, 255),
        glyph_shadow=(90, 120, 124, 120),
    ),
}


def title_strip(scheme, w, h):
    s = SCHEMES[scheme]
    a = vgrad(w, h, s["title"])
    img = to_img(a)
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (w, 0)], fill=s["top_line"], width=max(1, h // 28))
    d.line([(0, h - 1), (w, h - 1)], fill=hex2rgb(s["bottom_line"]) + (255,), width=max(1, h // 28))
    return img


def corner(scheme, side, H, R, B):
    """Top-left / top-right corner piece: width = R+? (we use max(R, B)+B), height H."""
    s = SCHEMES[scheme]
    W = R + B
    big = Image.new("RGBA", (W * SS, H * SS), (0, 0, 0, 0))
    strip = title_strip(scheme, W * SS, H * SS)
    mask = Image.new("L", (W * SS, H * SS), 0)
    md = ImageDraw.Draw(mask)
    # rounded rect extending beyond right edge so only the left corner is rounded
    md.rounded_rectangle([0, 0, W * SS * 3, H * SS * 3], radius=R * SS, fill=255)
    big.paste(strip, (0, 0), mask)
    d = ImageDraw.Draw(big)
    # outer dark outline along the rounded edge
    d.rounded_rectangle([0, 0, W * SS * 3, H * SS * 3], radius=R * SS,
                        outline=hex2rgb(s["border_out"]) + (255,), width=SS)
    # inner highlight
    d.rounded_rectangle([SS, SS, W * SS * 3, H * SS * 3], radius=(R - 1) * SS,
                        outline=(255, 255, 255, 90), width=SS)
    # side border strip below the title bar is drawn by left/right pieces; title bottom line:
    d.line([(0, H * SS - SS), (W * SS, H * SS - SS)], fill=hex2rgb(s["bottom_line"]) + (255,), width=SS)
    img = big.resize((W, H), Image.LANCZOS)
    if side == "right":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def side_piece(scheme, side, B, length=8):
    """Left/right border (B wide, tiled vertically): dark outer, mid, light inner."""
    s = SCHEMES[scheme]
    img = Image.new("RGBA", (B, length), hex2rgb(s["border"]) + (255,))
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (0, length)], fill=hex2rgb(s["border_out"]) + (255,))
    d.line([(B - 1, 0), (B - 1, length)], fill=hex2rgb(s["border_in"]) + (255,))
    if B >= 6:
        d.line([(1, 0), (1, length)], fill=hex2rgb(lighten(s["border"], 0.25)) + (255,))
    if side == "right":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def bottom_piece(scheme, B, length=8):
    s = SCHEMES[scheme]
    img = Image.new("RGBA", (length, B), hex2rgb(s["border"]) + (255,))
    d = ImageDraw.Draw(img)
    d.line([(0, B - 1), (length, B - 1)], fill=hex2rgb(s["border_out"]) + (255,))
    d.line([(0, 0), (length, 0)], fill=hex2rgb(s["border_in"]) + (255,))
    return img


def bottom_corner(scheme, side, B):
    s = SCHEMES[scheme]
    img = Image.new("RGBA", (B, B), hex2rgb(s["border"]) + (255,))
    d = ImageDraw.Draw(img)
    d.line([(0, 0), (0, B)], fill=hex2rgb(s["border_out"]) + (255,))
    d.line([(0, B - 1), (B, B - 1)], fill=hex2rgb(s["border_out"]) + (255,))
    if side == "right":
        img = img.transpose(Image.FLIP_LEFT_RIGHT)
    return img


def glyph(draw, kind, box, col, width):
    x0, y0, x1, y1 = box
    w = x1 - x0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if kind == "close":
        k = w * 0.26
        draw.line([(cx - k, cy - k), (cx + k, cy + k)], fill=col, width=width)
        draw.line([(cx - k, cy + k), (cx + k, cy - k)], fill=col, width=width)
        # rounded caps
        r = width / 2
        for (px, py) in [(cx - k, cy - k), (cx + k, cy + k), (cx - k, cy + k), (cx + k, cy - k)]:
            draw.ellipse([px - r, py - r, px + r, py + r], fill=col)
    elif kind == "hide":
        k = w * 0.26
        draw.rounded_rectangle([cx - k, cy + w * 0.12, cx + k, cy + w * 0.12 + width], radius=width / 3, fill=col)
    elif kind == "maximize":
        k = w * 0.25
        draw.rectangle([cx - k, cy - k, cx + k, cy + k], outline=col, width=width // 2 + 1)
        draw.rectangle([cx - k, cy - k, cx + k, cy - k + width], fill=col)
    elif kind == "maximize-toggled":
        k = w * 0.19
        o = w * 0.09
        draw.rectangle([cx - k + o, cy - k - o, cx + k + o, cy + k - o], outline=col, width=width // 2)
        draw.rectangle([cx - k + o, cy - k - o, cx + k + o, cy - k - o + width * 0.8], fill=col)
        draw.rectangle([cx - k - o, cy - k + o, cx + k - o, cy + k + o], outline=col, width=width // 2 + 1)
        draw.rectangle([cx - k - o, cy - k + o, cx + k - o, cy - k + o + width], fill=col)
    elif kind == "shade":
        k = w * 0.24
        draw.polygon([(cx - k, cy + k * 0.5), (cx + k, cy + k * 0.5), (cx, cy - k * 0.6)], fill=col)
    elif kind == "shade-toggled":
        k = w * 0.24
        draw.polygon([(cx - k, cy - k * 0.5), (cx + k, cy - k * 0.5), (cx, cy + k * 0.6)], fill=col)
    elif kind == "stick":
        r = w * 0.12
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], outline=col, width=width // 2 + 1)
    elif kind == "stick-toggled":
        r = w * 0.14
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col)


def button(scheme, kind, state, H, BW, BS):
    """Button image: title-bar background baked in, glass button BSxBS centred, glyph."""
    s = SCHEMES[scheme]
    big_w, big_h = BW * SS, H * SS
    img = title_strip(scheme, big_w, big_h)
    if kind == "menu":
        return img.resize((BW, H), Image.LANCZOS)  # app icon drawn by xfwm4 on top
    bx0 = (big_w - BS * SS) // 2
    by0 = (big_h - BS * SS) // 2 - SS // 2
    box = [bx0, by0, bx0 + BS * SS, by0 + BS * SS]
    r = int(BS * SS * 0.22)
    base_kind = kind.replace("-toggled", "")
    # glass body
    top, bot = s["btn_fill_top"], s["btn_fill_bot"]
    tint = None
    if state == "prelight":
        top, bot = top + 0.22, bot + 0.18
    if state == "pressed":
        top, bot = 0.05, 0.25
    if base_kind == "close" and state in ("prelight", "pressed") and scheme == "active":
        tint = ("#F07A5C", "#C8392B") if state == "prelight" else ("#B8331F", "#E0583F")
    body = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    bd = ImageDraw.Draw(body)
    if tint:
        g = vgrad(BS * SS, BS * SS, [(0, tint[0], 1), (1, tint[1], 1)])
    else:
        g = vgrad(BS * SS, BS * SS, [(0, "#FFFFFF", top), (0.5, "#FFFFFF", (top + bot) / 2), (0.51, "#FFFFFF", bot), (1, "#FFFFFF", bot + 0.05)])
    gi = to_img(g)
    m = Image.new("L", (BS * SS, BS * SS), 0)
    ImageDraw.Draw(m).rounded_rectangle([0, 0, BS * SS - 1, BS * SS - 1], radius=r, fill=255)
    body.paste(gi, (bx0, by0), m)
    if state == "pressed":
        # inner shadow at top
        sh = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([bx0, by0, bx0 + BS * SS, by0 + BS * SS * 0.45], radius=r, fill=(0, 0, 0, 40))
        body.alpha_composite(sh)
    # border: dark outer + light inner
    bd.rounded_rectangle(box, radius=r, outline=hex2rgb(s["bottom_line"]) + (200,), width=SS)
    bd.rounded_rectangle([box[0] + SS, box[1] + SS, box[2] - SS, box[3] - SS], radius=r - SS,
                         outline=s["btn_border"], width=SS)
    img.alpha_composite(body)
    # glyph with soft shadow
    gl = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(gl), kind, box, s["glyph_shadow"], int(SS * 2.4))
    gl = gl.filter(ImageFilter.GaussianBlur(SS * 0.8))
    shifted = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    shifted.paste(gl, (0, SS), gl)
    img.alpha_composite(shifted)
    gl2 = Image.new("RGBA", (big_w, big_h), (0, 0, 0, 0))
    glyph(ImageDraw.Draw(gl2), kind, box, s["glyph"], int(SS * 2.2))
    img.alpha_composite(gl2)
    return img.resize((BW, H), Image.LANCZOS)


THEMERC = """# Tei xfwm4 theme — original design for Tei OS
# License: GPL-2.0-or-later
active_text_color=#FFFFFF
active_text_shadow_color=#0B3A41
inactive_text_color=#F4F8F8
inactive_text_shadow_color=#7A979B
title_shadow_active=true
title_shadow_inactive=true
title_alignment=left
full_width_title=true
title_horizontal_offset={tho}
title_vertical_offset_active={tvo}
title_vertical_offset_inactive={tvo}
button_offset={bo}
button_spacing={bs}
button_layout=O|HMC
show_app_icon=true
maximized_offset=0
shadow_delta_height=2
shadow_delta_width=0
shadow_delta_x=0
shadow_delta_y=-4
shadow_opacity=45
"""


def build(out, scale=1):
    os.makedirs(out, exist_ok=True)
    H = 28 * scale       # title height
    R = 8 * scale        # corner radius
    B = 4 * scale        # border width
    BW = 25 * scale      # button cell width
    BS = 21 * scale      # glass button size
    for sch in ("active", "inactive"):
        title_strip(sch, 2, H).save(f"{out}/title-1-{sch}.png")
        for n in (2, 3, 4, 5):
            title_strip(sch, 2, H).save(f"{out}/title-{n}-{sch}.png")
        corner(sch, "left", H, R, B).save(f"{out}/top-left-{sch}.png")
        corner(sch, "right", H, R, B).save(f"{out}/top-right-{sch}.png")
        side_piece(sch, "left", B).save(f"{out}/left-{sch}.png")
        side_piece(sch, "right", B).save(f"{out}/right-{sch}.png")
        bottom_piece(sch, B).save(f"{out}/bottom-{sch}.png")
        bottom_corner(sch, "left", B).save(f"{out}/bottom-left-{sch}.png")
        bottom_corner(sch, "right", B).save(f"{out}/bottom-right-{sch}.png")
        for kind in ("close", "hide", "maximize", "maximize-toggled", "shade", "shade-toggled",
                     "stick", "stick-toggled", "menu"):
            for state in ("active", "inactive", "prelight", "pressed"):
                # xfwm4 naming: <kind>-<state>.png ; for inactive windows only "inactive" is used
                sch_for = "inactive" if state == "inactive" else sch
                if sch == "inactive" and state != "inactive":
                    continue
                st = "active" if state == "inactive" else state
                img = button(sch_for, kind, st, H, BW, BS)
                img.save(f"{out}/{kind}-{state}.png")
    open(f"{out}/themerc", "w").write(THEMERC.format(tho=4 * scale, tvo=1 * scale, bo=4 * scale, bs=1 * scale))
    print("xfwm4 theme written to", out)


if __name__ == "__main__":
    build(sys.argv[1], int(sys.argv[2]) if len(sys.argv) > 2 else 1)
