#!/usr/bin/python3
"""Tei OS Welcome — first steps after installation (and the installer launcher in the live session)."""
import configparser
import os
import sys

sys.path.insert(0, "/usr/lib/tei")
from teilib import (GLib, Gtk, T, banner, install_css, is_live_session, launch,  # noqa: E402
                    message, run_async, tr_add, which)

tr_add({
    "Welcome to Tei OS": "Bun venit în Tei OS",
    "A classic desktop, ready for work. Here are a few first steps.": "Un desktop clasic, gata de lucru. Iată câțiva primi pași.",
    "Install Tei OS": "Instalează Tei OS",
    "Install on this computer's disk (takes about 10 minutes)": "Instalare pe discul acestui computer (durează aproximativ 10 minute)",
    "Control Panel": "Panou de control",
    "All settings in one place": "Toate setările într-un singur loc",
    "Updates": "Actualizări",
    "Get the latest security fixes": "Obțineți cele mai noi remedieri de securitate",
    "Drivers": "Drivere",
    "Graphics, Wi-Fi and other drivers": "Drivere video, Wi-Fi și altele",
    "Install programs": "Instalare programe",
    "Thousands of free programs": "Mii de programe gratuite",
    "Install Firefox": "Instalează Firefox",
    "Mozilla Firefox browser (needs internet)": "Navigatorul Mozilla Firefox (necesită internet)",
    "Help and Support": "Ajutor și asistență",
    "Guides for everyday tasks": "Ghiduri pentru activitățile zilnice",
    "System Restore": "Restaurare sistem",
    "Protect the system with snapshots": "Protejați sistemul cu instantanee",
    "Show this window at startup": "Arată această fereastră la pornire",
    "Installing Firefox… this can take a few minutes.": "Se instalează Firefox… poate dura câteva minute.",
    "Firefox was installed. You will find it in the Start menu.": "Firefox a fost instalat. Îl găsiți în meniul Start.",
    "Firefox could not be installed": "Firefox nu a putut fi instalat",
    "Check the internet connection and try again.": "Verificați conexiunea la internet și încercați din nou.",
    "Live session": "Sesiune live",
    "You are trying Tei OS without installing it. Changes are not saved.":
        "Încercați Tei OS fără să-l instalați. Modificările nu se salvează.",
})

CONF = os.path.expanduser("~/.config/tei/welcome.conf")


def load_show():
    c = configparser.ConfigParser()
    c.read(CONF)
    return c.getboolean("welcome", "show", fallback=True)


def save_show(v):
    os.makedirs(os.path.dirname(CONF), exist_ok=True)
    c = configparser.ConfigParser()
    c["welcome"] = {"show": "true" if v else "false"}
    with open(CONF, "w") as fh:
        c.write(fh)


class Welcome(Gtk.Window):
    def __init__(self):
        super().__init__(title=T("Welcome to Tei OS"))
        self.set_icon_name("tei-welcome")
        self.set_default_size(720, 540)
        self.set_position(Gtk.WindowPosition.CENTER)
        install_css()
        live = is_live_session()
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        outer.pack_start(banner("tei-start", T("Welcome to Tei OS"), T("A classic desktop, ready for work. Here are a few first steps.")), False, False, 0)
        if live:
            info = Gtk.InfoBar(message_type=Gtk.MessageType.INFO)
            info.get_content_area().pack_start(Gtk.Label(label=T("You are trying Tei OS without installing it. Changes are not saved.")), False, False, 0)
            outer.pack_start(info, False, False, 0)
        grid = Gtk.FlowBox(margin=14)
        grid.set_selection_mode(Gtk.SelectionMode.NONE)
        grid.set_max_children_per_line(2)
        grid.set_min_children_per_line(2)
        grid.set_homogeneous(True)
        grid.set_row_spacing(6)
        grid.set_column_spacing(6)
        items = []
        if live:
            items.append(("tei-installer", "Install Tei OS", "Install on this computer's disk (takes about 10 minutes)", ["tei-install"]))
        items += [
            ("tei-control-panel", "Control Panel", "All settings in one place", ["tei-control-panel"]),
            ("tei-updates", "Updates", "Get the latest security fixes", ["update-manager"]),
            ("tei-programs", "Drivers", "Graphics, Wi-Fi and other drivers", ["software-properties-gtk", "--open-tab=4"]),
            ("tei-programs", "Install programs", "Thousands of free programs", ["synaptic-pkexec"]),
            ("tei-web-browser", "Install Firefox", "Mozilla Firefox browser (needs internet)", None),
            ("tei-restore", "System Restore", "Protect the system with snapshots", ["timeshift-launcher"]),
            ("tei-help", "Help and Support", "Guides for everyday tasks", ["tei-help"]),
        ]
        for icon, title, desc, cmd in items:
            grid.add(self.tile(icon, title, desc, cmd))
        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.add(grid)
        outer.pack_start(sw, True, True, 0)
        bb = Gtk.Box(spacing=8, margin=12, margin_top=4)
        self.chk = Gtk.CheckButton(label=T("Show this window at startup"), active=load_show())
        self.chk.connect("toggled", lambda c: save_show(c.get_active()))
        if not live:
            bb.pack_start(self.chk, False, False, 0)
        close = Gtk.Button(label=T("Close"))
        close.connect("clicked", lambda *_: self.destroy())
        bb.pack_end(close, False, False, 0)
        outer.pack_start(bb, False, False, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()

    def tile(self, icon, title, desc, cmd):
        b = Gtk.Button()
        b.get_style_context().add_class("tei-tile")
        b.set_relief(Gtk.ReliefStyle.NONE)
        h = Gtk.Box(spacing=12)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        h.pack_start(img, False, False, 0)
        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        t = Gtk.Label(label=T(title), xalign=0)
        t.get_style_context().add_class("tei-tile-title")
        d = Gtk.Label(label=T(desc), xalign=0)
        d.set_line_wrap(True)
        d.get_style_context().add_class("tei-tile-desc")
        v.pack_start(t, False, False, 0)
        v.pack_start(d, False, False, 0)
        h.pack_start(v, True, True, 0)
        b.add(h)
        if cmd is None:
            b.connect("clicked", self.install_firefox)
            b.set_sensitive(which(["snap"]) is not None)
        else:
            b.set_sensitive(which(cmd) is not None)
            b.connect("clicked", lambda *_: launch(cmd))
        return b

    def install_firefox(self, btn):
        btn.set_sensitive(False)
        w = Gtk.Window(transient_for=self, modal=True, decorated=False)
        w.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        box = Gtk.Box(spacing=12, margin=18)
        sp = Gtk.Spinner()
        sp.start()
        box.pack_start(sp, False, False, 0)
        box.pack_start(Gtk.Label(label=T("Installing Firefox… this can take a few minutes.")), False, False, 0)
        w.add(box)
        w.show_all()

        def done(rc, out, err):
            w.destroy()
            btn.set_sensitive(True)
            if rc == 0:
                message(self, T("Firefox was installed. You will find it in the Start menu."))
            elif rc not in (126, 127):
                message(self, T("Firefox could not be installed"), T("Check the internet connection and try again.") + "\n\n" + (err or out).strip()[-600:], Gtk.MessageType.ERROR)
        run_async(["pkexec", "snap", "install", "firefox"], done)


if __name__ == "__main__":
    if "--autostart" in sys.argv and not is_live_session() and not load_show():
        sys.exit(0)
    Welcome()
    Gtk.main()
