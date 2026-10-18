"""Boot splash (Plymouth), boot menu (GRUB) and installer (Calamares) artwork for Tei OS."""
import io
import os
import subprocess
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

sys.path.insert(0, os.path.dirname(__file__))
from palette import *  # noqa
from logo import leaf_svg, wordmark_svg  # noqa
import wallpaper  # noqa

SCREENS = os.path.join(os.path.dirname(__file__), "..", "screens")
FONT_B = "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf"
FONT_R = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"
FONT_L = "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf"


def svg_png(svg, w, h=None):
    args = ["rsvg-convert", "-w", str(w)] + (["-h", str(h)] if h else [])
    return Image.open(io.BytesIO(subprocess.run(args, input=svg.encode(), capture_output=True, check=True).stdout)).convert("RGBA")


def plymouth(out):
    os.makedirs(out, exist_ok=True)
    wallpaper.wp_login(1920, 1080).save(f"{out}/background.png")
    # logo + wordmark (white text) for the dark teal splash
    logo = svg_png(leaf_svg(256, shadow=False, uid="p"), 150)
    f1, f2 = ImageFont.truetype(FONT_B, 54), ImageFont.truetype(FONT_L, 54)
    W, H = 420, 240
    canvas = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    canvas.alpha_composite(logo, ((W - 150) // 2, 0))
    d = ImageDraw.Draw(canvas)
    w1, w2 = d.textlength("Tei ", font=f1), d.textlength("OS", font=f2)
    x = (W - (w1 + w2)) / 2
    d.text((x, 160), "Tei ", font=f1, fill=(255, 255, 255, 255))
    d.text((x + w1, 160), "OS", font=f2, fill=hex2rgb(HONEY_400) + (255,))
    canvas = canvas.crop(canvas.getbbox())
    canvas.save(f"{out}/logo.png")
    # loading dot
    d = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
    dd = ImageDraw.Draw(d)
    dd.ellipse([4, 4, 36, 36], fill=hex2rgb(HONEY_400) + (255,))
    dd.ellipse([10, 8, 24, 18], fill=(255, 255, 255, 110))
    d = d.resize((14, 14), Image.LANCZOS)
    d.save(f"{out}/dot.png")
    # password entry box and bullet
    box = Image.new("RGBA", (300, 40), (0, 0, 0, 0))
    bd = ImageDraw.Draw(box)
    bd.rounded_rectangle([0, 0, 299, 39], radius=8, fill=(255, 255, 255, 235), outline=hex2rgb(TEAL_300) + (255,), width=2)
    box.save(f"{out}/entry.png")
    b = Image.new("RGBA", (12, 12), (0, 0, 0, 0))
    ImageDraw.Draw(b).ellipse([1, 1, 11, 11], fill=hex2rgb(TEAL_800) + (255,))
    b.save(f"{out}/bullet.png")
    lock = svg_png('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect x="6" y="14" width="20" height="15" rx="3" fill="#FFFFFF"/>'
                   '<path d="M10 14 V10 A6 6 0 0 1 22 10 V14" stroke="#FFFFFF" stroke-width="3" fill="none"/></svg>', 28)
    lock.save(f"{out}/lock.png")
    open(f"{out}/teios.plymouth", "w").write("""[Plymouth Theme]
Name=Tei OS
Description=Tei OS boot splash
ModuleName=script

[script]
ImageDir=/usr/share/plymouth/themes/teios
ScriptFile=/usr/share/plymouth/themes/teios/teios.script
""")
    open(f"{out}/teios.script", "w").write(PLYMOUTH_SCRIPT)


PLYMOUTH_SCRIPT = r'''# Tei OS boot splash — original design
Window.SetBackgroundTopColor(0.04, 0.23, 0.25);
Window.SetBackgroundBottomColor(0.03, 0.17, 0.19);

screen_w = Window.GetWidth();
screen_h = Window.GetHeight();
screen_x = Window.GetX();
screen_y = Window.GetY();

bg_img = Image("background.png");
bg = Sprite(bg_img.Scale(screen_w, screen_h));
bg.SetPosition(screen_x, screen_y, -100);

logo_img = Image("logo.png");
scale = 1;
if (screen_h < 700) scale = 0.7;
logo_img = logo_img.Scale(logo_img.GetWidth() * scale, logo_img.GetHeight() * scale);
logo = Sprite(logo_img);
logo.SetX(screen_x + screen_w / 2 - logo_img.GetWidth() / 2);
logo.SetY(screen_y + screen_h / 2 - logo_img.GetHeight() / 2 - 50);
logo.SetZ(10);

dot_img = Image("dot.png");
n = 5;
spacing = 26;
base_x = screen_x + screen_w / 2 - (spacing * (n - 1)) / 2 - dot_img.GetWidth() / 2;
dots_y = logo.GetY() + logo_img.GetHeight() + 50;
for (i = 0; i < n; i++) {
    dots[i] = Sprite(dot_img);
    dots[i].SetPosition(base_x + i * spacing, dots_y, 10);
    dots[i].SetOpacity(0.25);
}

frame = 0;
password_mode = 0;
fun refresh_callback () {
    frame++;
    if (password_mode) return;
    t = frame / 9;
    for (i = 0; i < n; i++) {
        v = Math.Sin(t - i * 0.75);
        if (v < 0) v = 0;
        dots[i].SetOpacity(0.22 + 0.78 * v);
    }
}
Plymouth.SetRefreshFunction(refresh_callback);

# ---------------------------------------------------------------- messages
msg_sprite = Sprite();
msg_sprite.SetZ(20);
fun message_callback (text) {
    img = Image.Text(text, 0.85, 0.93, 0.94);
    msg_sprite.SetImage(img);
    msg_sprite.SetPosition(screen_x + screen_w / 2 - img.GetWidth() / 2, screen_y + screen_h - 60, 20);
}
Plymouth.SetMessageFunction(message_callback);

# ---------------------------------------------------------------- disk encryption password
entry_img = Image("entry.png");
bullet_img = Image("bullet.png");
lock_img = Image("lock.png");
prompt_sprite = Sprite();
entry_sprite = Sprite();
lock_sprite = Sprite();
bullets = [];

fun display_password_callback (prompt, bullet_count) {
    password_mode = 1;
    for (i = 0; i < n; i++) dots[i].SetOpacity(0);
    entry_sprite.SetOpacity(1);
    lock_sprite.SetOpacity(1);
    prompt_sprite.SetOpacity(1);
    ey = dots_y - 6;
    ex = screen_x + screen_w / 2 - entry_img.GetWidth() / 2;
    entry_sprite.SetImage(entry_img);
    entry_sprite.SetPosition(ex, ey, 30);
    lock_sprite.SetImage(lock_img);
    lock_sprite.SetPosition(ex - lock_img.GetWidth() - 12, ey + 6, 30);
    p = Image.Text(prompt, 1, 1, 1);
    prompt_sprite.SetImage(p);
    prompt_sprite.SetPosition(screen_x + screen_w / 2 - p.GetWidth() / 2, ey - p.GetHeight() - 10, 30);
    for (i = 0; bullets[i] || i < bullet_count; i++) {
        if (!bullets[i]) bullets[i] = Sprite(bullet_img);
        if (i < bullet_count && i < 22) {
            bullets[i].SetPosition(ex + 14 + i * 12, ey + entry_img.GetHeight() / 2 - 6, 31);
            bullets[i].SetOpacity(1);
        } else {
            bullets[i].SetOpacity(0);
        }
    }
}
Plymouth.SetDisplayPasswordFunction(display_password_callback);

fun display_normal_callback () {
    entry_sprite.SetOpacity(0);
    lock_sprite.SetOpacity(0);
    prompt_sprite.SetOpacity(0);
    for (i = 0; bullets[i]; i++) bullets[i].SetOpacity(0);
    password_mode = 0;
}
Plymouth.SetDisplayNormalFunction(display_normal_callback);

fun quit_callback () {
    for (i = 0; i < n; i++) dots[i].SetOpacity(0);
}
Plymouth.SetQuitFunction(quit_callback);
'''


def grub_theme(out, title="Tei OS"):
    os.makedirs(out, exist_ok=True)
    bg = wallpaper.wp_login(1920, 1080).convert("RGB")
    d = ImageDraw.Draw(bg, "RGBA")
    logo = svg_png(leaf_svg(256, shadow=False, uid="g"), 120)
    bg.paste(logo, (1920 // 2 - 60, 170), logo)
    f = ImageFont.truetype(FONT_B, 64)
    f2 = ImageFont.truetype(FONT_L, 64)
    w1 = d.textlength("Tei ", font=f)
    w2 = d.textlength("OS", font=f2)
    x = (1920 - (w1 + w2)) // 2
    d.text((x, 305), "Tei ", font=f, fill=(255, 255, 255))
    d.text((x + w1, 305), "OS", font=f2, fill=hex2rgb(HONEY_400))
    # translucent panel behind the menu
    d.rounded_rectangle([560, 400, 1360, 860], radius=18, fill=(8, 50, 58, 120), outline=(168, 216, 221, 90), width=2)
    bg.save(f"{out}/background.jpg", quality=92)
    # selection highlight (JPEG — the signed GRUB build has no PNG loader)
    sel = Image.new("RGB", (8, 40))
    a = np.zeros((40, 8, 3), np.float32)
    top, bot = np.array(hex2rgb("#FBD07E"), np.float32), np.array(hex2rgb(HONEY_600), np.float32)
    for y in range(40):
        a[y] = top + (bot - top) * (y / 39)
    sel = Image.fromarray(a.astype(np.uint8))
    sel.save(f"{out}/select_c.jpg", quality=95)
    sel.crop((0, 0, 4, 40)).save(f"{out}/select_w.jpg", quality=95)
    sel.crop((0, 0, 4, 40)).save(f"{out}/select_e.jpg", quality=95)
    open(f"{out}/theme.txt", "w").write(GRUB_THEME)


GRUB_THEME = """# Tei OS boot menu theme
title-text: ""
desktop-image: "background.jpg"
desktop-image-scale-method: "stretch"
desktop-color: "#0B3A41"
terminal-font: "Unifont Regular 16"

+ boot_menu {
  left = 29%
  top = 39%
  width = 42%
  height = 38%
  item_font = "DejaVu Sans Regular 16"
  selected_item_font = "DejaVu Sans Bold 16"
  item_color = "#E6F4F5"
  selected_item_color = "#3B2205"
  item_height = 34
  item_padding = 8
  item_spacing = 6
  icon_width = 0
  icon_height = 0
  item_icon_space = 0
  selected_item_pixmap_style = "select_*.jpg"
  scrollbar = false
}

+ label {
  top = 82%
  left = 0
  width = 100%
  align = "center"
  font = "DejaVu Sans Regular 14"
  color = "#BFE3E7"
  text = "↑ ↓  alegeți   ·   Enter  porniți   ·   choose ↑ ↓ and press Enter"
}

+ label {
  id = "__timeout__"
  top = 86%
  left = 0
  width = 100%
  align = "center"
  font = "DejaVu Sans Regular 14"
  color = "#F6B84E"
  text = "Pornire automată în %d s"
}
"""


def calamares(out):
    os.makedirs(out, exist_ok=True)
    svg_png(leaf_svg(256, shadow=False, uid="c"), 128).save(f"{out}/logo.png")
    svg_png(leaf_svg(256, shadow=False, uid="c2"), 64).save(f"{out}/icon.png")
    # welcome illustration: wordmark on light background
    wm = svg_png(wordmark_svg(), 520)
    wm.save(f"{out}/welcome.png")
    # slideshow: real screenshots of the desktop (artwork/screens/*.png), framed
    screens = sorted(os.path.join(SCREENS, f) for f in os.listdir(SCREENS) if f.endswith(".png")) if os.path.isdir(SCREENS) else []
    for i, src in enumerate(screens[:5], start=1):
        im = Image.open(src).convert("RGB")
        # keep 16:9 without distortion: trim the top of the desktop (the taskbar stays at the bottom)
        want_h = round(im.width * 9 / 16)
        if im.height > want_h:
            im = im.crop((0, im.height - want_h, im.width, im.height))
        im = im.resize((640, 360), Image.LANCZOS)
        mask = Image.new("L", im.size, 0)
        ImageDraw.Draw(mask).rounded_rectangle([0, 0, im.width - 1, im.height - 1], radius=10, fill=255)
        rgba = im.convert("RGBA")
        rgba.putalpha(mask)
        canvas = Image.new("RGBA", (im.width + 24, im.height + 24), (0, 0, 0, 0))
        sh = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        ImageDraw.Draw(sh).rounded_rectangle([12, 16, 12 + im.width, 16 + im.height], radius=12, fill=(0, 0, 0, 110))
        canvas.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
        canvas.alpha_composite(rgba, (12, 10))
        ImageDraw.Draw(canvas).rounded_rectangle([12, 10, 12 + im.width - 1, 10 + im.height - 1], radius=10, outline=(255, 255, 255, 140), width=1)
        canvas.save(f"{out}/shot{i}.png")


def grub_installed_bg(path):
    bg = wallpaper.wp_login(1024, 768).convert("RGB")
    bg.save(path)


if __name__ == "__main__":
    out = sys.argv[1]
    plymouth(os.path.join(out, "plymouth", "teios"))
    grub_theme(os.path.join(out, "grub", "teios"))
    calamares(os.path.join(out, "calamares"))
    os.makedirs(os.path.join(out, "backgrounds"), exist_ok=True)
    grub_installed_bg(os.path.join(out, "backgrounds", "grub.png"))
    print("boot artwork written to", out)
