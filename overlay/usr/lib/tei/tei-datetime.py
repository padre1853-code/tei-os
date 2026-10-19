#!/usr/bin/python3
"""WinLow XP Date and Time — time zone, automatic time, manual date/time (systemd-timedated)."""
import subprocess
import sys
from datetime import datetime

sys.path.insert(0, "/usr/lib/tei")
from teilib import GLib, Gtk, T, banner, install_css, message, run_async, tr_add  # noqa: E402

tr_add({
    "Date and Time": "Dată și oră",
    "Set the date, the time and the time zone": "Setați data, ora și fusul orar",
    "Time zone:": "Fus orar:",
    "Set the time automatically from the internet": "Setează ora automat de pe internet",
    "Date:": "Data:",
    "Time:": "Ora:",
    "Apply": "Aplică",
    "Current time": "Ora curentă",
    "The settings were saved.": "Setările au fost salvate.",
    "Hardware clock uses local time (needed only when dual-booting with Windows)":
        "Ceasul hardware folosește ora locală (necesar doar alături de Windows pe același computer)",
})


def tdctl(*args):
    try:
        return subprocess.run(["timedatectl", *args], capture_output=True, text=True, timeout=5).stdout
    except (OSError, subprocess.SubprocessError):
        return ""


def status():
    out = tdctl("show")
    d = {}
    for line in out.splitlines():
        k, _, v = line.partition("=")
        d[k] = v
    return d


class DateTime(Gtk.Window):
    def __init__(self):
        super().__init__(title=T("Date and Time"))
        self.set_icon_name("tei-datetime")
        self.set_default_size(520, 520)
        self.set_position(Gtk.WindowPosition.CENTER)
        install_css()
        st = status()
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        outer.pack_start(banner("tei-datetime", T("Date and Time"), T("Set the date, the time and the time zone")), False, False, 0)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=14)
        outer.pack_start(body, True, True, 0)

        self.clock = Gtk.Label()
        body.pack_start(self.clock, False, False, 0)
        GLib.timeout_add_seconds(1, self.tick)
        self.tick()

        body.pack_start(Gtk.Label(label=T("Time zone:"), xalign=0), False, False, 0)
        self.tz = Gtk.ComboBoxText.new_with_entry()
        zones = tdctl("list-timezones").split()
        for z in zones:
            self.tz.append_text(z)
        comp = Gtk.EntryCompletion()
        store = Gtk.ListStore(str)
        for z in zones:
            store.append([z])
        comp.set_model(store)
        comp.set_text_column(0)
        comp.set_match_func(lambda c, key, it: key.lower() in store[it][0].lower())
        self.tz.get_child().set_completion(comp)
        self.tz.get_child().set_text(st.get("Timezone", "Europe/Bucharest"))
        body.pack_start(self.tz, False, False, 0)

        self.ntp = Gtk.CheckButton(label=T("Set the time automatically from the internet"))
        self.ntp.set_active(st.get("NTP", "yes") == "yes")
        self.ntp.connect("toggled", self.on_ntp)
        body.pack_start(self.ntp, False, False, 6)

        self.manual = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.cal = Gtk.Calendar()
        self.manual.pack_start(Gtk.Label(label=T("Date:"), xalign=0), False, False, 0)
        self.manual.pack_start(self.cal, False, False, 0)
        hb = Gtk.Box(spacing=6)
        hb.pack_start(Gtk.Label(label=T("Time:")), False, False, 0)
        now = datetime.now()
        self.h = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.m = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.s = Gtk.SpinButton.new_with_range(0, 59, 1)
        for sb, v in ((self.h, now.hour), (self.m, now.minute), (self.s, now.second)):
            sb.set_value(v)
            sb.set_wrap(True)
            sb.set_numeric(True)
            hb.pack_start(sb, False, False, 0)
        self.manual.pack_start(hb, False, False, 0)
        body.pack_start(self.manual, False, False, 0)
        self.rtc = Gtk.CheckButton(label=T("Hardware clock uses local time (needed only when dual-booting with Windows)"))
        self.rtc.set_active(st.get("LocalRTC", "no") == "yes")
        body.pack_start(self.rtc, False, False, 0)
        self.on_ntp(self.ntp)

        bb = Gtk.Box(spacing=8, margin=12, margin_top=0)
        apply = Gtk.Button(label=T("Apply"))
        apply.get_style_context().add_class("suggested-action")
        apply.connect("clicked", self.on_apply)
        close = Gtk.Button(label=T("Close"))
        close.connect("clicked", lambda *_: self.destroy())
        bb.pack_end(close, False, False, 0)
        bb.pack_end(apply, False, False, 0)
        outer.pack_start(bb, False, False, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.on_ntp(self.ntp)

    def tick(self):
        self.clock.set_markup(f"<span size='xx-large' weight='bold' foreground='#135A64'>{datetime.now():%H:%M:%S}</span>\n"
                              f"<span foreground='#4A5759'>{datetime.now():%A, %d %B %Y}</span>")
        self.clock.set_justify(Gtk.Justification.CENTER)
        return True

    def on_ntp(self, cb):
        self.manual.set_sensitive(not cb.get_active())

    def on_apply(self, *_):
        st = status()
        cmds = []
        tz = self.tz.get_child().get_text().strip()
        if tz and tz != st.get("Timezone"):
            cmds.append(["timedatectl", "set-timezone", tz])
        rtc = "true" if self.rtc.get_active() else "false"
        if (st.get("LocalRTC") == "yes") != self.rtc.get_active():
            cmds.append(["timedatectl", "set-local-rtc", rtc])
        want_ntp = self.ntp.get_active()
        if (st.get("NTP") == "yes") != want_ntp:
            cmds.append(["timedatectl", "set-ntp", "true" if want_ntp else "false"])
        if not want_ntp:
            y, mo, d = self.cal.get_date()
            cmds.append(["timedatectl", "set-time",
                         f"{y:04d}-{mo + 1:02d}-{d:02d} {int(self.h.get_value()):02d}:{int(self.m.get_value()):02d}:{int(self.s.get_value()):02d}"])
        self.run_chain(cmds)

    def run_chain(self, cmds):
        if not cmds:
            message(self, T("The settings were saved."))
            return

        def done(rc, out, err):
            if rc != 0:
                message(self, T("Error"), (err or out).strip(), Gtk.MessageType.ERROR)
                return
            self.run_chain(cmds[1:])
        run_async(cmds[0], done)


if __name__ == "__main__":
    DateTime()
    Gtk.main()
