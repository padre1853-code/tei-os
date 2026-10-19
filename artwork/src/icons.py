"""WinLow XP icon theme ("Tei") — original glossy 2000s-style icons, drawn from code.

Every icon is an SVG on a 64x64 canvas, light from the top-left, soft outline,
gloss highlight and a contact shadow. Nothing here is traced from another icon set.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa
from logo import LEAF_PATH, STEM, VEINS, MIDRIB  # noqa

_uid = [0]


def uid(p="g"):
    _uid[0] += 1
    return f"{p}{_uid[0]}"


def lg(stops, x1=0, y1=0, x2=0, y2=1, gid=None):
    gid = gid or uid("lg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(t + (None,))[:3] for t in stops])
    return gid, f'<linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">{s}</linearGradient>'


def rg(stops, cx=0.5, cy=0.5, r=0.5, fx=None, fy=None, gid=None):
    gid = gid or uid("rg")
    s = "".join(f'<stop offset="{o}" stop-color="{c}"' + (f' stop-opacity="{a}"' if a is not None else "") + "/>"
                for o, c, a in [(t + (None,))[:3] for t in stops])
    f = (f' fx="{fx}"' if fx is not None else "") + (f' fy="{fy}"' if fy is not None else "")
    return gid, f'<radialGradient id="{gid}" cx="{cx}" cy="{cy}" r="{r}"{f}>{s}</radialGradient>'


class Icon:
    def __init__(self):
        self.defs = []
        self.body = []

    def grad(self, g):
        gid, d = g
        self.defs.append(d)
        return f"url(#{gid})"

    def add(self, s):
        self.body.append(s)

    def shadow(self, cx=32, cy=58, rx=22, ry=3.2, op=0.28):
        fid = uid("blur")
        self.defs.append(f'<filter id="{fid}" x="-30%" y="-150%" width="160%" height="400%"><feGaussianBlur stdDeviation="1.6"/></filter>')
        self.add(f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="#000" opacity="{op}" filter="url(#{fid})"/>')

    def svg(self, size=64):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 64 64">'
                f'<defs>{"".join(self.defs)}</defs>{"".join(self.body)}</svg>')


def gloss(ic, path, top=0.55, bottom=0.0):
    f = ic.grad(lg([(0, "#FFFFFF", top), (1, "#FFFFFF", bottom)]))
    ic.add(f'<path d="{path}" fill="{f}"/>')


def orb_mark(ic, cx, cy, r, sparkle=False):
    """The WinLow XP logo (orange orb with a white W) at centre (cx, cy), radius r, in 64-px icon units."""
    o = ic.grad(rg([(0, "#FFE6B8"), (0.26, "#FFB04A"), (0.64, ORANGE_500), (1, ORANGE_800)], 0.40, 0.30, 0.78))
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{o}" stroke="{ORANGE_900}" stroke-width="{max(0.6, r * 0.05):.2f}"/>')
    k = r / 104.0  # logo geometry is a 256-px box with the orb centred at (128, 124), radius 104
    tx, ty = cx - 128 * k, cy - 124 * k
    gl = ic.grad(lg([(0, "#FFFFFF", 0.80), (1, "#FFFFFF", 0.04)]))
    ic.add(f'<g transform="translate({tx:.3f} {ty:.3f}) scale({k:.4f})">'
           f'<path d="M38 112 C42 56 84 28 128 28 C172 28 214 56 218 112 C188 94 160 88 128 88 C96 88 68 94 38 112 Z" fill="{gl}"/>'
           f'<path d="M66 92 L98 166 L128 108 L158 166 L194 84" fill="none" stroke="{ORANGE_900}" stroke-opacity="0.45" '
           f'stroke-width="27" stroke-linecap="round" stroke-linejoin="round" transform="translate(0 7)"/>'
           f'<path d="M66 92 L98 166 L128 108 L158 166 L194 84" fill="none" stroke="#FFFFFF" stroke-width="25" '
           f'stroke-linecap="round" stroke-linejoin="round"/>'
           + (f'<path d="M200 46 L205 59 L218 64 L205 69 L200 82 L195 69 L182 64 L195 59 Z" fill="#FFFFFF"/>' if sparkle else "")
           + '</g>')


# ---------------------------------------------------------------- glyphs
# Emblem glyphs are drawn in a 24x24 box (0..24) and placed with a transform.
GLYPHS = {
    "home": '<path d="M12 3 L2 11.5 H5 V21 H10 V15 H14 V21 H19 V11.5 H22 Z" />',
    "document": '<path d="M5 2 H14 L19 7 V22 H5 Z M14 2 V7 H19" /><path d="M8 11 H16 M8 14 H16 M8 17 H13" stroke-width="1.8" stroke-linecap="round" fill="none" class="ln"/>',
    "music": '<path d="M9 4 L20 2 V16.5 A3 3 0 1 1 18 13.7 V6.5 L11 7.8 V18.5 A3 3 0 1 1 9 15.7 Z" />',
    "pictures": '<path d="M2 5 H22 V20 H2 Z" /><path d="M4 18 L9 11 L12.5 15 L15 12.5 L20 18 Z" class="cut"/><circle cx="16.5" cy="8.8" r="2" class="cut"/>',
    "videos": '<path d="M2 6 H16 V18 H2 Z M16 10 L22 6.5 V17.5 L16 14 Z" />',
    "download": '<path d="M9.5 2 H14.5 V11 H19.5 L12 19 L4.5 11 H9.5 Z" /><path d="M3 20 H21 V22.5 H3 Z" />',
    "desktop": '<path d="M2 3 H22 V17 H14 V20 H17 V22 H7 V20 H10 V17 H2 Z" /><path d="M4 5 H20 V15 H4 Z" class="cut"/>',
    "templates": '<path d="M4 2 H13 L18 7 V22 H4 Z" /><path d="M7 10 H15 M7 13 H15 M7 16 H11" class="ln" fill="none" stroke-width="1.8" stroke-dasharray="2 1.2"/>',
    "public": '<circle cx="8" cy="7" r="3.2"/><circle cx="16.5" cy="7.5" r="3"/><path d="M2 20 C2 14 5 12 8 12 C11 12 14 14 14 20 Z"/><path d="M12.5 13.5 C13.5 12.6 15 12.2 16.5 12.2 C19.5 12.2 22 14 22 20 H15.5 C15.5 17 14.5 15 12.5 13.5 Z"/>',
    "network": '<circle cx="12" cy="12" r="9.5" /><path d="M12 2.5 C8 6 8 18 12 21.5 M12 2.5 C16 6 16 18 12 21.5 M2.5 12 H21.5 M4 7 H20 M4 17 H20" class="ln" fill="none" stroke-width="1.4"/>',
    "recent": '<circle cx="12" cy="12" r="9.5"/><path d="M12 6 V12.5 L16 15" class="ln" fill="none" stroke-width="2.2" stroke-linecap="round"/>',
    "star": '<path d="M12 2 L14.9 8.6 L22 9.3 L16.6 14 L18.2 21 L12 17.3 L5.8 21 L7.4 14 L2 9.3 L9.1 8.6 Z"/>',
}


def glyph(ic, name, x, y, size, fill, stroke=None, cut="#FFFFFF", ln=None):
    """Place a glyph; '.cut' parts are filled with `cut`, '.ln' parts stroked with `ln`."""
    s = size / 24.0
    g = GLYPHS[name]
    g = g.replace('class="cut"', f'fill="{cut}"').replace('class="ln"', f'stroke="{ln or cut}"')
    st = f' stroke="{stroke}" stroke-width="{1.2 / s:.2f}" stroke-linejoin="round"' if stroke else ""
    ic.add(f'<g transform="translate({x} {y}) scale({s:.4f})" fill="{fill}"{st}>{g}</g>')


def embossed(ic, name, x, y, size, base):
    """Emblem pressed into a surface: light lower edge + darker glyph."""
    glyph(ic, name, x, y + 0.8, size, lighten(base, 0.55), cut=lighten(base, 0.55), ln=lighten(base, 0.55))
    glyph(ic, name, x, y, size, darken(base, 0.30), cut=lighten(base, 0.2), ln=lighten(base, 0.25))


# ---------------------------------------------------------------- folders
FOLDER_COLORS = {
    "honey": ("#FFE39A", HONEY_400, HONEY_500, HONEY_600, HONEY_800),
    "teal": ("#BDEBF0", TEAL_300, TEAL_400, TEAL_600, TEAL_900),
    "leaf": ("#DDF2B5", LEAF_300, LEAF_400, LEAF_600, LEAF_800),
}


def folder(emblem=None, color="honey", open_=False, badge=None):
    ic = Icon()
    hi, c1, c2, c3, edge = FOLDER_COLORS[color]
    ic.shadow(32, 57.5, 26, 3)
    back = ic.grad(lg([(0, c2), (1, c3)]))
    ic.add(f'<path d="M5 12.5 Q5 10 7.5 10 H22 Q23.6 10 24.6 11.4 L27.6 15.5 H56.5 Q59 15.5 59 18 V51 Q59 54 56 54 H8 Q5 54 5 51 Z" '
           f'fill="{back}" stroke="{edge}" stroke-width="1.3" stroke-linejoin="round"/>')
    # paper
    ic.add('<path d="M10.5 19.5 H52 V46 H10.5 Z" fill="#FFFFFF" stroke="#9FAEB0" stroke-width="0.8" transform="rotate(-2.5 32 32)"/>')
    ic.add('<path d="M14 25 H46 M14 29 H44 M14 33 H40" stroke="#C9D3D4" stroke-width="1.2" transform="rotate(-2.5 32 32)"/>')
    front = ic.grad(lg([(0, hi), (0.45, c1), (1, c2)]))
    if open_:
        fp = "M2.5 28 Q2.5 26 4.5 26 H59.5 Q62 26 61.5 28.5 L57.5 51.5 Q57 54 54.5 54 H9.5 Q7 54 6.6 51.5 Z"
    else:
        fp = "M4 25.5 Q4 23.5 6 23.5 H58 Q60 23.5 60 25.5 L58.7 51 Q58.5 54 55.5 54 H8.5 Q5.5 54 5.3 51 Z"
    ic.add(f'<path d="{fp}" fill="{front}" stroke="{edge}" stroke-width="1.3" stroke-linejoin="round"/>')
    gl = ic.grad(lg([(0, "#FFFFFF", 0.65), (1, "#FFFFFF", 0.0)]))
    ic.add(f'<path d="M6 24.6 H58 Q59 24.6 58.9 26 L58.6 31 Q40 29 5.5 33 L5.1 26 Q5 24.6 6 24.6 Z" fill="{gl}"/>')
    if emblem:
        embossed(ic, emblem, 23, 30.5, 18, c2)
    if badge:
        badge(ic)
    return ic.svg()


# ---------------------------------------------------------------- pages / mimetypes
def page(band=None, glyph_name=None, glyph_col=None, label=None, lines=True, special=None):
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6, 0.22)
    pg = ic.grad(lg([(0, "#FFFFFF"), (1, "#E9EEEF")]))
    ic.add(f'<path d="M13 4 H40 L52 16 V58 Q52 60 50 60 H15 Q13 60 13 58 Z" fill="{pg}" stroke="#7F9093" stroke-width="1.2" stroke-linejoin="round"/>')
    fold = ic.grad(lg([(0, "#FFFFFF"), (1, "#C9D3D5")], 0, 0, 1, 1))
    ic.add(f'<path d="M40 4 V14 Q40 16 42 16 H52 Z" fill="{fold}" stroke="#7F9093" stroke-width="1.2" stroke-linejoin="round"/>')
    if lines:
        for i, y in enumerate((22, 27, 32, 37, 42)):
            w = 30 if i % 3 else 24
            ic.add(f'<path d="M18 {y} H{18 + w}" stroke="#B9C5C7" stroke-width="2" stroke-linecap="round"/>')
    if special:
        special(ic)
    if band:
        b = ic.grad(lg([(0, lighten(band, 0.25)), (1, darken(band, 0.12))]))
        ic.add(f'<path d="M13 46 H52 V58 Q52 60 50 60 H15 Q13 60 13 58 Z" fill="{b}" stroke="{darken(band, 0.35)}" stroke-width="1.2"/>')
        if label:
            ic.add(f'<text x="32.5" y="56.5" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" '
                   f'font-weight="700" font-size="9" fill="#FFFFFF">{label}</text>')
    if glyph_name:
        glyph(ic, glyph_name, 20.5, 19, 24, glyph_col or TEAL_600)
    return ic.svg()


def sp_spreadsheet(ic):
    ic.add('<rect x="18" y="20" width="29" height="22" fill="#FFFFFF" stroke="#5E9A3A" stroke-width="1.2"/>')
    for x in (27.7, 37.3):
        ic.add(f'<path d="M{x} 20 V42" stroke="#9CC27E" stroke-width="1"/>')
    for y in (25.5, 31, 36.5):
        ic.add(f'<path d="M18 {y} H47" stroke="#9CC27E" stroke-width="1"/>')
    ic.add('<rect x="18" y="20" width="29" height="5.5" fill="#CFE6BC"/>')


def sp_presentation(ic):
    ic.add(f'<rect x="17" y="20" width="31" height="21" rx="1" fill="#FFF4E2" stroke="{HONEY_700}" stroke-width="1.2"/>')
    ic.add(f'<path d="M22 36 V30 M27 36 V26 M32 36 V29 M37 36 V24 M42 36 V31" stroke="{HONEY_600}" stroke-width="3"/>')


def sp_image(ic):
    sky = ic.grad(lg([(0, "#7FC8F0"), (1, "#D8F0FB")]))
    ic.add(f'<rect x="17" y="19" width="31" height="24" fill="{sky}" stroke="#5B8EA8" stroke-width="1.2"/>')
    ic.add(f'<path d="M17 43 L26 31 L32 37 L37 32 L48 43 Z" fill="{LEAF_500}" stroke="{LEAF_700}" stroke-width="0.8"/>')
    ic.add(f'<circle cx="41" cy="25" r="3.2" fill="{HONEY_400}"/>')


def sp_audio(ic):
    glyph(ic, "music", 20, 18, 24, TEAL_600)


def sp_video(ic):
    ic.add(f'<rect x="16" y="19" width="33" height="24" rx="2" fill="{GRAPHITE_800}"/>')
    for x in range(18, 48, 5):
        ic.add(f'<rect x="{x}" y="20.5" width="2.6" height="2.6" fill="#FFFFFF" opacity="0.85"/><rect x="{x}" y="38.9" width="2.6" height="2.6" fill="#FFFFFF" opacity="0.85"/>')
    ic.add(f'<path d="M28 25.5 L38 31 L28 36.5 Z" fill="{HONEY_400}"/>')


def sp_script(ic):
    ic.add(f'<rect x="16" y="19" width="33" height="24" rx="2" fill="{GRAPHITE_900}"/>')
    ic.add(f'<path d="M20 25 L25 29 L20 33" stroke="{LEAF_400}" stroke-width="2" fill="none" stroke-linecap="round"/>')
    ic.add(f'<path d="M27 34 H35" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round"/>')


def sp_html(ic):
    glyph(ic, "network", 20.5, 19, 24, BLUE_500, cut="#FFFFFF", ln="#FFFFFF")


def sp_font(ic):
    ic.add(f'<text x="32.5" y="40" text-anchor="middle" font-family="Noto Serif, DejaVu Serif, serif" font-size="22" font-weight="700" fill="{GRAPHITE_800}">Aa</text>')


def sp_exe(ic):
    ic.add(f'<rect x="16" y="19" width="33" height="24" rx="2" fill="#FFFFFF" stroke="{TEAL_700}" stroke-width="1.2"/>')
    t = ic.grad(lg([(0, TEAL_400), (1, TEAL_600)]))
    ic.add(f'<rect x="16" y="19" width="33" height="6" rx="2" fill="{t}"/>')
    gear(ic, 32.5, 34, 6.2, HONEY_500)


def gear(ic, cx, cy, r, col, teeth=8):
    import math
    pts = []
    for i in range(teeth * 2):
        a = math.pi * 2 * i / (teeth * 2)
        rr = r if i % 2 == 0 else r * 0.78
        a1 = a - math.pi / (teeth * 2) * 0.55
        a2 = a + math.pi / (teeth * 2) * 0.55
        pts.append((cx + rr * math.cos(a1), cy + rr * math.sin(a1)))
        pts.append((cx + rr * math.cos(a2), cy + rr * math.sin(a2)))
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts) + " Z"
    f = ic.grad(lg([(0, lighten(col, 0.35)), (1, darken(col, 0.15))]))
    ic.add(f'<path d="{d}" fill="{f}" stroke="{darken(col, 0.4)}" stroke-width="0.9" stroke-linejoin="round"/>')
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.32:.2f}" fill="#FFFFFF" stroke="{darken(col, 0.4)}" stroke-width="0.9"/>')


# ---------------------------------------------------------------- hardware
def monitor_body(ic, x=6, y=8, w=52, h=36, screen=None, stand=True):
    if stand:
        st = ic.grad(lg([(0, SILVER_200), (1, SILVER_400)]))
        ic.add(f'<path d="M27 {y + h - 1} H37 L39 {y + h + 7} H25 Z" fill="{st}" stroke="#6F7A7D" stroke-width="1"/>')
        ic.add(f'<path d="M17 {y + h + 6.5} H47 Q49 {y + h + 6.5} 49 {y + h + 8.5} V{y + h + 9.5} H15 V{y + h + 8.5} Q15 {y + h + 6.5} 17 {y + h + 6.5} Z" fill="{st}" stroke="#6F7A7D" stroke-width="1"/>')
    bz = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
    ic.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{bz}" stroke="#141819" stroke-width="1.2"/>')
    sx, sy, sw, sh = x + 3.5, y + 3.5, w - 7, h - 8
    if screen is None:
        scr = ic.grad(rg([(0, "#9A4A10"), (0.55, "#3A1E0C"), (1, "#120E0C")], 0.72, 0.18, 0.95))
        ic.add(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{scr}"/>')
        orb_mark(ic, sx + sw / 2, sy + sh / 2, min(sw, sh) * 0.30)
    else:
        screen(ic, sx, sy, sw, sh)
    gl = ic.grad(lg([(0, "#FFFFFF", 0.42), (1, "#FFFFFF", 0.0)], 0, 0, 0.6, 1))
    ic.add(f'<path d="M{sx} {sy} H{sx + sw} V{sy + sh * 0.18} Q{sx + sw * 0.5} {sy + sh * 0.42} {sx} {sy + sh * 0.62} Z" fill="{gl}"/>')
    ic.add(f'<circle cx="{x + w / 2}" cy="{y + h - 2.3}" r="0.9" fill="{LEAF_400}"/>')


def computer():
    ic = Icon()
    ic.shadow(32, 58.5, 20, 2.6)
    monitor_body(ic)
    return ic.svg()


def hdd(system=False):
    ic = Icon()
    ic.shadow(32, 54, 26, 3)
    top = ic.grad(lg([(0, "#F4F6F7"), (1, SILVER_300)]))
    ic.add(f'<path d="M8 22 L14 14 H50 L56 22 Z" fill="{top}" stroke="#6F7A7D" stroke-width="1.2" stroke-linejoin="round"/>')
    body = ic.grad(lg([(0, SILVER_200), (0.5, SILVER_300), (1, "#8A9497")]))
    ic.add(f'<rect x="8" y="22" width="48" height="26" rx="2.5" fill="{body}" stroke="#5E686B" stroke-width="1.2"/>')
    ic.add(f'<rect x="12" y="27" width="30" height="16" rx="1.5" fill="#E9EEEF" stroke="#8A9497" stroke-width="0.8"/>')
    ic.add(f'<path d="M15 31 H38 M15 35 H34 M15 39 H30" stroke="#A9B4B6" stroke-width="1.4"/>')
    led = LEAF_400
    ic.add(f'<circle cx="50" cy="42" r="2.2" fill="{led}" stroke="{LEAF_800}" stroke-width="0.8"/>')
    ic.add('<circle cx="49.4" cy="41.3" r="0.8" fill="#FFFFFF" opacity="0.8"/>')
    if system:
        orb_mark(ic, 48, 28, 7)
    gloss(ic, "M9 23 H55 V30 Q32 33 9 30 Z", 0.45)
    return ic.svg()


def usb():
    ic = Icon()
    ic.shadow(32, 57, 18, 2.4)
    ic.add('<g transform="rotate(-35 32 32)">')
    metal = ic.grad(lg([(0, "#F3F5F5"), (1, SILVER_400)], 0, 0, 1, 0))
    ic.add(f'<rect x="25" y="4" width="14" height="13" rx="1" fill="{metal}" stroke="#6F7A7D" stroke-width="1.1"/>')
    ic.add('<rect x="28" y="7" width="3" height="3" fill="#6F7A7D"/><rect x="33" y="7" width="3" height="3" fill="#6F7A7D"/>')
    body = ic.grad(lg([(0, TEAL_400), (0.5, TEAL_600), (1, TEAL_800)], 0, 0, 1, 0))
    ic.add(f'<rect x="21" y="16" width="22" height="40" rx="4" fill="{body}" stroke="{TEAL_950}" stroke-width="1.2"/>')
    ic.add(f'<rect x="24" y="22" width="16" height="10" rx="1.5" fill="{HONEY_400}" stroke="{HONEY_700}" stroke-width="0.8"/>')
    gloss(ic, "M22.5 17.5 H31 V54.5 H25 Q22.5 54.5 22.5 52 Z", 0.4)
    ic.add('</g>')
    return ic.svg()


def optical():
    ic = Icon()
    ic.shadow(32, 58, 22, 2.8)
    d = ic.grad(rg([(0, "#FFFFFF"), (0.35, "#DDE7EA"), (0.55, "#C7E7E0"), (0.7, "#E9D9F2"), (0.85, "#F5E7C6"), (1, "#C9D4D7")], 0.42, 0.38, 0.65))
    ic.add(f'<circle cx="32" cy="31" r="26" fill="{d}" stroke="#7F9093" stroke-width="1.2"/>')
    ic.add('<circle cx="32" cy="31" r="8.5" fill="#E9EEEF" stroke="#9FAEB0" stroke-width="1"/>')
    ic.add('<circle cx="32" cy="31" r="3.2" fill="#FFFFFF" stroke="#7F9093" stroke-width="1"/>')
    ic.add('<path d="M14 18 A22 22 0 0 1 30 9" stroke="#FFFFFF" stroke-width="3" fill="none" opacity="0.8" stroke-linecap="round"/>')
    return ic.svg()


def trash(full=False):
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6)
    body = ic.grad(lg([(0, "#E3ECED"), (0.35, "#C3D2D4"), (0.75, "#9DB0B3"), (1, "#7E9396")], 0, 0, 1, 0))
    ic.add(f'<path d="M14 18 H50 L46.5 57 Q46.2 59 44 59 H20 Q17.8 59 17.5 57 Z" fill="{body}" stroke="#55676A" stroke-width="1.2" stroke-linejoin="round"/>')
    for x in (23, 29, 35, 41):
        ic.add(f'<path d="M{x} 23 L{x + (x - 32) * 0.08:.1f} 54" stroke="#6F8487" stroke-width="1.6" stroke-linecap="round" opacity="0.7"/>')
        ic.add(f'<path d="M{x + 1.4} 23 L{x + 1.4 + (x - 32) * 0.08:.1f} 54" stroke="#FFFFFF" stroke-width="0.8" stroke-linecap="round" opacity="0.6"/>')
    if full:
        p1 = ic.grad(lg([(0, "#FFFFFF"), (1, "#DCE3E4")]))
        ic.add(f'<path d="M17 18 Q16 9 24 8 Q27 3 33 6 Q40 2 44 8 Q51 9 48 18 Z" fill="{p1}" stroke="#7F9093" stroke-width="1"/>')
        ic.add('<path d="M22 13 L27 10 M31 9 L36 12 M39 9 L44 13" stroke="#9FAEB0" stroke-width="1" fill="none"/>')
        ic.add(f'<path d="M36 17 L41 6 L45 7.5 L40 18 Z" fill="{HONEY_200}" stroke="{HONEY_700}" stroke-width="0.8"/>')
    lid = ic.grad(lg([(0, "#F4F7F7"), (1, "#A8B8BB")]))
    ic.add(f'<rect x="11" y="15" width="42" height="6" rx="2" fill="{lid}" stroke="#55676A" stroke-width="1.2"/>')
    ic.add(f'<path d="M26 15 V12.5 Q26 11 27.5 11 H36.5 Q38 11 38 12.5 V15" fill="none" stroke="#55676A" stroke-width="1.6"/>')
    gloss(ic, "M15.5 21 H24 L22.6 55 H18.5 Z", 0.5)
    return ic.svg()


def globe(ic, cx=32, cy=30, r=22):
    sea = ic.grad(rg([(0, "#9EE0F5"), (0.6, BLUE_500), (1, "#1D4E8A")], 0.38, 0.32, 0.75))
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{sea}" stroke="#163E6E" stroke-width="1.2"/>')
    land = ic.grad(lg([(0, LEAF_300), (1, LEAF_600)]))
    s = r / 22
    ic.add(f'<g transform="translate({cx - 22 * s} {cy - 22 * s}) scale({s:.3f})" fill="{land}" stroke="{LEAF_800}" stroke-width="0.8">'
           '<path d="M9 13 Q14 6 22 7 Q26 9 24 13 Q20 14 21 18 Q24 21 21 25 Q18 29 14 26 Q10 22 9 18 Z"/>'
           '<path d="M28 9 Q34 7 37 11 Q36 14 32 14 Q29 13 28 9 Z"/>'
           '<path d="M27 22 Q32 18 38 21 Q41 25 37 31 Q34 37 30 35 Q28 30 27 26 Z"/></g>')
    gl = ic.grad(lg([(0, "#FFFFFF", 0.6), (1, "#FFFFFF", 0)]))
    ic.add(f'<ellipse cx="{cx - r * 0.18}" cy="{cy - r * 0.45}" rx="{r * 0.62}" ry="{r * 0.36}" fill="{gl}"/>')


def network():
    ic = Icon()
    ic.shadow(32, 59, 24, 2.5)
    globe(ic, 32, 25, 18)
    # two small computers linked under the globe
    for x in (6, 40):
        bz = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
        ic.add(f'<rect x="{x}" y="40" width="18" height="13" rx="1.5" fill="{bz}" stroke="#141819"/>')
        sc = ic.grad(lg([(0, "#57C3CC"), (1, TEAL_800)]))
        ic.add(f'<rect x="{x + 1.8}" y="41.8" width="14.4" height="8.4" fill="{sc}"/>')
        ic.add(f'<rect x="{x + 6}" y="53" width="6" height="2" fill="{SILVER_400}"/><rect x="{x + 3}" y="55" width="12" height="2" rx="1" fill="{SILVER_300}" stroke="#6F7A7D" stroke-width="0.6"/>')
    ic.add(f'<path d="M24 47 H40" stroke="{HONEY_500}" stroke-width="2.5" stroke-linecap="round"/>')
    ic.add(f'<path d="M32 43 V47" stroke="{HONEY_500}" stroke-width="2.5" stroke-linecap="round"/>')
    return ic.svg()


def server():
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6)
    body = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)], 0, 0, 1, 0))
    ic.add(f'<rect x="16" y="5" width="32" height="52" rx="3" fill="{body}" stroke="#101415" stroke-width="1.2"/>')
    for y in (10, 22, 34):
        ic.add(f'<rect x="20" y="{y}" width="24" height="8" rx="1.2" fill="#4A5457" stroke="#232829" stroke-width="0.8"/>')
        ic.add(f'<circle cx="40" cy="{y + 4}" r="1.4" fill="{LEAF_400}"/><path d="M23 {y + 4} H33" stroke="#7E898C" stroke-width="1.4"/>')
    gloss(ic, "M17 6 H31 V56 H19 Q17 56 17 54 Z", 0.25)
    return ic.svg()


# ---------------------------------------------------------------- apps
def window_frame(ic, x=6, y=8, w=52, h=44, title_col=None, body="#FFFFFF"):
    ic.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="{body}" stroke="{CHAR_900}" stroke-width="1.2"/>')
    t = ic.grad(lg([(0, "#6A645F"), (0.5, "#36322F"), (0.51, "#2A2725"), (1, "#1C1A19")]))
    ic.add(f'<path d="M{x} {y + 3} Q{x} {y} {x + 3} {y} H{x + w - 3} Q{x + w} {y} {x + w} {y + 3} V{y + 8} H{x} Z" fill="{t}"/>')
    ic.add(f'<rect x="{x}" y="{y + 7.2}" width="{w}" height="1.1" fill="{ORANGE_500}"/>')
    ic.add(f'<rect x="{x + w - 7}" y="{y + 2}" width="4.5" height="4.5" rx="1" fill="#FFFFFF" opacity="0.8"/>')


def terminal():
    ic = Icon()
    ic.shadow(32, 57, 24, 2.6)
    window_frame(ic, 6, 9, 52, 44, body=GRAPHITE_900)
    ic.add(f'<path d="M12 26 L19 31 L12 36" stroke="{LEAF_400}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    ic.add('<path d="M22 38 H32" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>')
    gloss(ic, "M7 18 H57 V28 Q32 33 7 26 Z", 0.18)
    return ic.svg()


def file_manager():
    ic = Icon()
    ic.shadow(32, 58, 26, 3)
    window_frame(ic, 4, 7, 50, 40, body="#F4F8F8")
    ic.add(f'<rect x="5" y="15" width="13" height="31" fill="{TEAL_100}"/>')
    for y in (19, 24, 29, 34):
        ic.add(f'<rect x="7" y="{y}" width="9" height="2.5" rx="1" fill="{TEAL_300}"/>')
    # small folder glyphs in the content area
    for (x, y) in ((22, 19), (36, 19), (22, 31)):
        f = ic.grad(lg([(0, "#FFE39A"), (1, HONEY_500)]))
        ic.add(f'<path d="M{x} {y + 2} H{x + 4} L{x + 5} {y + 3.5} H{x + 11} V{y + 10} H{x} Z" fill="{f}" stroke="{HONEY_700}" stroke-width="0.7"/>')
    # magnifier
    ic.add(f'<circle cx="45" cy="43" r="9" fill="#E8F7F9" fill-opacity="0.7" stroke="{GRAPHITE_800}" stroke-width="3"/>')
    ic.add(f'<path d="M51.5 49.5 L59 57" stroke="{HONEY_600}" stroke-width="5" stroke-linecap="round"/>')
    ic.add('<path d="M40 39 Q42 36.5 45.5 36.5" stroke="#FFFFFF" stroke-width="2" fill="none" stroke-linecap="round"/>')
    return ic.svg()


def browser():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    globe(ic, 30, 29, 24)
    ar = ic.grad(lg([(0, "#FFFFFF"), (1, "#E3E9EA")]))
    ic.add(f'<path d="M38 30 L38 56 L44 50 L48.5 59 L53 57 L48.6 48 L57 48 Z" fill="{ar}" stroke="{GRAPHITE_900}" stroke-width="1.6" stroke-linejoin="round"/>')
    return ic.svg()


def control_panel():
    ic = Icon()
    ic.shadow(32, 58, 25, 2.8)
    window_frame(ic, 6, 7, 52, 46, body="#F7FAFA")
    rows = [(20, HONEY_500, 0.65), (30, TEAL_500, 0.35), (40, LEAF_500, 0.8)]
    for y, col, pos in rows:
        ic.add(f'<rect x="12" y="{y - 1.5}" width="40" height="3" rx="1.5" fill="#D3DDDF"/>')
        ic.add(f'<rect x="12" y="{y - 1.5}" width="{40 * pos}" height="3" rx="1.5" fill="{col}"/>')
        k = ic.grad(lg([(0, "#FFFFFF"), (1, SILVER_300)]))
        ic.add(f'<circle cx="{12 + 40 * pos}" cy="{y}" r="4" fill="{k}" stroke="{darken(col, 0.3)}" stroke-width="1.2"/>')
    gear(ic, 50, 48, 10, SILVER_400, 9)
    return ic.svg()


def text_editor():
    ic = Icon()
    ic.shadow(30, 59, 18, 2.4)
    pad = ic.grad(lg([(0, "#FFFDF5"), (1, "#F2EBD3")]))
    ic.add(f'<rect x="11" y="8" width="38" height="50" rx="2" fill="{pad}" stroke="#8A7E5C" stroke-width="1.2"/>')
    top = ic.grad(lg([(0, "#5CC0C9"), (1, TEAL_700)]))
    ic.add(f'<rect x="11" y="6" width="38" height="7" rx="2" fill="{top}" stroke="{TEAL_900}" stroke-width="1.2"/>')
    for y in range(19, 54, 6):
        ic.add(f'<path d="M15 {y} H45" stroke="#C9D8E4" stroke-width="1.2"/>')
    ic.add(f'<path d="M15 19 H38 M15 25 H42 M15 31 H33" stroke="{GRAPHITE_600}" stroke-width="1.6" stroke-linecap="round"/>')
    # pencil
    ic.add('<g transform="rotate(40 44 40)">')
    pb = ic.grad(lg([(0, HONEY_400), (1, HONEY_600)], 0, 0, 1, 0))
    ic.add(f'<rect x="40" y="18" width="8" height="28" fill="{pb}" stroke="{HONEY_800}" stroke-width="1"/>')
    ic.add(f'<rect x="40" y="14" width="8" height="5" fill="#E88B8B" stroke="#8E3B3B" stroke-width="1"/>')
    ic.add('<path d="M40 46 L44 54 L48 46 Z" fill="#F1DDB6" stroke="#8A7E5C" stroke-width="1"/>')
    ic.add(f'<path d="M42.6 51 L44 54 L45.4 51 Z" fill="{GRAPHITE_800}"/>')
    ic.add('</g>')
    return ic.svg()


def calculator():
    ic = Icon()
    ic.shadow(32, 59, 18, 2.4)
    b = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
    ic.add(f'<rect x="13" y="5" width="38" height="53" rx="5" fill="{b}" stroke="#101415" stroke-width="1.2"/>')
    scr = ic.grad(lg([(0, "#E3F2D4"), (1, "#B9D6A3")]))
    ic.add(f'<rect x="17" y="9" width="30" height="11" rx="1.5" fill="{scr}" stroke="#3D4A33" stroke-width="0.8"/>')
    ic.add(f'<text x="44.5" y="18" text-anchor="end" font-family="DejaVu Sans Mono, monospace" font-size="8.5" font-weight="700" fill="#2F3B28">128</text>')
    keys = [(r, c) for r in range(4) for c in range(4)]
    for r, c in keys:
        col = HONEY_500 if c == 3 else ("#E9EEEF" if r < 3 else SILVER_300)
        if r == 3 and c == 3:
            col = TEAL_500
        k = ic.grad(lg([(0, lighten(col, 0.3)), (1, col)]))
        ic.add(f'<rect x="{17 + c * 7.6:.1f}" y="{24 + r * 8:.1f}" width="6.2" height="6.3" rx="1.2" fill="{k}" stroke="#101415" stroke-width="0.6"/>')
    gloss(ic, "M14 6 H50 V14 Q32 20 14 16 Z", 0.25)
    return ic.svg()


def image_viewer():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    ic.add('<g transform="rotate(-6 32 32)">')
    ic.add('<rect x="8" y="12" width="48" height="38" rx="1.5" fill="#FFFFFF" stroke="#7F9093" stroke-width="1.2"/>')
    sky = ic.grad(lg([(0, "#79C6EF"), (1, "#DDF2FB")]))
    ic.add(f'<rect x="12" y="16" width="40" height="27" fill="{sky}"/>')
    ic.add(f'<path d="M12 43 L23 29 L31 37 L37 31 L52 43 Z" fill="{LEAF_500}" stroke="{LEAF_700}" stroke-width="0.8"/>')
    ic.add(f'<circle cx="44" cy="23" r="3.6" fill="{HONEY_400}"/>')
    ic.add('</g>')
    return ic.svg()


def paint():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    pal = ic.grad(lg([(0, "#F7E3BE"), (1, "#D9B276")]))
    ic.add(f'<path d="M32 8 C50 8 60 18 58 30 C56.5 38 49 37 45 37 C40 37 39 41 41 45 C43.5 50 38 56 30 56 C15 56 5 46 5 32 C5 18 16 8 32 8 Z" fill="{pal}" stroke="#8A6A33" stroke-width="1.2"/>')
    for (x, y, c) in ((20, 22, RED_500), (32, 16, HONEY_500), (44, 21, LEAF_500), (15, 34, BLUE_500), (22, 45, PURPLE_500)):
        ic.add(f'<circle cx="{x}" cy="{y}" r="4.6" fill="{c}" stroke="{darken(c, 0.3)}" stroke-width="0.8"/>')
    ic.add('<g transform="rotate(38 46 40)">')
    ic.add(f'<rect x="43" y="22" width="6" height="26" rx="2" fill="{TEAL_600}" stroke="{TEAL_900}" stroke-width="1"/>')
    ic.add(f'<rect x="43" y="18" width="6" height="5" fill="{SILVER_300}" stroke="#6F7A7D" stroke-width="0.8"/>')
    ic.add(f'<path d="M43.5 18 Q46 8 48.5 18 Z" fill="{RED_500}" stroke="{RED_600}" stroke-width="0.8"/>')
    ic.add('</g>')
    return ic.svg()


def archive():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.8)
    top = ic.grad(lg([(0, "#E8C690"), (1, "#C99A55")]))
    ic.add(f'<path d="M8 20 L16 10 H48 L56 20 Z" fill="{top}" stroke="#7D5A25" stroke-width="1.2" stroke-linejoin="round"/>')
    body = ic.grad(lg([(0, "#E2BC80"), (1, "#B98A47")]))
    ic.add(f'<rect x="8" y="20" width="48" height="35" rx="1.5" fill="{body}" stroke="#7D5A25" stroke-width="1.2"/>')
    ic.add(f'<rect x="28" y="20" width="8" height="35" fill="{TEAL_500}" stroke="{TEAL_800}" stroke-width="0.8"/>')
    for y in range(22, 54, 4):
        ic.add(f'<path d="M29.5 {y} H34.5" stroke="#FFFFFF" stroke-width="1.4" opacity="0.85"/>')
    ic.add(f'<rect x="29" y="34" width="6" height="8" rx="1" fill="{SILVER_300}" stroke="#55676A" stroke-width="0.8"/>')
    gloss(ic, "M9 21 H55 V27 Q32 30 9 27 Z", 0.35)
    return ic.svg()


def pdf_viewer():
    return page(band=RED_500, label="PDF")


def media_player():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    c = ic.grad(rg([(0, "#FFE7A8"), (0.55, HONEY_500), (1, HONEY_700)], 0.4, 0.32, 0.75))
    ic.add(f'<circle cx="32" cy="31" r="25" fill="{c}" stroke="{HONEY_800}" stroke-width="1.3"/>')
    ic.add('<path d="M25 18 L46 31 L25 44 Z" fill="#FFFFFF" stroke="#9A5A0E" stroke-width="1.2" stroke-linejoin="round"/>')
    gloss(ic, "M10 26 A22 22 0 0 1 54 26 Q32 17 10 26 Z", 0.6)
    return ic.svg()


def remote_desktop():
    ic = Icon()
    ic.shadow(32, 59, 24, 2.6)
    monitor_body(ic, 4, 6, 44, 32)
    monitor_body(ic, 22, 22, 38, 26, stand=False)
    ic.add(f'<path d="M14 50 Q14 56 22 56 H30" stroke="{HONEY_500}" stroke-width="3" fill="none" stroke-linecap="round"/>')
    ic.add(f'<path d="M27 52 L31 56 L27 60" stroke="{HONEY_500}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return ic.svg()


def task_manager():
    ic = Icon()
    ic.shadow(32, 57, 24, 2.6)
    window_frame(ic, 6, 9, 52, 44, body=GRAPHITE_900)
    for x in range(10, 56, 6):
        ic.add(f'<path d="M{x} 18 V50" stroke="#2F4A4D" stroke-width="0.8"/>')
    for y in range(22, 52, 6):
        ic.add(f'<path d="M7 {y} H57" stroke="#2F4A4D" stroke-width="0.8"/>')
    ic.add(f'<path d="M8 44 L16 40 L22 42 L28 30 L34 34 L40 24 L46 30 L56 20" stroke="{LEAF_400}" stroke-width="2.4" fill="none" stroke-linejoin="round"/>')
    ic.add(f'<path d="M8 48 L18 47 L26 45 L36 46 L46 43 L56 44" stroke="{HONEY_400}" stroke-width="2" fill="none" stroke-linejoin="round"/>')
    return ic.svg()


def screenshot():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    ic.add(f'<rect x="5" y="9" width="50" height="38" rx="2" fill="none" stroke="{TEAL_600}" stroke-width="2" stroke-dasharray="5 3"/>')
    b = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
    ic.add(f'<path d="M22 28 H28 L31 24 H42 L45 28 H52 Q55 28 55 31 V52 Q55 55 52 55 H22 Q19 55 19 52 V31 Q19 28 22 28 Z" fill="{b}" stroke="#101415" stroke-width="1.2"/>')
    lens = ic.grad(rg([(0, "#9FE3EA"), (0.5, TEAL_600), (1, TEAL_950)], 0.4, 0.35, 0.7))
    ic.add(f'<circle cx="37" cy="41" r="9" fill="{lens}" stroke="{SILVER_300}" stroke-width="2"/>')
    ic.add('<circle cx="34" cy="38" r="2.4" fill="#FFFFFF" opacity="0.8"/>')
    ic.add(f'<rect x="46" y="31" width="5" height="3" rx="1" fill="{HONEY_400}"/>')
    return ic.svg()


def search_icon():
    ic = Icon()
    ic.shadow(32, 59, 20, 2.4)
    lens = ic.grad(rg([(0, "#FFFFFF", 0.95), (0.7, TEAL_100, 0.85), (1, TEAL_200, 0.9)], 0.4, 0.35, 0.65))
    ic.add(f'<circle cx="26" cy="26" r="17" fill="{lens}" stroke="{GRAPHITE_800}" stroke-width="5"/>')
    h = ic.grad(lg([(0, HONEY_400), (1, HONEY_700)], 0, 0, 1, 1))
    ic.add(f'<path d="M38.5 38.5 L55 55" stroke="{GRAPHITE_900}" stroke-width="10" stroke-linecap="round"/>')
    ic.add(f'<path d="M39.5 39.5 L54 54" stroke="{h}" stroke-width="7" stroke-linecap="round"/>')
    ic.add('<path d="M15 22 Q18 14 27 13" stroke="#FFFFFF" stroke-width="3" fill="none" stroke-linecap="round"/>')
    return ic.svg()


def run_icon():
    ic = Icon()
    ic.shadow(32, 57, 24, 2.6)
    window_frame(ic, 6, 11, 52, 40)
    ic.add(f'<rect x="11" y="27" width="34" height="9" rx="2" fill="#FFFFFF" stroke="{TEAL_700}" stroke-width="1.2"/>')
    ic.add(f'<path d="M14 31.5 H30" stroke="{GRAPHITE_600}" stroke-width="1.6"/>')
    ic.add(f'<path d="M44 26 H52 L48 21 M52 26 L48 31" stroke="{HONEY_600}" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return ic.svg()


def help_icon():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    c = ic.grad(rg([(0, "#9FE3EA"), (0.55, TEAL_500), (1, TEAL_900)], 0.4, 0.32, 0.75))
    ic.add(f'<circle cx="32" cy="31" r="25" fill="{c}" stroke="{TEAL_950}" stroke-width="1.3"/>')
    ic.add('<text x="32" y="44" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="36" font-weight="700" fill="#FFFFFF">?</text>')
    gloss(ic, "M10 26 A22 22 0 0 1 54 26 Q32 17 10 26 Z", 0.6)
    return ic.svg()


def info_badge(ic, cx, cy, r=9):
    c = ic.grad(rg([(0, "#9FE3EA"), (1, TEAL_700)], 0.4, 0.3, 0.8))
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{c}" stroke="#FFFFFF" stroke-width="1.6"/>')
    ic.add(f'<text x="{cx}" y="{cy + r * 0.42:.1f}" text-anchor="middle" font-family="Noto Serif, DejaVu Serif, serif" font-size="{r * 1.35:.1f}" font-weight="700" font-style="italic" fill="#FFFFFF">i</text>')


def system_info():
    ic = Icon()
    ic.shadow(30, 58.5, 20, 2.6)
    monitor_body(ic, 4, 8, 48, 34)
    info_badge(ic, 49, 46, 11)
    return ic.svg()


def speaker(ic, x=6, y=14, s=1.0, waves=True):
    b = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
    ic.add(f'<path transform="translate({x} {y}) scale({s})" d="M2 12 H12 L26 1 V39 L12 28 H2 Q0 28 0 26 V14 Q0 12 2 12 Z" fill="{b}" stroke="#101415" stroke-width="1.2" stroke-linejoin="round"/>')
    if waves:
        for i, r in enumerate((8, 15, 22)):
            col = (TEAL_400, TEAL_500, TEAL_600)[i]
            ic.add(f'<path transform="translate({x} {y}) scale({s})" d="M{30 + i * 2} {20 - r} A{r} {r} 0 0 1 {30 + i * 2} {20 + r}" fill="none" stroke="{col}" stroke-width="3.6" stroke-linecap="round"/>')


def sound():
    ic = Icon()
    ic.shadow(32, 58, 22, 2.4)
    speaker(ic, 6, 12, 1.0)
    return ic.svg()


def display_settings():
    ic = Icon()
    ic.shadow(32, 58.5, 20, 2.6)

    def scr(ic, sx, sy, sw, sh):
        cols = [RED_500, HONEY_500, LEAF_500, TEAL_500, BLUE_500, PURPLE_500]
        w = sw / len(cols)
        for i, c in enumerate(cols):
            ic.add(f'<rect x="{sx + i * w:.2f}" y="{sy}" width="{w + 0.3:.2f}" height="{sh}" fill="{c}"/>')
    monitor_body(ic, screen=scr)
    return ic.svg()


def wallpaper_settings():
    ic = Icon()
    ic.shadow(32, 58.5, 20, 2.6)

    def scr(ic, sx, sy, sw, sh):
        sky = ic.grad(rg([(0, "#E07A1C"), (0.5, "#5A2A0C"), (1, "#0E0B0A")], 0.78, 0.15, 0.95))
        ic.add(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{sky}"/>')
        ic.add(f'<path d="M{sx} {sy + sh * 0.75} Q{sx + sw * 0.5} {sy + sh * 0.45} {sx + sw} {sy + sh * 0.55}" stroke="#FFD39A" stroke-width="1.6" fill="none" opacity="0.85"/>')
    monitor_body(ic, screen=scr)
    return ic.svg()


def appearance():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    window_frame(ic, 4, 6, 44, 34, body="#F7FAFA")
    for i, c in enumerate((TEAL_500, HONEY_500, LEAF_500)):
        ic.add(f'<rect x="{9 + i * 12}" y="20" width="9" height="14" rx="1.5" fill="{c}" stroke="{darken(c, 0.3)}" stroke-width="0.8"/>')
    ic.add('<g transform="rotate(35 46 44)">')
    ic.add(f'<rect x="43" y="30" width="7" height="24" rx="2" fill="{HONEY_600}" stroke="{HONEY_800}" stroke-width="1"/>')
    ic.add(f'<rect x="43" y="26" width="7" height="5" fill="{SILVER_300}" stroke="#6F7A7D" stroke-width="0.8"/>')
    ic.add(f'<path d="M43.5 26 Q46.5 14 49.5 26 Z" fill="{TEAL_500}" stroke="{TEAL_800}" stroke-width="0.8"/>')
    ic.add('</g>')
    return ic.svg()


def keyboard():
    ic = Icon()
    ic.shadow(32, 54, 28, 3)
    b = ic.grad(lg([(0, SILVER_100), (1, SILVER_300)]))
    ic.add(f'<path d="M6 22 H58 Q61 22 61 25 V47 Q61 50 58 50 H6 Q3 50 3 47 V25 Q3 22 6 22 Z" fill="{b}" stroke="#55676A" stroke-width="1.2"/>')
    for r in range(3):
        for c in range(10):
            x = 7 + c * 5.1 + (r * 1.6)
            if x > 55:
                continue
            ic.add(f'<rect x="{x:.1f}" y="{26 + r * 6}" width="4.2" height="4.6" rx="0.8" fill="#FFFFFF" stroke="#8A9497" stroke-width="0.6"/>')
    ic.add(f'<rect x="17" y="44" width="30" height="3.6" rx="0.8" fill="#FFFFFF" stroke="#8A9497" stroke-width="0.6"/>')
    ic.add(f'<rect x="51" y="44" width="6" height="3.6" rx="0.8" fill="{HONEY_400}" stroke="{HONEY_700}" stroke-width="0.6"/>')
    return ic.svg()


def mouse():
    ic = Icon()
    ic.shadow(32, 59, 16, 2.4)
    ic.add(f'<path d="M32 14 Q32 6 40 6 Q50 6 50 2" stroke="{GRAPHITE_700}" stroke-width="2" fill="none"/>')
    b = ic.grad(lg([(0, "#FFFFFF"), (0.6, SILVER_200), (1, SILVER_400)], 0, 0, 1, 1))
    ic.add(f'<path d="M32 14 C46 14 49 26 49 37 C49 49 42 57 32 57 C22 57 15 49 15 37 C15 26 18 14 32 14 Z" fill="{b}" stroke="#55676A" stroke-width="1.3"/>')
    ic.add('<path d="M32 14 V31 M15.5 31 Q32 35 48.5 31" stroke="#8A9497" stroke-width="1.1" fill="none"/>')
    ic.add(f'<rect x="30" y="19" width="4" height="8" rx="2" fill="{TEAL_500}" stroke="{TEAL_800}" stroke-width="0.8"/>')
    gloss(ic, "M20 30 C20 22 24 16 31 15.5 V30 Z", 0.6)
    return ic.svg()


def power():
    ic = Icon()
    ic.shadow(32, 55, 26, 2.8)
    b = ic.grad(lg([(0, SILVER_100), (1, SILVER_400)]))
    ic.add(f'<rect x="6" y="18" width="46" height="28" rx="4" fill="{b}" stroke="#55676A" stroke-width="1.3"/>')
    ic.add(f'<rect x="52" y="26" width="5" height="12" rx="1.5" fill="{SILVER_400}" stroke="#55676A" stroke-width="1"/>')
    g = ic.grad(lg([(0, LEAF_300), (1, LEAF_600)]))
    ic.add(f'<rect x="10" y="22" width="30" height="20" rx="2" fill="{g}"/>')
    ic.add(f'<path d="M30 21 L22 33 H29 L26 44 L37 30 H30 L33 21 Z" fill="{HONEY_300}" stroke="{HONEY_800}" stroke-width="1" stroke-linejoin="round"/>')
    gloss(ic, "M7 19 H51 V27 Q29 31 7 27 Z", 0.5)
    return ic.svg()


def printer():
    ic = Icon()
    ic.shadow(32, 58, 26, 3)
    ic.add('<rect x="16" y="6" width="32" height="20" fill="#FFFFFF" stroke="#7F9093" stroke-width="1.1"/>')
    ic.add('<path d="M20 12 H44 M20 16 H40" stroke="#B9C5C7" stroke-width="1.4"/>')
    b = ic.grad(lg([(0, SILVER_100), (0.5, SILVER_300), (1, "#7E8A8D")]))
    ic.add(f'<path d="M8 24 H56 Q59 24 59 27 V45 Q59 48 56 48 H8 Q5 48 5 45 V27 Q5 24 8 24 Z" fill="{b}" stroke="#55676A" stroke-width="1.3"/>')
    ic.add(f'<rect x="14" y="40" width="36" height="16" fill="#FFFFFF" stroke="#7F9093" stroke-width="1.1"/>')
    ic.add('<path d="M18 46 H44 M18 50 H38" stroke="#B9C5C7" stroke-width="1.4"/>')
    ic.add(f'<circle cx="51" cy="31" r="1.8" fill="{LEAF_400}" stroke="{LEAF_800}" stroke-width="0.6"/>')
    gloss(ic, "M6 25 H58 V31 Q32 34 6 31 Z", 0.5)
    return ic.svg()


def scanner():
    ic = Icon()
    ic.shadow(32, 54, 28, 3)
    b = ic.grad(lg([(0, SILVER_100), (1, "#7E8A8D")]))
    ic.add(f'<path d="M5 30 H59 V46 Q59 49 56 49 H8 Q5 49 5 46 Z" fill="{b}" stroke="#55676A" stroke-width="1.3"/>')
    lid = ic.grad(lg([(0, GRAPHITE_600), (1, GRAPHITE_900)]))
    ic.add(f'<path d="M8 18 H56 L59 30 H5 Z" fill="{lid}" stroke="#101415" stroke-width="1.2"/>')
    ic.add(f'<rect x="9" y="33" width="46" height="3" fill="{TEAL_300}"/>')
    ic.add(f'<circle cx="52" cy="42" r="1.8" fill="{LEAF_400}"/>')
    return ic.svg()


def people(ic, x=0, y=0, s=1.0):
    for (cx, col, sc) in ((22, TEAL_500, 1.0), (40, HONEY_500, 0.92)):
        hb = ic.grad(rg([(0, "#FCE6CF"), (1, "#D9A97C")], 0.4, 0.35, 0.7))
        bd = ic.grad(lg([(0, lighten(col, 0.25)), (1, darken(col, 0.15))]))
        ic.add(f'<g transform="translate({x} {y}) scale({s})">'
               f'<path d="M{cx - 15 * sc} 56 C{cx - 15 * sc} 42 {cx - 9 * sc} 36 {cx} 36 C{cx + 9 * sc} 36 {cx + 15 * sc} 42 {cx + 15 * sc} 56 Z" fill="{bd}" stroke="{darken(col, 0.4)}" stroke-width="1.2"/>'
               f'<circle cx="{cx}" cy="{25 - (1 - sc) * 6}" r="{10 * sc}" fill="{hb}" stroke="#8A5E3B" stroke-width="1.1"/></g>')


def users():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    people(ic)
    return ic.svg()


def user_single():
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6)
    hb = ic.grad(rg([(0, "#FCE6CF"), (1, "#D9A97C")], 0.4, 0.35, 0.7))
    bd = ic.grad(lg([(0, TEAL_400), (1, TEAL_700)]))
    ic.add(f'<path d="M12 58 C12 41 20 35 32 35 C44 35 52 41 52 58 Z" fill="{bd}" stroke="{TEAL_900}" stroke-width="1.2"/>')
    ic.add(f'<circle cx="32" cy="21" r="13" fill="{hb}" stroke="#8A5E3B" stroke-width="1.1"/>')
    return ic.svg()


def clock(ic, cx, cy, r):
    f = ic.grad(rg([(0, "#FFFFFF"), (1, "#DDE5E6")], 0.4, 0.35, 0.75))
    rim = ic.grad(lg([(0, TEAL_400), (1, TEAL_800)], 0, 0, 1, 1))
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{rim}" stroke="{TEAL_950}" stroke-width="1.2"/>')
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="{r * 0.82:.2f}" fill="{f}"/>')
    for i in range(12):
        import math
        a = math.pi * 2 * i / 12
        r1, r2 = r * 0.68, r * 0.76
        ic.add(f'<path d="M{cx + r1 * math.cos(a):.2f} {cy + r1 * math.sin(a):.2f} L{cx + r2 * math.cos(a):.2f} {cy + r2 * math.sin(a):.2f}" stroke="{GRAPHITE_700}" stroke-width="{1.4 if i % 3 == 0 else 0.8}"/>')
    ic.add(f'<path d="M{cx} {cy} L{cx} {cy - r * 0.55:.2f}" stroke="{GRAPHITE_900}" stroke-width="2.2" stroke-linecap="round"/>')
    ic.add(f'<path d="M{cx} {cy} L{cx + r * 0.42:.2f} {cy + r * 0.12:.2f}" stroke="{GRAPHITE_900}" stroke-width="2.2" stroke-linecap="round"/>')
    ic.add(f'<circle cx="{cx}" cy="{cy}" r="1.6" fill="{HONEY_600}"/>')


def datetime_icon():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    cal = ic.grad(lg([(0, "#FFFFFF"), (1, "#E3E9EA")]))
    ic.add(f'<rect x="4" y="10" width="36" height="40" rx="3" fill="{cal}" stroke="#7F9093" stroke-width="1.2"/>')
    t = ic.grad(lg([(0, "#F08A6B"), (1, RED_600)]))
    ic.add(f'<path d="M4 13 Q4 10 7 10 H37 Q40 10 40 13 V20 H4 Z" fill="{t}" stroke="#8E241A" stroke-width="1"/>')
    ic.add(f'<text x="22" y="42" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="19" font-weight="700" fill="{GRAPHITE_800}">18</text>')
    clock(ic, 44, 42, 16)
    return ic.svg()


def programs():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.8)
    # open box with a disc and a leaf peeking out
    optical_disc = ic.grad(rg([(0, "#FFFFFF"), (0.5, "#CFE8E3"), (0.8, "#EBDDF3"), (1, "#C9D4D7")], 0.42, 0.38, 0.7))
    ic.add(f'<circle cx="32" cy="20" r="14" fill="{optical_disc}" stroke="#7F9093" stroke-width="1.1"/>')
    ic.add('<circle cx="32" cy="20" r="3" fill="#FFFFFF" stroke="#7F9093" stroke-width="0.9"/>')
    side = ic.grad(lg([(0, TEAL_400), (1, TEAL_700)]))
    front = ic.grad(lg([(0, "#5CC0C9"), (1, TEAL_600)]))
    ic.add(f'<path d="M8 28 L32 22 L56 28 L56 50 L32 58 L8 50 Z" fill="{side}" stroke="{TEAL_950}" stroke-width="1.2" stroke-linejoin="round"/>')
    ic.add(f'<path d="M8 28 L32 35 L32 58 L8 50 Z" fill="{front}" stroke="{TEAL_950}" stroke-width="1.2" stroke-linejoin="round"/>')
    ic.add(f'<path d="M32 35 L56 28 L56 50 L32 58 Z" fill="{TEAL_700}" stroke="{TEAL_950}" stroke-width="1.2" stroke-linejoin="round"/>')
    ic.add(f'<path d="M8 28 L2 36 L26 43 L32 35 Z" fill="#7CD0D7" stroke="{TEAL_950}" stroke-width="1.1" stroke-linejoin="round"/>')
    ic.add(f'<path d="M56 28 L62 36 L38 43 L32 35 Z" fill="{TEAL_400}" stroke="{TEAL_950}" stroke-width="1.1" stroke-linejoin="round"/>')
    ic.add(f'<rect x="13" y="42" width="13" height="7" rx="1" fill="{HONEY_400}" stroke="{HONEY_800}" stroke-width="0.8" transform="skewY(17) translate(0 -9)"/>')
    return ic.svg()


def shield(ic, col_top, col_bot, x=12, y=6, s=1.0):
    g = ic.grad(lg([(0, col_top), (1, col_bot)]))
    ic.add(f'<path transform="translate({x} {y}) scale({s})" d="M20 0 C28 4 34 5 40 5 V22 C40 36 31 46 20 52 C9 46 0 36 0 22 V5 C6 5 12 4 20 0 Z" fill="{g}" stroke="{darken(col_bot, 0.35)}" stroke-width="1.3" stroke-linejoin="round"/>')
    gl = ic.grad(lg([(0, "#FFFFFF", 0.55), (1, "#FFFFFF", 0)]))
    ic.add(f'<path transform="translate({x} {y}) scale({s})" d="M20 2 C27 5.5 32 6.5 38 7 V20 Q20 26 2 30 V7 C8 6.5 13 5.5 20 2 Z" fill="{gl}"/>')


def updates():
    ic = Icon()
    ic.shadow(32, 59, 20, 2.6)
    shield(ic, "#7CD0D7", TEAL_700)
    ic.add('<path d="M23 31 A9 9 0 1 0 26 24" stroke="#FFFFFF" stroke-width="3.6" fill="none" stroke-linecap="round"/>')
    ic.add('<path d="M21 20 L27 24.5 L21 28 Z" fill="#FFFFFF" transform="rotate(-20 24 24)"/>')
    ic.add(f'<circle cx="46" cy="47" r="9" fill="{HONEY_500}" stroke="#FFFFFF" stroke-width="1.6"/>')
    ic.add('<path d="M46 42 V52 M42 48 L46 52 L50 48" stroke="#FFFFFF" stroke-width="2.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return ic.svg()


def firewall():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    # brick wall behind a shield
    for r in range(4):
        for c in range(4):
            x = 4 + c * 14 + (7 if r % 2 else 0)
            if x > 50:
                x -= 56
            ic.add(f'<rect x="{max(4, x)}" y="{30 + r * 7}" width="{min(13, 60 - max(4, x))}" height="6" fill="#C9694F" stroke="#7A3626" stroke-width="0.8"/>')
    shield(ic, "#9EE48A", LEAF_700, 16, 4, 0.8)
    ic.add('<path d="M26 26 L31 31 L40 20" stroke="#FFFFFF" stroke-width="3.6" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return ic.svg()


def restore():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    clock(ic, 34, 32, 22)
    ic.add(f'<path d="M10 22 A26 26 0 0 1 22 8" stroke="{HONEY_600}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    ic.add(f'<path d="M4 18 L11 26 L16 16 Z" fill="{HONEY_600}"/>')
    return ic.svg()


def cleanup():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    ic.add('<g transform="rotate(-30 32 32)">')
    h = ic.grad(lg([(0, "#C99A55"), (1, "#8A6224")], 0, 0, 1, 0))
    ic.add(f'<rect x="29" y="0" width="6" height="34" rx="2" fill="{h}" stroke="#5C3F14" stroke-width="1"/>')
    br = ic.grad(lg([(0, HONEY_300), (1, HONEY_700)]))
    ic.add(f'<path d="M20 34 H44 L50 60 H14 Z" fill="{br}" stroke="{HONEY_800}" stroke-width="1.2" stroke-linejoin="round"/>')
    for x in range(18, 48, 4):
        ic.add(f'<path d="M{x + 1} 38 L{x - 1 + (x - 32) * 0.2:.1f} 58" stroke="{HONEY_800}" stroke-width="0.9" opacity="0.7"/>')
    ic.add(f'<rect x="19" y="32" width="26" height="5" rx="1" fill="{TEAL_500}" stroke="{TEAL_900}" stroke-width="1"/>')
    ic.add('</g>')
    for (x, y, r) in ((50, 14, 2.6), (56, 22, 1.8), (46, 8, 1.6)):
        ic.add(f'<path d="M{x} {y - r * 2} L{x + r * 0.5} {y - r * 0.5} L{x + r * 2} {y} L{x + r * 0.5} {y + r * 0.5} L{x} {y + r * 2} L{x - r * 0.5} {y + r * 0.5} L{x - r * 2} {y} L{x - r * 0.5} {y - r * 0.5} Z" fill="{HONEY_400}"/>')
    return ic.svg()


def disks():
    ic = Icon()
    ic.shadow(32, 54, 26, 3)
    top = ic.grad(lg([(0, "#F4F6F7"), (1, SILVER_300)]))
    ic.add(f'<path d="M8 26 L14 18 H50 L56 26 Z" fill="{top}" stroke="#6F7A7D" stroke-width="1.2" stroke-linejoin="round"/>')
    body = ic.grad(lg([(0, SILVER_200), (1, "#8A9497")]))
    ic.add(f'<rect x="8" y="26" width="48" height="22" rx="2.5" fill="{body}" stroke="#5E686B" stroke-width="1.2"/>')
    # pie chart
    ic.add(f'<circle cx="24" cy="37" r="8" fill="{TEAL_200}" stroke="{TEAL_800}" stroke-width="1"/>')
    ic.add(f'<path d="M24 37 V29 A8 8 0 0 1 31.6 39.5 Z" fill="{HONEY_500}" stroke="{HONEY_800}" stroke-width="0.8"/>')
    ic.add(f'<circle cx="50" cy="42" r="2" fill="{LEAF_400}" stroke="{LEAF_800}" stroke-width="0.8"/>')
    return ic.svg()


def bluetooth():
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6)
    g = ic.grad(lg([(0, "#5FA4E6"), (1, "#1E5AA8")]))
    ic.add(f'<rect x="12" y="4" width="40" height="54" rx="20" fill="{g}" stroke="#123A70" stroke-width="1.3"/>')
    ic.add('<path d="M22 21 L42 39 L32 48 V12 L42 21 L22 39" stroke="#FFFFFF" stroke-width="3.4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    gloss(ic, "M14 22 Q14 6 32 6 Q50 6 50 22 Q32 28 14 22 Z", 0.45)
    return ic.svg()


def network_settings():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    globe(ic, 30, 28, 22)
    plug = ic.grad(lg([(0, SILVER_100), (1, SILVER_400)]))
    ic.add(f'<rect x="38" y="38" width="20" height="14" rx="2.5" fill="{plug}" stroke="#55676A" stroke-width="1.2"/>')
    ic.add(f'<rect x="42" y="52" width="12" height="6" fill="{GRAPHITE_700}"/>')
    for x in (42, 46, 50):
        ic.add(f'<rect x="{x}" y="34" width="2.6" height="5" fill="{HONEY_500}" stroke="{HONEY_800}" stroke-width="0.5"/>')
    return ic.svg()


def language():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    globe(ic, 28, 30, 22)
    b = ic.grad(lg([(0, "#FFFFFF"), (1, "#E3E9EA")]))
    ic.add(f'<path d="M36 34 H58 Q61 34 61 37 V51 Q61 54 58 54 H47 L41 59 V54 H39 Q36 54 36 51 Z" fill="{b}" stroke="{TEAL_700}" stroke-width="1.2" stroke-linejoin="round"/>')
    ic.add(f'<text x="48.5" y="49" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="12" font-weight="700" fill="{TEAL_700}">Aă</text>')
    return ic.svg()


def accessibility():
    ic = Icon()
    ic.shadow(32, 59, 20, 2.6)
    c = ic.grad(rg([(0, "#9FE3EA"), (0.55, TEAL_500), (1, TEAL_900)], 0.4, 0.32, 0.75))
    ic.add(f'<circle cx="32" cy="31" r="25" fill="{c}" stroke="{TEAL_950}" stroke-width="1.3"/>')
    ic.add('<circle cx="32" cy="16" r="4" fill="#FFFFFF"/>')
    ic.add('<path d="M17 23 Q32 27 47 23 M32 25 V36 M32 36 L25 49 M32 36 L39 49" stroke="#FFFFFF" stroke-width="4" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    gloss(ic, "M10 26 A22 22 0 0 1 54 26 Q32 17 10 26 Z", 0.4)
    return ic.svg()


def notifications():
    ic = Icon()
    ic.shadow(32, 59, 18, 2.6)
    g = ic.grad(lg([(0, "#FFE7A8"), (1, HONEY_600)]))
    ic.add(f'<path d="M32 6 C42 6 47 13 47 23 V36 L53 44 V47 H11 V44 L17 36 V23 C17 13 22 6 32 6 Z" fill="{g}" stroke="{HONEY_800}" stroke-width="1.3" stroke-linejoin="round"/>')
    ic.add(f'<path d="M26 47 A6 6 0 0 0 38 47 Z" fill="{HONEY_700}" stroke="{HONEY_800}" stroke-width="1.2"/>')
    gloss(ic, "M20 22 C20 13 25 9 32 9 V30 Q26 30 20 33 Z", 0.5)
    return ic.svg()


def taskbar_settings():
    ic = Icon()
    ic.shadow(32, 57, 26, 2.6)
    window_frame(ic, 4, 8, 56, 42, body="#EEF5F6")
    t = ic.grad(lg([(0, "#59BCC5"), (1, "#146570")]))
    ic.add(f'<rect x="5" y="41" width="54" height="8" fill="{t}"/>')
    hb = ic.grad(lg([(0, "#FFE2A6"), (1, "#E3901F")]))
    ic.add(f'<rect x="7" y="42.5" width="12" height="5" rx="2.5" fill="{hb}" stroke="{HONEY_800}" stroke-width="0.6"/>')
    for x in (22, 32):
        ic.add(f'<rect x="{x}" y="42.5" width="8.5" height="5" rx="1" fill="#FFFFFF" opacity="0.35"/>')
    return ic.svg()


def window_settings():
    ic = Icon()
    ic.shadow(32, 57, 24, 2.6)
    window_frame(ic, 14, 6, 44, 34, body="#F7FAFA")
    window_frame(ic, 4, 20, 44, 34, body="#FFFFFF")
    return ic.svg()


def session_startup():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    c = ic.grad(rg([(0, "#C9F09C"), (0.55, LEAF_500), (1, LEAF_800)], 0.4, 0.32, 0.75))
    ic.add(f'<circle cx="32" cy="31" r="25" fill="{c}" stroke="{LEAF_800}" stroke-width="1.3"/>')
    ic.add('<path d="M24 31 A10 10 0 1 0 40 31" stroke="#FFFFFF" stroke-width="4" fill="none" stroke-linecap="round" transform="rotate(180 32 34)"/>')
    ic.add('<path d="M32 17 V31" stroke="#FFFFFF" stroke-width="4" stroke-linecap="round"/>')
    gloss(ic, "M10 26 A22 22 0 0 1 54 26 Q32 17 10 26 Z", 0.45)
    return ic.svg()


def default_apps():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    for (rot, c) in ((-14, HONEY_500), (0, LEAF_500), (14, TEAL_500)):
        g = ic.grad(lg([(0, lighten(c, 0.3)), (1, darken(c, 0.12))]))
        ic.add(f'<g transform="rotate({rot} 32 56)"><rect x="19" y="10" width="26" height="36" rx="4" fill="{g}" stroke="{darken(c, 0.4)}" stroke-width="1.1"/>'
               f'<rect x="23" y="15" width="18" height="3" rx="1.5" fill="#FFFFFF" opacity="0.6"/></g>')
    ic.add(f'<circle cx="46" cy="46" r="10" fill="{TEAL_600}" stroke="#FFFFFF" stroke-width="1.8"/>')
    ic.add('<path d="M41 46 L45 50 L52 41" stroke="#FFFFFF" stroke-width="3.2" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    return ic.svg()


def settings_editor():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    gear(ic, 26, 28, 20, SILVER_400, 10)
    gear(ic, 46, 46, 12, HONEY_500, 8)
    return ic.svg()


def screensaver():
    ic = Icon()
    ic.shadow(32, 58.5, 20, 2.6)

    def scr(ic, sx, sy, sw, sh):
        sky = ic.grad(lg([(0, "#14234A"), (1, "#081227")]))
        ic.add(f'<rect x="{sx}" y="{sy}" width="{sw}" height="{sh}" fill="{sky}"/>')
        ic.add(f'<circle cx="{sx + sw * 0.7}" cy="{sy + sh * 0.4}" r="{sh * 0.28}" fill="{HONEY_200}"/>')
        ic.add(f'<circle cx="{sx + sw * 0.76}" cy="{sy + sh * 0.33}" r="{sh * 0.26}" fill="#14234A"/>')
        for (a, b) in ((0.2, 0.3), (0.35, 0.6), (0.15, 0.75), (0.45, 0.2)):
            ic.add(f'<circle cx="{sx + sw * a}" cy="{sy + sh * b}" r="0.9" fill="#FFFFFF"/>')
    monitor_body(ic, screen=scr)
    return ic.svg()


def removable_settings():
    ic = Icon()
    ic.add(usb().split('<defs>', 1)[1].split('</svg>')[0].replace('</defs>', '', 1) if False else '')
    return usb()


def cards():
    ic = Icon()
    ic.shadow(32, 59, 24, 2.6)
    for i, (rot, col) in enumerate(((-16, "#FFFFFF"), (0, "#FFFFFF"), (16, "#FFFFFF"))):
        ic.add(f'<g transform="rotate({rot} 32 52)"><rect x="19" y="10" width="26" height="38" rx="3" fill="{col}" stroke="#7F9093" stroke-width="1.2"/></g>')
    ic.add(f'<g transform="rotate(16 32 52)"><path d="M32 21 C29 16 22 18 24 24 C25.5 28 32 33 32 33 C32 33 38.5 28 40 24 C42 18 35 16 32 21 Z" fill="{RED_500}"/>'
           f'<text x="23" y="45" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="9" font-weight="700" fill="{RED_600}">A</text></g>')
    return ic.svg()


def mines():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    for r in range(3):
        for c in range(3):
            raised = (r + c) % 2 == 0
            g = ic.grad(lg([(0, "#FFFFFF" if raised else "#D3DDDF"), (1, SILVER_300 if raised else "#E9EEEF")]))
            ic.add(f'<rect x="{6 + c * 17.5}" y="{6 + r * 17.5}" width="16.5" height="16.5" rx="2" fill="{g}" stroke="#7F9093" stroke-width="1"/>')
    ic.add(f'<circle cx="32" cy="32" r="6.5" fill="{GRAPHITE_900}"/><path d="M32 22 V42 M22 32 H42 M25 25 L39 39 M39 25 L25 39" stroke="{GRAPHITE_900}" stroke-width="2"/>')
    ic.add('<circle cx="30" cy="30" r="1.8" fill="#FFFFFF"/>')
    ic.add(f'<text x="14.2" y="20.5" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="12" font-weight="700" fill="{BLUE_600}">1</text>')
    ic.add(f'<text x="49.2" y="55.5" text-anchor="middle" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="12" font-weight="700" fill="{LEAF_700}">2</text>')
    return ic.svg()


def charmap():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    window_frame(ic, 6, 8, 52, 44)
    for i, ch in enumerate("ĂȘȚ"):
        ic.add(f'<text x="{17 + i * 15}" y="40" text-anchor="middle" font-family="Noto Serif, DejaVu Serif, serif" font-size="17" font-weight="700" fill="{TEAL_700}">{ch}</text>')
    return ic.svg()


def installer():
    ic = Icon()
    ic.shadow(32, 59, 24, 2.8)
    d = ic.grad(rg([(0, "#FFFFFF"), (0.4, "#DDE7EA"), (0.6, "#C7E7E0"), (0.8, "#F5E7C6"), (1, "#C9D4D7")], 0.42, 0.38, 0.65))
    ic.add(f'<circle cx="26" cy="30" r="22" fill="{d}" stroke="#7F9093" stroke-width="1.2"/>')
    ic.add('<circle cx="26" cy="30" r="5" fill="#FFFFFF" stroke="#7F9093" stroke-width="1"/>')
    hd = hdd_small(ic, 30, 36)
    orb_mark(ic, 49, 14, 11)
    return ic.svg()


def hdd_small(ic, x, y):
    body = ic.grad(lg([(0, SILVER_200), (1, "#8A9497")]))
    ic.add(f'<rect x="{x}" y="{y}" width="30" height="18" rx="2" fill="{body}" stroke="#5E686B" stroke-width="1.2"/>')
    ic.add(f'<circle cx="{x + 25}" cy="{y + 13}" r="1.8" fill="{LEAF_400}"/>')
    ic.add(f'<path d="M{x + 4} {y + 6} H{x + 20} M{x + 4} {y + 10} H{x + 16}" stroke="#E9EEEF" stroke-width="1.4"/>')


def welcome():
    ic = Icon()
    ic.shadow(32, 59, 22, 2.6)
    orb_mark(ic, 32, 31, 25, sparkle=True)
    return ic.svg()


def start_here():
    """Menu / Start button logo: the WinLow XP orb."""
    from logo import orb_svg
    return orb_svg(64, shadow=False, sparkle=False, uid="sh")


def domain():
    ic = Icon()
    ic.shadow(32, 59, 24, 2.6)
    s = server()
    ic.add('<g transform="translate(-8 0) scale(0.85)">' + s.split('</defs>', 1)[1].rsplit('</svg>', 1)[0] + '</g>')
    ic.defs.append(s.split('<defs>', 1)[1].split('</defs>', 1)[0])
    people(ic, 22, 14, 0.7)
    return ic.svg()


def wine_icon():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    window_frame(ic, 4, 8, 48, 40)
    glass = ic.grad(lg([(0, "#FFFFFF", 0.9), (1, "#DCEFF1", 0.8)], 0, 0, 1, 0))
    wine_c = ic.grad(lg([(0, "#C2364A"), (1, "#7A1426")]))
    # glass bowl, stem, foot (generic wine glass)
    ic.add(f'<path d="M36 22 H58 Q58 36 47 39 Q36 36 36 22 Z" fill="{glass}" stroke="#55676A" stroke-width="1.2"/>')
    ic.add(f'<path d="M37.2 28 H56.8 Q55.5 35.5 47 37.6 Q38.5 35.5 37.2 28 Z" fill="{wine_c}"/>')
    ic.add('<path d="M47 39 V53" stroke="#55676A" stroke-width="2.2"/>')
    ic.add('<path d="M40 55 Q47 51 54 55 Z" fill="#DCEFF1" stroke="#55676A" stroke-width="1.2"/>')
    ic.add('<path d="M39.5 24.5 Q40 31 43 34" stroke="#FFFFFF" stroke-width="1.6" fill="none" stroke-linecap="round" opacity="0.9"/>')
    return ic.svg()


def login_settings():
    ic = Icon()
    ic.shadow(32, 58, 24, 2.6)
    monitor_body(ic)
    ic.add(f'<rect x="21" y="18" width="22" height="16" rx="2" fill="#FFFFFF" opacity="0.92"/>')
    ic.add(f'<circle cx="32" cy="23.5" r="3" fill="{TEAL_500}"/><rect x="25" y="28.5" width="14" height="3" rx="1.5" fill="{SILVER_300}"/>')
    return ic.svg()


ICONS = {
    # places
    "tei-folder": lambda: folder(),
    "tei-folder-open": lambda: folder(open_=True),
    "tei-folder-documents": lambda: folder("document"),
    "tei-folder-download": lambda: folder("download"),
    "tei-folder-music": lambda: folder("music"),
    "tei-folder-pictures": lambda: folder("pictures"),
    "tei-folder-videos": lambda: folder("videos"),
    "tei-folder-templates": lambda: folder("templates"),
    "tei-folder-publicshare": lambda: folder("public"),
    "tei-folder-remote": lambda: folder("network", "teal"),
    "tei-folder-recent": lambda: folder("recent", "teal"),
    "tei-user-bookmarks": lambda: folder("star"),
    "tei-user-home": lambda: folder("home"),
    "tei-user-desktop": lambda: folder("desktop", "teal"),
    "tei-trash-empty": lambda: trash(False),
    "tei-trash-full": lambda: trash(True),
    "tei-computer": computer,
    "tei-network": network,
    "tei-server": server,
    "tei-drive-harddisk": lambda: hdd(False),
    "tei-drive-harddisk-system": lambda: hdd(True),
    "tei-drive-removable": usb,
    "tei-drive-optical": optical,
    # apps
    "tei-terminal": terminal,
    "tei-file-manager": file_manager,
    "tei-web-browser": browser,
    "tei-control-panel": control_panel,
    "tei-text-editor": text_editor,
    "tei-calculator": calculator,
    "tei-image-viewer": image_viewer,
    "tei-paint": paint,
    "tei-archive": archive,
    "tei-pdf": pdf_viewer,
    "tei-media-player": media_player,
    "tei-remote-desktop": remote_desktop,
    "tei-task-manager": task_manager,
    "tei-screenshot": screenshot,
    "tei-search": search_icon,
    "tei-run": run_icon,
    "tei-help": help_icon,
    "tei-system-info": system_info,
    "tei-sound": sound,
    "tei-display": display_settings,
    "tei-wallpaper": wallpaper_settings,
    "tei-appearance": appearance,
    "tei-keyboard": keyboard,
    "tei-mouse": mouse,
    "tei-power": power,
    "tei-printer": printer,
    "tei-scanner": scanner,
    "tei-users": users,
    "tei-user": user_single,
    "tei-datetime": datetime_icon,
    "tei-programs": programs,
    "tei-updates": updates,
    "tei-firewall": firewall,
    "tei-restore": restore,
    "tei-cleanup": cleanup,
    "tei-disks": disks,
    "tei-bluetooth": bluetooth,
    "tei-network-settings": network_settings,
    "tei-language": language,
    "tei-accessibility": accessibility,
    "tei-notifications": notifications,
    "tei-taskbar": taskbar_settings,
    "tei-windows": window_settings,
    "tei-startup": session_startup,
    "tei-default-apps": default_apps,
    "tei-settings-editor": settings_editor,
    "tei-screensaver": screensaver,
    "tei-cards": cards,
    "tei-mines": mines,
    "tei-charmap": charmap,
    "tei-installer": installer,
    "tei-welcome": welcome,
    "tei-start": start_here,
    "tei-domain": domain,
    "tei-wine": wine_icon,
    "tei-login-settings": login_settings,
    # mimetypes
    "tei-mime-text": lambda: page(),
    "tei-mime-document": lambda: page(band=BLUE_500),
    "tei-mime-spreadsheet": lambda: page(band=LEAF_600, lines=False, special=sp_spreadsheet),
    "tei-mime-presentation": lambda: page(band=HONEY_600, lines=False, special=sp_presentation),
    "tei-mime-pdf": lambda: page(band=RED_500, label="PDF"),
    "tei-mime-image": lambda: page(lines=False, special=sp_image),
    "tei-mime-audio": lambda: page(lines=False, special=sp_audio),
    "tei-mime-video": lambda: page(lines=False, special=sp_video),
    "tei-mime-script": lambda: page(lines=False, special=sp_script),
    "tei-mime-html": lambda: page(lines=False, special=sp_html),
    "tei-mime-font": lambda: page(lines=False, special=sp_font),
    "tei-mime-exe": lambda: page(lines=False, special=sp_exe, band=TEAL_600, label="EXE"),
    "tei-mime-unknown": lambda: page(lines=False),
    "tei-mime-archive": archive,
    "tei-mime-package": programs,
    "tei-mime-disc": optical,
}

# freedesktop / application icon names → Tei drawings
NAMES = {
    "places": {
        "tei-folder": ["folder", "inode-directory", "folder-symbolic-colored", "gtk-directory", "default-folder"],
        "tei-folder-open": ["folder-open", "folder-drag-accept", "folder-visiting"],
        "tei-folder-documents": ["folder-documents", "folder-documents-open"],
        "tei-folder-download": ["folder-download", "folder-downloads"],
        "tei-folder-music": ["folder-music", "folder-sound"],
        "tei-folder-pictures": ["folder-pictures", "folder-images", "folder-image"],
        "tei-folder-videos": ["folder-videos", "folder-video", "folder-movies"],
        "tei-folder-templates": ["folder-templates"],
        "tei-folder-publicshare": ["folder-publicshare", "folder-public"],
        "tei-folder-remote": ["folder-remote", "folder-network", "folder-remote-smb", "folder-remote-ftp"],
        "tei-folder-recent": ["folder-recent", "document-open-recent", "recent"],
        "tei-user-bookmarks": ["user-bookmarks", "bookmarks", "folder-favorites"],
        "tei-user-home": ["user-home", "folder-home", "go-home-folder"],
        "tei-user-desktop": ["user-desktop", "desktop", "folder-desktop"],
        "tei-trash-empty": ["user-trash", "trashcan_empty", "emptytrash"],
        "tei-trash-full": ["user-trash-full", "trashcan_full"],
        "tei-network": ["network-workgroup", "network", "network-server-workgroup", "folder-network-workgroup", "gnome-fs-network"],
        "tei-computer": ["computer", "user-computer", "gnome-fs-client"],
        "tei-start": ["start-here", "distributor-logo", "tei-logo", "xfce4-whiskermenu", "org.xfce.panel.whiskermenu", "start-here-teios", "ubuntu-logo-icon"],
    },
    "devices": {
        "tei-computer": ["computer", "computer-laptop"],
        "tei-drive-harddisk": ["drive-harddisk", "drive-harddisk-usb", "drive-harddisk-ieee1394", "harddrive"],
        "tei-drive-harddisk-system": ["drive-harddisk-system", "drive-harddisk-root"],
        "tei-drive-removable": ["drive-removable-media", "drive-removable-media-usb", "media-removable", "media-flash", "drive-removable-media-usb-pendrive", "media-flash-sd-mmc", "media-flash-memory-stick"],
        "tei-drive-optical": ["drive-optical", "media-optical", "media-optical-cd", "media-optical-dvd", "media-optical-bd", "media-optical-cd-audio"],
        "tei-network-settings": ["network-wired", "network-card"],
        "tei-printer": ["printer", "printer-network", "printer-remote", "printer-printing"],
        "tei-scanner": ["scanner"],
        "tei-keyboard": ["input-keyboard"],
        "tei-mouse": ["input-mouse", "input-touchpad"],
        "tei-bluetooth": ["bluetooth"],
        "tei-server": ["network-server"],
        "tei-sound": ["audio-speakers", "audio-card"],
        "tei-display": ["video-display", "display"],
    },
    "apps": {
        "tei-terminal": ["utilities-terminal", "org.xfce.terminal", "xfce4-terminal", "terminal", "org.gnome.Terminal", "xterm", "lxterminal"],
        "tei-file-manager": ["system-file-manager", "org.xfce.thunar", "thunar", "Thunar", "file-manager", "org.gnome.Nautilus"],
        "tei-web-browser": ["web-browser", "internet-web-browser", "falkon", "org.kde.falkon", "browser", "applications-internet"],
        "tei-control-panel": ["preferences-system", "org.xfce.settings.manager", "xfce4-settings-manager", "preferences-desktop", "tei-control-panel", "gnome-control-center", "systemsettings", "applications-system"],
        "tei-text-editor": ["accessories-text-editor", "org.xfce.mousepad", "mousepad", "text-editor", "gedit", "org.gnome.TextEditor"],
        "tei-calculator": ["accessories-calculator", "galculator", "org.gnome.Calculator", "calc", "gnome-calculator"],
        "tei-image-viewer": ["org.xfce.ristretto", "ristretto", "image-viewer", "eog", "org.gnome.eog", "multimedia-photo-viewer"],
        "tei-paint": ["drawing", "com.github.maoschanz.drawing", "applications-graphics", "kolourpaint"],
        "tei-archive": ["utilities-file-archiver", "engrampa", "file-roller", "org.gnome.FileRoller", "ark", "xarchiver"],
        "tei-pdf": ["atril", "org.gnome.Evince", "evince", "x-office-document-viewer"],
        "tei-remote-desktop": ["remmina", "org.remmina.Remmina", "preferences-desktop-remote-desktop", "krdc"],
        "tei-task-manager": ["utilities-system-monitor", "org.xfce.taskmanager", "xfce4-taskmanager", "gnome-system-monitor", "org.gnome.SystemMonitor"],
        "tei-screenshot": ["org.xfce.screenshooter", "applets-screenshooter", "accessories-screenshot", "xfce4-screenshooter", "screenshot"],
        "tei-search": ["system-search", "catfish", "org.xfce.catfish", "edit-find-replace-app"],
        "tei-run": ["system-run", "org.xfce.appfinder", "xfce4-appfinder", "gnome-run"],
        "tei-help": ["help-browser", "help-contents", "system-help", "help-faq", "org.gnome.Yelp", "yelp"],
        "tei-system-info": ["hardinfo2", "hardinfo", "help-about", "org.xfce.about", "xfce4-about", "computer-info", "tei-system-properties"],
        "tei-sound": ["multimedia-volume-control", "pavucontrol", "org.pulseaudio.pavucontrol", "preferences-desktop-sound", "audio-volume-control"],
        "tei-display": ["preferences-desktop-display", "org.xfce.settings.display", "xfce-display-settings", "display-settings"],
        "tei-wallpaper": ["preferences-desktop-wallpaper", "org.xfce.xfdesktop", "xfdesktop", "background"],
        "tei-appearance": ["preferences-desktop-theme", "org.xfce.settings.appearance", "preferences-desktop-appearance", "preferences-desktop-color"],
        "tei-keyboard": ["preferences-desktop-keyboard", "org.xfce.settings.keyboard", "keyboard", "onboard", "preferences-desktop-keyboard-shortcuts"],
        "tei-mouse": ["preferences-desktop-peripherals", "org.xfce.settings.mouse", "mouse", "preferences-desktop-mouse"],
        "tei-power": ["preferences-system-power", "org.xfce.powermanager", "xfce4-power-manager-settings", "xfce4-power-manager", "power-manager"],
        "tei-printer": ["system-config-printer", "printer", "preferences-devices-printer", "printers"],
        "tei-scanner": ["simple-scan", "org.gnome.SimpleScan", "xsane"],
        "tei-users": ["system-users", "users-admin", "config-users", "preferences-system-users", "tei-users"],
        "tei-user": ["preferences-desktop-user", "user-info", "avatar-default", "mugshot"],
        "tei-datetime": ["preferences-system-time", "time-admin", "config-date", "preferences-system-date-time", "tei-datetime"],
        "tei-programs": ["system-software-install", "synaptic", "org.gnome.Software", "gnome-software", "software-store", "applications-other", "package-x-generic", "softwarecenter"],
        "tei-updates": ["system-software-update", "update-manager", "software-update-available", "software-properties", "software-sources", "system-upgrade"],
        "tei-firewall": ["gufw", "firewall", "preferences-system-firewall", "security-high"],
        "tei-restore": ["timeshift", "deja-dup", "org.gnome.DejaDup", "document-revert"],
        "tei-cleanup": ["bleachbit", "edit-clear-all"],
        "tei-disks": ["gnome-disks", "org.gnome.DiskUtility", "gparted", "partitionmanager", "drive-harddisk-system-app", "baobab"],
        "tei-bluetooth": ["blueman", "preferences-system-bluetooth", "bluetooth-manager"],
        "tei-network-settings": ["preferences-system-network", "nm-connection-editor", "network-manager", "preferences-system-network-proxy", "networkmanager"],
        "tei-language": ["preferences-desktop-locale", "language-selector", "config-language", "preferences-desktop-locale-symbolic-colored"],
        "tei-accessibility": ["preferences-desktop-accessibility", "org.xfce.settings.accessibility", "accessibility"],
        "tei-notifications": ["preferences-system-notifications", "org.xfce.notification", "xfce4-notifyd"],
        "tei-taskbar": ["org.xfce.panel", "xfce4-panel", "panel-applets"],
        "tei-windows": ["org.xfce.xfwm4", "xfwm4", "preferences-system-windows", "org.xfce.xfwm4-tweaks", "org.xfce.workspaces", "preferences-desktop-workspaces"],
        "tei-startup": ["org.xfce.session", "xfce4-session-settings", "preferences-system-session", "session-properties"],
        "tei-default-apps": ["org.xfce.settings.default-applications", "preferences-desktop-default-applications", "preferences-desktop-default-apps"],
        "tei-settings-editor": ["org.xfce.settings.editor", "dconf-editor", "preferences-other", "org.xfce.settings.color", "preferences-color"],
        "tei-screensaver": ["preferences-desktop-screensaver", "org.xfce.ScreenSaver", "xfce4-screensaver-preferences", "org.xfce.screensaver"],
        "tei-drive-removable": ["org.xfce.volman", "thunar-volman-settings", "drive-removable-media-app"],
        "tei-cards": ["gnome-aisleriot", "aisleriot", "sol", "org.gnome.Aisleriot", "ace-solitaire", "ace-freecell", "ace-spider", "ace-golf", "ace-canfield", "ace-thornq", "applications-games"],
        "tei-mines": ["gnome-mines", "ace-minesweeper", "org.gnome.Mines", "kmines"],
        "tei-charmap": ["accessories-character-map", "gucharmap", "org.gnome.Charmap"],
        "tei-installer": ["calamares", "system-installer", "install", "tei-installer", "ubiquity"],
        "tei-welcome": ["tei-welcome"],
        "tei-domain": ["tei-domain", "realmd", "preferences-system-domain"],
        "tei-wine": ["wine", "wine-notepad", "wine-winecfg", "winecfg", "application-x-wine-extension-msp", "wine-uninstaller", "winetricks"],
        "tei-login-settings": ["lightdm-gtk-greeter-settings", "preferences-system-login", "gdm-setup"],
        "tei-computer": ["computer"],
        "tei-start": ["start-here", "tei-logo", "xfce4-whiskermenu"],
        "tei-media-player": ["applications-multimedia", "multimedia-video-player", "multimedia-audio-player", "parole", "org.xfce.Parole", "totem"],
    },
    "mimetypes": {
        "tei-mime-text": ["text-x-generic", "text-plain", "text-x-readme", "text-x-log", "x-office-document-template"],
        "tei-mime-document": ["x-office-document", "application-msword", "application-vnd.openxmlformats-officedocument.wordprocessingml.document", "application-rtf", "text-richtext"],
        "tei-mime-spreadsheet": ["x-office-spreadsheet", "application-vnd.ms-excel", "application-vnd.openxmlformats-officedocument.spreadsheetml.sheet", "text-csv"],
        "tei-mime-presentation": ["x-office-presentation", "application-vnd.ms-powerpoint", "application-vnd.openxmlformats-officedocument.presentationml.presentation"],
        "tei-mime-pdf": ["application-pdf", "application-x-pdf", "image-x-eps", "application-postscript"],
        "tei-mime-image": ["image-x-generic", "image-png", "image-jpeg", "image-gif", "image-bmp", "image-svg+xml", "image-webp", "image-tiff"],
        "tei-mime-audio": ["audio-x-generic", "audio-mpeg", "audio-x-wav", "audio-ogg", "audio-flac", "audio-x-flac"],
        "tei-mime-video": ["video-x-generic", "video-mp4", "video-x-matroska", "video-webm", "video-x-msvideo", "video-mpeg"],
        "tei-mime-script": ["text-x-script", "application-x-shellscript", "text-x-python", "application-x-perl", "text-x-csrc", "text-x-c++src", "application-javascript", "application-json", "text-x-makefile"],
        "tei-mime-html": ["text-html", "application-xhtml+xml", "text-xml", "application-xml"],
        "tei-mime-font": ["font-x-generic", "application-x-font-ttf", "font-ttf", "font-otf"],
        "tei-mime-exe": ["application-x-executable", "application-x-ms-dos-executable", "application-x-msdownload", "application-x-msi", "application-x-ms-shortcut", "application-x-sharedlib", "application-x-desktop"],
        "tei-mime-unknown": ["unknown", "application-octet-stream", "empty", "application-x-generic"],
        "tei-mime-archive": ["package-x-generic", "application-x-archive", "application-zip", "application-x-tar", "application-x-compressed-tar", "application-x-7z-compressed", "application-x-rar", "application-gzip", "application-x-bzip", "application-x-xz-compressed-tar", "application-zstd", "application-x-zstd-compressed-tar"],
        "tei-mime-package": ["application-x-deb", "application-vnd.debian.binary-package", "application-x-rpm", "application-vnd.snap", "application-vnd.flatpak.ref"],
        "tei-mime-disc": ["application-x-cd-image", "application-x-iso9660-image", "application-x-raw-disk-image"],
        "tei-folder": ["inode-directory"],
    },
}


def build(out):
    import shutil
    if os.path.exists(out):
        shutil.rmtree(out)
    os.makedirs(out)
    src = os.path.join(out, "_src")
    os.makedirs(src)
    for name, fn in ICONS.items():
        open(os.path.join(src, name + ".svg"), "w").write(fn())
    dirs = []
    for ctx, mapping in NAMES.items():
        d = os.path.join(out, "scalable", ctx)
        os.makedirs(d, exist_ok=True)
        dirs.append(("scalable/" + ctx, ctx))
        for icon, aliases in mapping.items():
            shutil.copy(os.path.join(src, icon + ".svg"), os.path.join(d, icon + ".svg"))
            for a in aliases:
                p = os.path.join(d, a + ".svg")
                if not os.path.exists(p):
                    os.symlink(icon + ".svg", p)
    # every tei-* icon also available under apps for our own launchers
    d = os.path.join(out, "scalable", "apps")
    for name in ICONS:
        p = os.path.join(d, name + ".svg")
        if not os.path.exists(p):
            shutil.copy(os.path.join(src, name + ".svg"), p)
    shutil.rmtree(src)
    ctxname = {"places": "Places", "devices": "Devices", "apps": "Applications", "mimetypes": "MimeTypes"}
    with open(os.path.join(out, "index.theme"), "w") as fh:
        fh.write("[Icon Theme]\nName=Tei\nComment=WinLow XP — glossy classic icons (original artwork)\n"
                 "Inherits=elementary-xfce,Adwaita,hicolor\nExample=folder\n")
        fh.write("Directories=" + ",".join(d for d, _ in dirs) + "\n\n")
        for d, ctx in dirs:
            fh.write(f"[{d}]\nContext={ctxname[ctx]}\nSize=64\nMinSize=8\nMaxSize=512\nType=Scalable\n\n")
    print("icons:", len(ICONS), "drawings ->", out)


if __name__ == "__main__":
    build(sys.argv[1])
