#!/usr/bin/python3
"""Tei OS System Properties — about this computer, computer name, domain, hardware, restore."""
import os
import platform
import re
import subprocess
import sys

sys.path.insert(0, "/usr/lib/tei")
from teilib import (GLib, Gtk, T, banner, install_css, launch, message, run_async,  # noqa: E402
                    tr_add, which)

tr_add({
    "System Properties": "Proprietăți sistem",
    "General": "General",
    "Computer Name": "Nume computer",
    "Hardware": "Hardware",
    "System Restore": "Restaurare sistem",
    "Updates": "Actualizări",
    "System:": "Sistem:",
    "Computer:": "Computer:",
    "Processor": "Procesor",
    "Memory (RAM)": "Memorie (RAM)",
    "Graphics": "Placă video",
    "Kernel": "Kernel",
    "Desktop": "Desktop",
    "Disk": "Disc",
    "free of": "liber din",
    "Detailed information…": "Informații detaliate…",
    "Full computer name:": "Numele complet al computerului:",
    "Domain:": "Domeniu:",
    "Not joined to a domain": "Nu este alăturat unui domeniu",
    "Change name…": "Schimbă numele…",
    "Join a domain…": "Alăturare la domeniu…",
    "Leave domain": "Părăsire domeniu",
    "Computer description used on the network. Windows computers and servers see this name.":
        "Numele cu care acest computer apare în rețea, inclusiv pentru computerele și serverele Windows.",
    "New computer name:": "Noul nume al computerului:",
    "Use letters, digits and hyphens (max. 63 characters).": "Folosiți litere, cifre și cratime (max. 63 de caractere).",
    "The computer name was changed.": "Numele computerului a fost schimbat.",
    "Restart the computer for all programs to see the new name.": "Reporniți computerul pentru ca toate programele să vadă noul nume.",
    "Join an Active Directory domain": "Alăturare la un domeniu Active Directory",
    "Domain name (for example company.local):": "Numele domeniului (de exemplu firma.local):",
    "Domain administrator account:": "Cont de administrator al domeniului:",
    "Password:": "Parolă:",
    "Let domain users log in with short names (without @domain)": "Utilizatorii domeniului se pot autentifica fără sufixul @domeniu",
    "Joining the domain…": "Se face alăturarea la domeniu…",
    "Welcome to the domain": "Bun venit în domeniu",
    "Domain users can now log in on this computer. Use \"Other user\" on the login screen.":
        "Utilizatorii domeniului se pot autentifica acum pe acest computer. Folosiți „Alt utilizator” în ecranul de autentificare.",
    "Could not join the domain": "Alăturarea la domeniu nu a reușit",
    "Leave the domain %s?": "Părăsiți domeniul %s?",
    "Domain users will no longer be able to log in.": "Utilizatorii domeniului nu se vor mai putea autentifica.",
    "Devices and drivers": "Dispozitive și drivere",
    "Disks and partitions": "Discuri și partiții",
    "Printers": "Imprimante",
    "Additional drivers (graphics, Wi-Fi)": "Drivere suplimentare (video, Wi-Fi)",
    "Hardware information": "Informații hardware",
    "System Restore takes snapshots of the system so you can return to an earlier state if an update or a change causes problems.":
        "Restaurarea sistemului salvează instantanee ale sistemului, ca să puteți reveni la o stare anterioară dacă o actualizare sau o modificare creează probleme.",
    "Open System Restore": "Deschide Restaurare sistem",
    "Keep the computer up to date with security fixes and improvements.": "Păstrați computerul la zi cu remedieri de securitate și îmbunătățiri.",
    "Check for updates": "Verifică actualizările",
    "Update settings": "Setări actualizări",
    "Close": "Închide",
    "Working…": "Se lucrează…",
})


def read_os():
    info = {}
    try:
        for line in open("/etc/os-release"):
            k, _, v = line.strip().partition("=")
            info[k] = v.strip('"')
    except OSError:
        pass
    return info


def cpu_name():
    try:
        for line in open("/proc/cpuinfo"):
            if line.startswith("model name"):
                return re.sub(r"\s+", " ", line.split(":", 1)[1]).strip()
    except OSError:
        pass
    return platform.processor() or "—"


def mem_total():
    try:
        for line in open("/proc/meminfo"):
            if line.startswith("MemTotal"):
                kb = int(line.split()[1])
                return f"{kb / 1048576:.1f} GB"
    except OSError:
        pass
    return "—"


def gpu_name():
    try:
        out = subprocess.run(["lspci"], capture_output=True, text=True, timeout=3).stdout
        for line in out.splitlines():
            if re.search(r"VGA|3D|Display", line):
                return line.split(":", 2)[-1].strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return "—"


def disk_usage():
    try:
        st = os.statvfs("/")
        total = st.f_blocks * st.f_frsize / 1e9
        free = st.f_bavail * st.f_frsize / 1e9
        return f"{free:.0f} GB {T('free of')} {total:.0f} GB"
    except OSError:
        return "—"


def current_domain():
    try:
        out = subprocess.run(["realm", "list", "--name-only"], capture_output=True, text=True, timeout=5).stdout.strip()
        return out.splitlines()[0] if out else None
    except (OSError, subprocess.SubprocessError, IndexError):
        return None


class SystemProperties(Gtk.Window):
    def __init__(self, page=0):
        super().__init__(title=T("System Properties"))
        self.set_icon_name("tei-system-info")
        self.set_default_size(560, 560)
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_resizable(False)
        install_css()
        osr = read_os()
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        nb = Gtk.Notebook(margin=10)
        outer.pack_start(nb, True, True, 0)
        nb.append_page(self.page_general(osr), Gtk.Label(label=T("General")))
        nb.append_page(self.page_name(), Gtk.Label(label=T("Computer Name")))
        nb.append_page(self.page_hardware(), Gtk.Label(label=T("Hardware")))
        nb.append_page(self.page_restore(), Gtk.Label(label=T("System Restore")))
        nb.append_page(self.page_updates(), Gtk.Label(label=T("Updates")))
        bb = Gtk.ButtonBox(layout_style=Gtk.ButtonBoxStyle.END, margin=10, margin_top=0)
        close = Gtk.Button(label=T("Close"))
        close.connect("clicked", lambda *_: self.destroy())
        bb.add(close)
        outer.pack_start(bb, False, False, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        nb.set_current_page(page)

    # ------------------------------------------------------------ pages
    def page_general(self, osr):
        g = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10, margin=16)
        top = Gtk.Box(spacing=18)
        img = Gtk.Image.new_from_icon_name("tei-start", Gtk.IconSize.DIALOG)
        img.set_pixel_size(112)
        top.pack_start(img, False, False, 0)
        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        v.set_valign(Gtk.Align.CENTER)
        name = Gtk.Label(xalign=0)
        name.set_markup(f"<span size='x-large' weight='bold' foreground='#135A64'>{GLib.markup_escape_text(osr.get('NAME', 'Tei OS'))}</span>")
        v.pack_start(name, False, False, 0)
        ver = Gtk.Label(label=osr.get("PRETTY_NAME", ""), xalign=0)
        ver.set_line_wrap(True)
        v.pack_start(ver, False, False, 0)
        top.pack_start(v, True, True, 0)
        g.pack_start(top, False, False, 0)
        g.pack_start(Gtk.Separator(), False, False, 4)
        grid = Gtk.Grid(column_spacing=14, row_spacing=7)
        rows = [
            (T("Processor"), cpu_name()),
            (T("Memory (RAM)"), mem_total()),
            (T("Graphics"), gpu_name()),
            (T("Disk"), disk_usage()),
            (T("Kernel"), platform.release() + " (" + platform.machine() + ")"),
            (T("Desktop"), "Xfce " + self.xfce_version()),
        ]
        for i, (k, val) in enumerate(rows):
            lk = Gtk.Label(label=k + ":", xalign=1)
            lk.get_style_context().add_class("tei-muted")
            lv = Gtk.Label(label=val, xalign=0, selectable=True)
            lv.set_line_wrap(True)
            lv.set_max_width_chars(46)
            grid.attach(lk, 0, i, 1, 1)
            grid.attach(lv, 1, i, 1, 1)
        g.pack_start(grid, False, False, 0)
        btn = Gtk.Button(label=T("Detailed information…"))
        btn.set_halign(Gtk.Align.START)
        btn.set_sensitive(which(["hardinfo2"]) is not None)
        btn.connect("clicked", lambda *_: launch(["hardinfo2"]))
        g.pack_end(btn, False, False, 0)
        return g

    @staticmethod
    def xfce_version():
        try:
            out = subprocess.run(["xfce4-session", "--version"], capture_output=True, text=True, timeout=3).stdout
            m = re.search(r"(\d+\.\d+(\.\d+)?)", out)
            return m.group(1) if m else ""
        except (OSError, subprocess.SubprocessError):
            return ""

    def page_name(self):
        g = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=16)
        top = Gtk.Box(spacing=14)
        img = Gtk.Image.new_from_icon_name("tei-computer", Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        top.pack_start(img, False, False, 0)
        d = Gtk.Label(label=T("Computer description used on the network. Windows computers and servers see this name."), xalign=0)
        d.set_line_wrap(True)
        top.pack_start(d, True, True, 0)
        g.pack_start(top, False, False, 0)
        grid = Gtk.Grid(column_spacing=12, row_spacing=10)
        grid.attach(Gtk.Label(label=T("Full computer name:"), xalign=1), 0, 0, 1, 1)
        self.host_lbl = Gtk.Label(label=platform.node(), xalign=0, selectable=True)
        self.host_lbl.get_style_context().add_class("tei-section")
        grid.attach(self.host_lbl, 1, 0, 1, 1)
        grid.attach(Gtk.Label(label=T("Domain:"), xalign=1), 0, 1, 1, 1)
        self.dom_lbl = Gtk.Label(xalign=0, selectable=True)
        grid.attach(self.dom_lbl, 1, 1, 1, 1)
        g.pack_start(grid, False, False, 6)
        bb = Gtk.Box(spacing=8)
        b1 = Gtk.Button(label=T("Change name…"))
        b1.connect("clicked", self.on_rename)
        self.join_btn = Gtk.Button(label=T("Join a domain…"))
        self.join_btn.connect("clicked", self.on_join)
        self.leave_btn = Gtk.Button(label=T("Leave domain"))
        self.leave_btn.connect("clicked", self.on_leave)
        for b in (b1, self.join_btn, self.leave_btn):
            bb.pack_start(b, False, False, 0)
        g.pack_start(bb, False, False, 0)
        self.refresh_domain()
        return g

    def refresh_domain(self):
        dom = current_domain()
        self.domain = dom
        self.dom_lbl.set_text(dom if dom else T("Not joined to a domain"))
        self.join_btn.set_sensitive(dom is None and which(["realm"]) is not None)
        self.leave_btn.set_sensitive(dom is not None)

    def page_hardware(self):
        g = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8, margin=16)
        for label, icon, cmd in [
            (T("Disks and partitions"), "tei-disks", ["gnome-disks"]),
            (T("Printers"), "tei-printer", ["system-config-printer"]),
            (T("Additional drivers (graphics, Wi-Fi)"), "tei-programs", ["software-properties-gtk", "--open-tab=4"]),
            (T("Hardware information"), "tei-system-info", ["hardinfo2"]),
        ]:
            g.pack_start(self.action_row(label, icon, cmd), False, False, 0)
        return g

    def page_restore(self):
        g = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=16)
        top = Gtk.Box(spacing=14)
        img = Gtk.Image.new_from_icon_name("tei-restore", Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        top.pack_start(img, False, False, 0)
        lbl = Gtk.Label(label=T("System Restore takes snapshots of the system so you can return to an earlier state if an update or a change causes problems."), xalign=0)
        lbl.set_line_wrap(True)
        top.pack_start(lbl, True, True, 0)
        g.pack_start(top, False, False, 0)
        b = Gtk.Button(label=T("Open System Restore"))
        b.set_halign(Gtk.Align.START)
        b.connect("clicked", lambda *_: launch(["timeshift-launcher"]))
        b.set_sensitive(which(["timeshift-launcher"]) is not None)
        g.pack_start(b, False, False, 0)
        return g

    def page_updates(self):
        g = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12, margin=16)
        top = Gtk.Box(spacing=14)
        img = Gtk.Image.new_from_icon_name("tei-updates", Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        top.pack_start(img, False, False, 0)
        lbl = Gtk.Label(label=T("Keep the computer up to date with security fixes and improvements."), xalign=0)
        lbl.set_line_wrap(True)
        top.pack_start(lbl, True, True, 0)
        g.pack_start(top, False, False, 0)
        g.pack_start(self.action_row(T("Check for updates"), "tei-updates", ["update-manager"]), False, False, 0)
        g.pack_start(self.action_row(T("Update settings"), "tei-settings-editor", ["software-properties-gtk", "--open-tab=2"]), False, False, 0)
        return g

    def action_row(self, label, icon, cmd):
        b = Gtk.Button()
        b.get_style_context().add_class("tei-tile")
        b.set_relief(Gtk.ReliefStyle.NONE)
        h = Gtk.Box(spacing=12)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DND)
        img.set_pixel_size(32)
        h.pack_start(img, False, False, 0)
        lab = Gtk.Label(label=label, xalign=0)
        lab.get_style_context().add_class("tei-tile-title")
        h.pack_start(lab, True, True, 0)
        b.add(h)
        b.set_sensitive(which(cmd) is not None)
        b.connect("clicked", lambda *_: launch(cmd))
        return b

    # ------------------------------------------------------------ actions
    def on_rename(self, *_):
        d = Gtk.Dialog(title=T("Computer Name"), transient_for=self, modal=True)
        d.add_buttons(T("Cancel"), Gtk.ResponseType.CANCEL, T("OK"), Gtk.ResponseType.OK)
        d.set_default_response(Gtk.ResponseType.OK)
        box = d.get_content_area()
        box.set_spacing(8)
        box.set_margin_top(12)
        box.set_margin_start(12)
        box.set_margin_end(12)
        box.pack_start(Gtk.Label(label=T("New computer name:"), xalign=0), False, False, 0)
        e = Gtk.Entry(text=platform.node(), activates_default=True, max_length=63)
        box.pack_start(e, False, False, 0)
        hint = Gtk.Label(label=T("Use letters, digits and hyphens (max. 63 characters)."), xalign=0)
        hint.get_style_context().add_class("tei-muted")
        box.pack_start(hint, False, False, 0)
        d.show_all()
        r = d.run()
        new = e.get_text().strip()
        d.destroy()
        if r != Gtk.ResponseType.OK or not new or new == platform.node():
            return

        def done(rc, out, err):
            if rc == 0:
                self.host_lbl.set_text(new)
                message(self, T("The computer name was changed."), T("Restart the computer for all programs to see the new name."))
            elif rc not in (126, 127):
                message(self, T("Error"), err.strip() or out.strip(), Gtk.MessageType.ERROR)
        run_async(["pkexec", "/usr/lib/tei/tei-admin-helper", "hostname", new], done)

    def on_join(self, *_):
        d = Gtk.Dialog(title=T("Join an Active Directory domain"), transient_for=self, modal=True)
        d.add_buttons(T("Cancel"), Gtk.ResponseType.CANCEL, T("OK"), Gtk.ResponseType.OK)
        d.set_default_response(Gtk.ResponseType.OK)
        d.set_default_size(420, -1)
        box = d.get_content_area()
        box.set_spacing(6)
        for m in ("top", "start", "end"):
            getattr(box, f"set_margin_{m}")(12)
        dom = Gtk.Entry(activates_default=True)
        usr = Gtk.Entry(text="Administrator", activates_default=True)
        pw = Gtk.Entry(visibility=False, activates_default=True, input_purpose=Gtk.InputPurpose.PASSWORD)
        for lab, w in ((T("Domain name (for example company.local):"), dom),
                       (T("Domain administrator account:"), usr), (T("Password:"), pw)):
            box.pack_start(Gtk.Label(label=lab, xalign=0), False, False, 0)
            box.pack_start(w, False, False, 0)
        short = Gtk.CheckButton(label=T("Let domain users log in with short names (without @domain)"), active=True)
        box.pack_start(short, False, False, 6)
        d.show_all()
        r = d.run()
        domain, user, password = dom.get_text().strip(), usr.get_text().strip(), pw.get_text()
        use_short = "1" if short.get_active() else "0"
        d.destroy()
        if r != Gtk.ResponseType.OK or not domain or not user:
            return
        spinner = self.busy(T("Joining the domain…"))

        def done(rc, out, err):
            spinner.destroy()
            self.refresh_domain()
            if rc == 0:
                message(self, T("Welcome to the domain") + " " + domain, T("Domain users can now log in on this computer. Use \"Other user\" on the login screen."))
            elif rc not in (126, 127):
                message(self, T("Could not join the domain"), (err or out).strip()[-1200:], Gtk.MessageType.ERROR)
        run_async(["pkexec", "/usr/lib/tei/tei-admin-helper", "domain-join", domain, user, use_short], done,
                  input_text=password + "\n")

    def on_leave(self, *_):
        if not self.domain:
            return
        from teilib import confirm
        if not confirm(self, T("Leave the domain %s?") % self.domain, T("Domain users will no longer be able to log in.")):
            return

        def done(rc, out, err):
            self.refresh_domain()
            if rc not in (0, 126, 127):
                message(self, T("Error"), (err or out).strip(), Gtk.MessageType.ERROR)
        run_async(["pkexec", "/usr/lib/tei/tei-admin-helper", "domain-leave", self.domain], done)

    def busy(self, text):
        w = Gtk.Window(transient_for=self, modal=True, decorated=False)
        w.set_position(Gtk.WindowPosition.CENTER_ON_PARENT)
        b = Gtk.Box(spacing=12, margin=18)
        sp = Gtk.Spinner()
        sp.start()
        b.pack_start(sp, False, False, 0)
        b.pack_start(Gtk.Label(label=text), False, False, 0)
        w.add(b)
        w.show_all()
        return w


if __name__ == "__main__":
    page = 1 if "--computer-name" in sys.argv else 0
    SystemProperties(page)
    Gtk.main()
