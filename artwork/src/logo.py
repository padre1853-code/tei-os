"""Tei OS logo: an original stylised linden (tei) leaf."""
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa

# Heart-shaped linden leaf, notch at top, tip at bottom (pre-rotation), 256x256 box.
LEAF_PATH = (
    "M128 74 "
    "C114 44 58 34 36 76 "
    "C18 112 30 156 66 186 "
    "C88 204 110 218 128 240 "
    "C148 214 172 202 194 184 "
    "C232 152 242 106 222 74 "
    "C198 36 142 42 128 74 Z"
)
MIDRIB = "M128 80 C126 120 126 170 128 232"
VEINS = [
    "M128 84 C106 84 82 88 58 102",
    "M128 84 C150 84 174 88 198 102",
    "M127 112 C110 118 88 130 62 152",
    "M129 112 C146 118 168 130 194 152",
    "M127 146 C112 154 96 166 80 186",
    "M129 146 C144 154 160 166 176 186",
    "M127 180 C118 188 110 198 102 210",
    "M129 180 C138 188 146 198 154 210",
]
STEM = "M128 78 C126 60 120 42 108 24"


def leaf_svg(size=256, veins=True, gloss=True, shadow=True, rotate=-24, outline=True, uid="l"):
    v = ""
    if veins:
        v = "".join(f'<path d="{d}" fill="none" stroke="url(#{uid}vein)" stroke-width="5" stroke-linecap="round"/>' for d in VEINS)
        v += f'<path d="{MIDRIB}" fill="none" stroke="url(#{uid}vein)" stroke-width="7" stroke-linecap="round"/>'
    g = ""
    if gloss:
        g = (f'<path d="M128 78 C114 50 62 42 42 80 C30 104 34 128 46 146 '
             f'C70 120 104 100 128 96 Z" fill="url(#{uid}gloss)"/>')
    sh = ""
    if shadow:
        sh = f'<ellipse cx="128" cy="236" rx="74" ry="10" fill="#000" opacity="0.18" filter="url(#{uid}blur)"/>'
    stroke = f'stroke="{LEAF_800}" stroke-width="5" stroke-linejoin="round"' if outline else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 256 256">
  <defs>
    <linearGradient id="{uid}fill" x1="0.15" y1="0.05" x2="0.85" y2="0.95">
      <stop offset="0" stop-color="{LEAF_300}"/>
      <stop offset="0.45" stop-color="{LEAF_500}"/>
      <stop offset="1" stop-color="{LEAF_700}"/>
    </linearGradient>
    <linearGradient id="{uid}vein" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#E9F6C8" stop-opacity="0.85"/>
      <stop offset="1" stop-color="#D3EC9E" stop-opacity="0.55"/>
    </linearGradient>
    <linearGradient id="{uid}gloss" x1="0" y1="0" x2="0.6" y2="1">
      <stop offset="0" stop-color="#FFFFFF" stop-opacity="0.75"/>
      <stop offset="1" stop-color="#FFFFFF" stop-opacity="0"/>
    </linearGradient>
    <linearGradient id="{uid}stem" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{LEAF_600}"/>
      <stop offset="1" stop-color="{LEAF_800}"/>
    </linearGradient>
    <filter id="{uid}blur" x="-20%" y="-200%" width="140%" height="500%"><feGaussianBlur stdDeviation="5"/></filter>
  </defs>
  {sh}
  <g transform="rotate({rotate} 128 136)">
    <path d="{STEM}" fill="none" stroke="url(#{uid}stem)" stroke-width="9" stroke-linecap="round"/>
    <path d="{LEAF_PATH}" fill="url(#{uid}fill)" {stroke}/>
    {v}
    {g}
  </g>
</svg>'''


def leaf_mono_svg(size=256, color="#FFFFFF", rotate=-24):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 256 256">
  <g transform="rotate({rotate} 128 136)" fill="{color}">
    <path d="{STEM}" fill="none" stroke="{color}" stroke-width="12" stroke-linecap="round"/>
    <path d="{LEAF_PATH}"/>
  </g>
</svg>'''


def wordmark_svg(dark=False, width=900, height=256):
    tc = "#FFFFFF" if dark else TEAL_800
    sub = HONEY_400 if dark else HONEY_600
    leaf = leaf_svg(256, uid="w").split('\n', 1)[1].rsplit('</svg>', 1)[0]
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <svg x="0" y="0" width="256" height="256" viewBox="0 0 256 256">{leaf}</svg>
  <text x="270" y="170" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="150" font-weight="700" fill="{tc}" letter-spacing="-2">Tei</text>
  <text x="522" y="170" font-family="Noto Sans, DejaVu Sans, sans-serif" font-size="150" font-weight="300" fill="{sub}">OS</text>
</svg>'''


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(__file__), "..", "out")
    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, "tei-logo.svg"), "w").write(leaf_svg())
    open(os.path.join(out, "tei-logo-small.svg"), "w").write(leaf_svg(veins=False, shadow=False, uid="s"))
    open(os.path.join(out, "tei-logo-white.svg"), "w").write(leaf_mono_svg())
    open(os.path.join(out, "tei-wordmark.svg"), "w").write(wordmark_svg())
    open(os.path.join(out, "tei-wordmark-dark.svg"), "w").write(wordmark_svg(dark=True))
    print("logo written to", out)
