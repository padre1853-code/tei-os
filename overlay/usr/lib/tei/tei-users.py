#!/usr/bin/python3
"""Tei OS User Accounts — add, remove and manage local users."""
import grp
import os
import pwd
import sys

sys.path.insert(0, "/usr/lib/tei")
from teilib import (Gtk, T, banner, confirm, install_css, message, run_async,  # noqa: E402
                    tr_add)

tr_add({
    "User Accounts": "Conturi utilizator",
    "Add, change or remove the people who use this computer": "Adăugați, modificați sau eliminați persoanele care folosesc acest computer",
    "Administrator": "Administrator",
    "Standard user": "Utilizator standard",
    "Create account…": "Creare cont…",
    "Change password…": "Schimbare parolă…",
    "Make administrator": "Fă administrator",
    "Make standard user": "Fă utilizator standard",
    "Delete account…": "Ștergere cont…",
    "Log in automatically": "Autentificare automată",
    "Create a new account": "Crearea unui cont nou",
    "Full name:": "Nume complet:",
    "User name (for logging in):": "Nume de utilizator (pentru autentificare):",
    "Password:": "Parolă:",
    "Confirm password:": "Confirmare parolă:",
    "This user is an administrator (can install programs and change settings)":
        "Acest utilizator este administrator (poate instala programe și modifica setări)",
    "The passwords do not match.": "Parolele nu coincid.",
    "Please fill in the user name and the password.": "Completați numele de utilizator și parola.",
    "User name: lowercase letters, digits, - and _ ; must start with a letter.":
        "Nume de utilizator: litere mici, cifre, - și _ ; trebuie să înceapă cu o literă.",
    "New password for %s": "Parolă nouă pentru %s",
    "Delete the account %s?": "Ștergeți contul %s?",
    "Keep the user's files in /home": "Păstrează fișierele utilizatorului în /home",
    "The account was created.": "Contul a fost creat.",
    "The password was changed.": "Parola a fost schimbată.",
    "(you)": "(dvs.)",
    "Domain accounts are managed on the domain controller.": "Conturile de domeniu se administrează pe controlerul de domeniu.",
})

HELPER = ["pkexec", "/usr/lib/tei/tei-admin-helper"]


def local_users():
    users = []
    for p in pwd.getpwall():
        if 1000 <= p.pw_uid < 60000 and not p.pw_shell.endswith(("nologin", "false")):
            users.append(p)
    return sorted(users, key=lambda p: p.pw_name)


def is_admin(name):
    try:
        return name in grp.getgrnam("sudo").gr_mem
    except KeyError:
        return False


def autologin_user():
    try:
        for line in open("/etc/lightdm/lightdm.conf.d/60-tei-autologin.conf"):
            if line.startswith("autologin-user="):
                return line.split("=", 1)[1].strip()
    except OSError:
        pass
    return None


class Users(Gtk.Window):
    def __init__(self):
        super().__init__(title=T("User Accounts"))
        self.set_icon_name("tei-users")
        self.set_default_size(640, 500)
        self.set_position(Gtk.WindowPosition.CENTER)
        install_css()
        self.me = pwd.getpwuid(os.getuid()).pw_name
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        outer.pack_start(banner("tei-users", T("User Accounts"), T("Add, change or remove the people who use this computer")), False, False, 0)
        body = Gtk.Box(spacing=12, margin=12)
        outer.pack_start(body, True, True, 0)
        sw = Gtk.ScrolledWindow()
        sw.set_size_request(280, -1)
        sw.set_shadow_type(Gtk.ShadowType.IN)
        self.listbox = Gtk.ListBox()
        self.listbox.connect("row-selected", self.on_select)
        sw.add(self.listbox)
        body.pack_start(sw, False, True, 0)
        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        body.pack_start(right, True, True, 0)
        self.sel_img = Gtk.Image.new_from_icon_name("tei-user", Gtk.IconSize.DIALOG)
        self.sel_img.set_pixel_size(96)
        right.pack_start(self.sel_img, False, False, 0)
        self.sel_name = Gtk.Label()
        right.pack_start(self.sel_name, False, False, 0)
        self.sel_type = Gtk.Label()
        self.sel_type.get_style_context().add_class("tei-muted")
        right.pack_start(self.sel_type, False, False, 0)
        self.b_pass = Gtk.Button(label=T("Change password…"))
        self.b_pass.connect("clicked", self.on_password)
        self.b_admin = Gtk.Button(label=T("Make administrator"))
        self.b_admin.connect("clicked", self.on_admin)
        self.auto = Gtk.CheckButton(label=T("Log in automatically"))
        self.auto_handler = self.auto.connect("toggled", self.on_autologin)
        self.b_del = Gtk.Button(label=T("Delete account…"))
        self.b_del.get_style_context().add_class("destructive-action")
        self.b_del.connect("clicked", self.on_delete)
        for w in (self.b_pass, self.b_admin, self.auto, self.b_del):
            right.pack_start(w, False, False, 0)
        hint = Gtk.Label(label=T("Domain accounts are managed on the domain controller."))
        hint.set_line_wrap(True)
        hint.get_style_context().add_class("tei-muted")
        right.pack_end(hint, False, False, 0)
        bb = Gtk.Box(spacing=8, margin=12, margin_top=0)
        add = Gtk.Button(label=T("Create account…"))
        add.get_style_context().add_class("suggested-action")
        add.connect("clicked", self.on_add)
        bb.pack_start(add, False, False, 0)
        close = Gtk.Button(label=T("Close"))
        close.connect("clicked", lambda *_: self.destroy())
        bb.pack_end(close, False, False, 0)
        outer.pack_start(bb, False, False, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.reload()

    def reload(self, select=None):
        for r in self.listbox.get_children():
            self.listbox.remove(r)
        self.rows = {}
        for p in local_users():
            row = Gtk.ListBoxRow()
            h = Gtk.Box(spacing=10, margin=6)
            img = Gtk.Image.new_from_icon_name("tei-user", Gtk.IconSize.DND)
            img.set_pixel_size(32)
            h.pack_start(img, False, False, 0)
            v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            full = p.pw_gecos.split(",")[0] or p.pw_name
            n = Gtk.Label(xalign=0)
            me = " " + T("(you)") if p.pw_name == self.me else ""
            n.set_markup(f"<b>{GLib_escape(full)}</b>{GLib_escape(me)}")
            v.pack_start(n, False, False, 0)
            t = Gtk.Label(label=f"{p.pw_name} · " + (T("Administrator") if is_admin(p.pw_name) else T("Standard user")), xalign=0)
            t.get_style_context().add_class("tei-muted")
            v.pack_start(t, False, False, 0)
            h.pack_start(v, True, True, 0)
            row.add(h)
            row.user = p
            self.listbox.add(row)
            self.rows[p.pw_name] = row
        self.listbox.show_all()
        target = self.rows.get(select or self.me) or (self.listbox.get_row_at_index(0))
        if target:
            self.listbox.select_row(target)
        else:
            self.on_select(self.listbox, None)

    def selected(self):
        r = self.listbox.get_selected_row()
        return r.user if r else None

    def on_select(self, lb, row):
        u = row.user if row else None
        for w in (self.b_pass, self.b_admin, self.auto, self.b_del):
            w.set_sensitive(u is not None)
        if not u:
            self.sel_name.set_text("")
            self.sel_type.set_text("")
            return
        self.sel_name.set_markup(f"<span size='large' weight='bold'>{GLib_escape(u.pw_gecos.split(',')[0] or u.pw_name)}</span>")
        adm = is_admin(u.pw_name)
        self.sel_type.set_text(u.pw_name + " — " + (T("Administrator") if adm else T("Standard user")))
        self.b_admin.set_label(T("Make standard user") if adm else T("Make administrator"))
        self.b_admin.set_sensitive(not (adm and u.pw_name == self.me))
        self.b_del.set_sensitive(u.pw_name != self.me)
        self.auto.handler_block(self.auto_handler)
        self.auto.set_active(autologin_user() == u.pw_name)
        self.auto.handler_unblock(self.auto_handler)

    # ------------------------------------------------------------ actions
    def helper(self, args, ok_msg=None, password=None, select=None):
        def done(rc, out, err):
            if rc == 0:
                if ok_msg:
                    message(self, ok_msg)
            elif rc not in (126, 127):
                message(self, T("Error"), (err or out).strip(), Gtk.MessageType.ERROR)
            self.reload(select)
        run_async(HELPER + args, done, input_text=(password + "\n") if password is not None else None)

    def password_fields(self, box):
        p1 = Gtk.Entry(visibility=False, activates_default=True, input_purpose=Gtk.InputPurpose.PASSWORD)
        p2 = Gtk.Entry(visibility=False, activates_default=True, input_purpose=Gtk.InputPurpose.PASSWORD)
        box.pack_start(Gtk.Label(label=T("Password:"), xalign=0), False, False, 0)
        box.pack_start(p1, False, False, 0)
        box.pack_start(Gtk.Label(label=T("Confirm password:"), xalign=0), False, False, 0)
        box.pack_start(p2, False, False, 0)
        return p1, p2

    def dialog(self, title):
        d = Gtk.Dialog(title=title, transient_for=self, modal=True)
        d.add_buttons(T("Cancel"), Gtk.ResponseType.CANCEL, T("OK"), Gtk.ResponseType.OK)
        d.set_default_response(Gtk.ResponseType.OK)
        d.set_default_size(400, -1)
        box = d.get_content_area()
        box.set_spacing(6)
        for m in ("top", "start", "end", "bottom"):
            getattr(box, f"set_margin_{m}")(12)
        return d, box

    def on_add(self, *_):
        d, box = self.dialog(T("Create a new account"))
        full = Gtk.Entry(activates_default=True)
        name = Gtk.Entry(activates_default=True)
        box.pack_start(Gtk.Label(label=T("Full name:"), xalign=0), False, False, 0)
        box.pack_start(full, False, False, 0)
        box.pack_start(Gtk.Label(label=T("User name (for logging in):"), xalign=0), False, False, 0)
        box.pack_start(name, False, False, 0)
        hint = Gtk.Label(label=T("User name: lowercase letters, digits, - and _ ; must start with a letter."), xalign=0)
        hint.set_line_wrap(True)
        hint.get_style_context().add_class("tei-muted")
        box.pack_start(hint, False, False, 0)
        p1, p2 = self.password_fields(box)
        adm = Gtk.CheckButton(label=T("This user is an administrator (can install programs and change settings)"))
        box.pack_start(adm, False, False, 6)

        def suggest(e):
            if not name.get_text() or getattr(name, "_auto", False):
                import unicodedata
                s = unicodedata.normalize("NFKD", e.get_text().split(" ")[0].lower())
                s = "".join(c for c in s if c.isalnum() and c.isascii())
                name.set_text(s)
                name._auto = True
        full.connect("changed", suggest)
        name.connect("key-press-event", lambda *_: setattr(name, "_auto", False))
        d.show_all()
        while True:
            r = d.run()
            if r != Gtk.ResponseType.OK:
                d.destroy()
                return
            if not name.get_text() or not p1.get_text():
                message(d, T("Please fill in the user name and the password."), kind=Gtk.MessageType.WARNING)
                continue
            if p1.get_text() != p2.get_text():
                message(d, T("The passwords do not match."), kind=Gtk.MessageType.WARNING)
                continue
            break
        args = ["user-add", name.get_text().strip(), full.get_text().strip(), "1" if adm.get_active() else "0"]
        pw = p1.get_text()
        nm = name.get_text().strip()
        d.destroy()
        self.helper(args, T("The account was created."), pw, select=nm)

    def on_password(self, *_):
        u = self.selected()
        if not u:
            return
        d, box = self.dialog(T("New password for %s") % u.pw_name)
        p1, p2 = self.password_fields(box)
        d.show_all()
        while True:
            r = d.run()
            if r != Gtk.ResponseType.OK:
                d.destroy()
                return
            if not p1.get_text() or p1.get_text() != p2.get_text():
                message(d, T("The passwords do not match."), kind=Gtk.MessageType.WARNING)
                continue
            break
        pw = p1.get_text()
        d.destroy()
        self.helper(["user-passwd", u.pw_name], T("The password was changed."), pw, select=u.pw_name)

    def on_admin(self, *_):
        u = self.selected()
        if u:
            self.helper(["user-admin", u.pw_name, "0" if is_admin(u.pw_name) else "1"], select=u.pw_name)

    def on_autologin(self, cb):
        u = self.selected()
        if u:
            self.helper(["autologin", u.pw_name if cb.get_active() else "none"], select=u.pw_name)

    def on_delete(self, *_):
        u = self.selected()
        if not u:
            return
        d, box = self.dialog(T("Delete the account %s?") % u.pw_name)
        keep = Gtk.CheckButton(label=T("Keep the user's files in /home"), active=True)
        box.pack_start(keep, False, False, 0)
        d.show_all()
        r = d.run()
        k = keep.get_active()
        d.destroy()
        if r == Gtk.ResponseType.OK:
            self.helper(["user-del", u.pw_name, "1" if k else "0"])


def GLib_escape(s):
    from gi.repository import GLib
    return GLib.markup_escape_text(s)


if __name__ == "__main__":
    Users()
    Gtk.main()
