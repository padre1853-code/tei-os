"""Shared helpers for the WinLow XP graphical tools (GTK 3)."""
import locale
import os
import shlex
import shutil
import subprocess

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

# ---------------------------------------------------------------- translations
try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass
_LANG = (os.environ.get("LANGUAGE") or os.environ.get("LC_ALL") or os.environ.get("LC_MESSAGES")
         or os.environ.get("LANG") or "en").split(":")[0].lower()
RO = _LANG.startswith("ro")

_TR = {}


def tr_add(table):
    _TR.update(table)


def T(text):
    """Return the Romanian text when running in Romanian, else the English original."""
    if RO:
        return _TR.get(text, text)
    return text


tr_add({
    "Close": "Închide",
    "Cancel": "Anulează",
    "Apply": "Aplică",
    "OK": "OK",
    "Back": "Înapoi",
    "Help": "Ajutor",
    "Search": "Căutare",
    "Error": "Eroare",
    "Done": "Gata",
    "Yes": "Da",
    "No": "Nu",
    "Add": "Adaugă",
    "Remove": "Elimină",
    "Change": "Modifică",
    "Not available": "Indisponibil",
    "This component is not installed.": "Această componentă nu este instalată.",
})


# ---------------------------------------------------------------- process helpers
def which(cmd):
    if not cmd:
        return None
    exe = cmd[0] if isinstance(cmd, (list, tuple)) else shlex.split(cmd)[0]
    if os.path.isabs(exe):
        return exe if os.access(exe, os.X_OK) else None
    return shutil.which(exe)


_LAST_LAUNCH = {}


def launch(cmd):
    """Start a program detached from us. cmd: list or shell-like string.
    A second request for the same program within 2 seconds is ignored, so a double-click on a
    single-click tile (the habit from other systems) does not open the program twice."""
    if isinstance(cmd, str):
        cmd = shlex.split(cmd)
    import time
    key, now = tuple(cmd), time.monotonic()
    if now - _LAST_LAUNCH.get(key, -10) < 2.0:
        return True
    _LAST_LAUNCH[key] = now
    try:
        subprocess.Popen(cmd, start_new_session=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except OSError:
        return False


def run_async(cmd, done_cb, input_text=None):
    """Run cmd in the background; call done_cb(returncode, stdout, stderr) in the GTK main loop."""
    import threading

    def worker():
        try:
            p = subprocess.run(cmd, input=input_text, capture_output=True, text=True)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except OSError as e:
            rc, out, err = 127, "", str(e)
        GLib.idle_add(done_cb, rc, out, err)

    threading.Thread(target=worker, daemon=True).start()


def is_live_session():
    try:
        return "boot=casper" in open("/proc/cmdline").read()
    except OSError:
        return False


# ---------------------------------------------------------------- styling
_CSS = b"""
.tei-banner {
  background-image: linear-gradient(to right, #17656F 0%, #2A8F9A 60%, #47A9B3 100%);
  color: #FFFFFF;
  padding: 14px 18px;
  border-bottom: 3px solid #EE9F2E;
}
.tei-banner label { color: #FFFFFF; text-shadow: 0 1px rgba(0,0,0,0.35); }
.tei-banner .tei-title { font-size: 17pt; font-weight: bold; }
.tei-banner .tei-subtitle { font-size: 10pt; opacity: 0.92; }
.tei-tile {
  border-radius: 6px;
  border: 1px solid transparent;
  background-image: none;
  background-color: transparent;
  box-shadow: none;
  padding: 8px;
}
.tei-tile:hover {
  border-color: #A8D8DD;
  background-image: linear-gradient(to bottom, #F5FBFC, #DDF0F2);
}
.tei-tile .tei-tile-title { font-weight: bold; color: #135A64; }
.tei-tile .tei-tile-desc { color: #4A5759; font-size: 9pt; }
.tei-link { color: #1E7A85; }
.tei-section { font-weight: bold; color: #135A64; font-size: 11pt; }
.tei-muted { color: #6F7A7D; }
.tei-card {
  background-color: #FFFFFF;
  border: 1px solid #D3DCDD;
  border-radius: 6px;
  padding: 12px;
}
.tei-body { background-color: #F7F9F9; }
"""


def install_css():
    prov = Gtk.CssProvider()
    prov.load_from_data(_CSS)
    Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), prov,
                                             Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)


def banner(icon_name, title, subtitle=None):
    box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
    box.get_style_context().add_class("tei-banner")
    img = Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.DIALOG)
    img.set_pixel_size(48)
    box.pack_start(img, False, False, 0)
    v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
    v.set_valign(Gtk.Align.CENTER)
    t = Gtk.Label(label=title, xalign=0)
    t.get_style_context().add_class("tei-title")
    v.pack_start(t, False, False, 0)
    if subtitle:
        s = Gtk.Label(label=subtitle, xalign=0)
        s.set_line_wrap(True)
        s.get_style_context().add_class("tei-subtitle")
        v.pack_start(s, False, False, 0)
    box.pack_start(v, True, True, 0)
    return box


def message(parent, text, secondary=None, kind=Gtk.MessageType.INFO):
    d = Gtk.MessageDialog(transient_for=parent, modal=True, message_type=kind,
                          buttons=Gtk.ButtonsType.OK, text=text)
    if secondary:
        d.format_secondary_text(secondary)
    d.run()
    d.destroy()


def confirm(parent, text, secondary=None):
    d = Gtk.MessageDialog(transient_for=parent, modal=True, message_type=Gtk.MessageType.QUESTION,
                          buttons=Gtk.ButtonsType.YES_NO, text=text)
    if secondary:
        d.format_secondary_text(secondary)
    r = d.run()
    d.destroy()
    return r == Gtk.ResponseType.YES
