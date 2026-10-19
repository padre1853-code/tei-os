"""WinLow XP — shared colour palette.

Theme (1.0 final): dark charcoal chrome with an ember-orange accent. The older teal/honey/leaf
families stay available for icon artwork, where they are just colourful details."""

# ember orange — the accent colour of the theme (selection, Start button, highlights)
ORANGE_900 = "#7A2E00"
ORANGE_800 = "#9E3D00"
ORANGE_700 = "#C24E00"
ORANGE_600 = "#E06A00"
ORANGE_500 = "#F57C00"
ORANGE_400 = "#FF9A2E"
ORANGE_300 = "#FFB65C"
ORANGE_200 = "#FFD39A"
ORANGE_100 = "#FFF0DC"

# charcoal — window title bars, taskbar, boot screens (very slightly warm)
CHAR_950 = "#0E0D0D"
CHAR_900 = "#171615"
CHAR_800 = "#201E1D"
CHAR_700 = "#2B2927"
CHAR_600 = "#383533"
CHAR_500 = "#4A4744"
CHAR_400 = "#62605D"
CHAR_300 = "#878480"
CHAR_200 = "#B2AFAB"
CHAR_100 = "#E3E1DE"

TEAL_950 = "#0B3A41"
TEAL_900 = "#0F4C55"
TEAL_800 = "#135A64"
TEAL_700 = "#17656F"
TEAL_600 = "#1E7A85"
TEAL_500 = "#2A8F9A"
TEAL_400 = "#47A9B3"
TEAL_300 = "#7CC4CB"
TEAL_200 = "#A8D8DD"
TEAL_100 = "#DDF0F2"

HONEY_800 = "#9A5A0E"
HONEY_700 = "#B96B14"
HONEY_600 = "#D9831F"
HONEY_500 = "#EE9F2E"
HONEY_400 = "#F6B84E"
HONEY_300 = "#FAD07E"
HONEY_200 = "#FBE0A8"
HONEY_100 = "#FEF3DC"

LEAF_800 = "#2E5E14"
LEAF_700 = "#3F7A1E"
LEAF_600 = "#529426"
LEAF_500 = "#6DAA2C"
LEAF_400 = "#8CC43F"
LEAF_300 = "#B2DB6E"

GRAPHITE_900 = "#1E2324"
GRAPHITE_800 = "#2E3436"
GRAPHITE_700 = "#3D4547"
GRAPHITE_600 = "#555F62"
GRAPHITE_500 = "#6F7A7D"
SILVER_400 = "#9AA4A7"
SILVER_300 = "#B9C0C2"
SILVER_200 = "#D5DADB"
SILVER_100 = "#ECEFEF"

BG = "#F3F3F0"
BASE = "#FFFFFF"
TEXT = "#1E2324"

RED_600 = "#C8392B"
RED_500 = "#E04B3A"
BLUE_600 = "#2F6FB2"
BLUE_500 = "#3F86CC"
PURPLE_500 = "#7E57C2"


def hex2rgb(h):
    h = h.lstrip('#')
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def rgb2hex(c):
    return '#%02X%02X%02X' % tuple(max(0, min(255, int(round(v)))) for v in c[:3])


def mix(a, b, t):
    a, b = hex2rgb(a), hex2rgb(b)
    return rgb2hex([a[i] + (b[i] - a[i]) * t for i in range(3)])


def lighten(c, t):
    return mix(c, "#FFFFFF", t)


def darken(c, t):
    return mix(c, "#000000", t)


# Product name as drawn in the wordmark: first part bold, second part light/orange.
PRODUCT_NAME = ("WinLow", "XP")
