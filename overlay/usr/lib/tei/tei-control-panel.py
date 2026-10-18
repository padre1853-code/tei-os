#!/usr/bin/python3
"""Tei OS Control Panel — every system setting in one window, by category or as one list."""
import sys

sys.path.insert(0, "/usr/lib/tei")
from teilib import Gtk, T, banner, install_css, launch, message, tr_add, which  # noqa: E402,F401

tr_add({
    "Control Panel": "Panou de control",
    "Adjust your computer's settings": "Ajustați setările computerului",
    "Pick a category": "Alegeți o categorie",
    "All items": "Toate elementele",
    "Categories": "Categorii",
    "Search settings": "Căutare setări",
    # categories
    "Appearance and Personalization": "Aspect și personalizare",
    "Themes, wallpaper, screen resolution, taskbar": "Teme, fundal, rezoluția ecranului, bara de activități",
    "Network and Internet": "Rețea și internet",
    "Connections, Bluetooth, firewall, remote desktop": "Conexiuni, Bluetooth, firewall, desktop la distanță",
    "Hardware and Sound": "Hardware și sunet",
    "Sound, printers, keyboard, mouse, power, disks": "Sunet, imprimante, tastatură, mouse, energie, discuri",
    "User Accounts": "Conturi utilizator",
    "Add users, change passwords, join a domain": "Adăugare utilizatori, parole, alăturare la domeniu",
    "Programs": "Programe",
    "Install and remove programs, updates, defaults": "Instalare și eliminare programe, actualizări, implicite",
    "System and Security": "Sistem și securitate",
    "System information, restore, cleanup, task manager": "Informații sistem, restaurare, curățare, activități",
    "Clock, Language and Region": "Ceas, limbă și regiune",
    "Date, time, time zone, language, keyboard layout": "Dată, oră, fus orar, limbă, aranjament tastatură",
    "Accessibility": "Accesibilitate",
    "Make the computer easier to see, hear and use": "Ușurați vederea, auzul și utilizarea computerului",
    # items
    "Theme and Colours": "Temă și culori",
    "Desktop Background": "Fundal desktop",
    "Display": "Ecran și rezoluție",
    "Taskbar": "Bara de activități",
    "Windows": "Ferestre",
    "Windows (advanced)": "Ferestre (avansat)",
    "Screensaver and Lock": "Protecție ecran și blocare",
    "Notifications": "Notificări",
    "Login Screen": "Ecranul de autentificare",
    "Network Connections": "Conexiuni de rețea",
    "Bluetooth": "Bluetooth",
    "Firewall": "Firewall",
    "Remote Desktop": "Desktop la distanță",
    "Sound": "Sunet",
    "Printers": "Imprimante",
    "Scanner": "Scaner",
    "Keyboard": "Tastatură",
    "Mouse and Touchpad": "Mouse și touchpad",
    "Power Options": "Opțiuni de alimentare",
    "Disks": "Discuri",
    "Partition Editor": "Editor de partiții",
    "Removable Drives": "Unități amovibile",
    "Additional Drivers": "Drivere suplimentare",
    "User Accounts ": "Conturi utilizator",
    "Domain and Computer Name": "Domeniu și nume computer",
    "Add or Remove Programs": "Adăugare sau eliminare programe",
    "Software Updates": "Actualizări software",
    "Software Sources": "Surse de software",
    "Default Applications": "Aplicații implicite",
    "Startup Applications": "Aplicații la pornire",
    "Windows Programs (Wine)": "Programe Windows (Wine)",
    "System": "Sistem",
    "Hardware Information": "Informații hardware",
    "Task Manager": "Manager de activități",
    "System Restore": "Restaurare sistem",
    "Disk Cleanup": "Curățare disc",
    "Settings Editor": "Editor de setări",
    "Date and Time": "Dată și oră",
    "Language and Region": "Limbă și regiune",
    "Keyboard Layout": "Aranjament tastatură",
    "Accessibility Options": "Opțiuni de accesibilitate",
    "On-Screen Keyboard": "Tastatură pe ecran",
    "Event Sounds": "Sunete de sistem",
    "Menu Editor": "Editor meniu Start",
})


CATEGORIES = [
    ("appearance", "Appearance and Personalization", "Themes, wallpaper, screen resolution, taskbar", "tei-appearance"),
    ("network", "Network and Internet", "Connections, Bluetooth, firewall, remote desktop", "tei-network-settings"),
    ("hardware", "Hardware and Sound", "Sound, printers, keyboard, mouse, power, disks", "tei-sound"),
    ("users", "User Accounts", "Add users, change passwords, join a domain", "tei-users"),
    ("programs", "Programs", "Install and remove programs, updates, defaults", "tei-programs"),
    ("system", "System and Security", "System information, restore, cleanup, task manager", "tei-system-info"),
    ("clock", "Clock, Language and Region", "Date, time, time zone, language, keyboard layout", "tei-datetime"),
    ("access", "Accessibility", "Make the computer easier to see, hear and use", "tei-accessibility"),
]

# (category, name, icon, command)
ITEMS = [
    ("appearance", "Theme and Colours", "tei-appearance", ["xfce4-appearance-settings"]),
    ("appearance", "Desktop Background", "tei-wallpaper", ["xfdesktop-settings"]),
    ("appearance", "Display", "tei-display", ["xfce4-display-settings"]),
    ("appearance", "Taskbar", "tei-taskbar", ["xfce4-panel", "--preferences"]),
    ("appearance", "Windows", "tei-windows", ["xfwm4-settings"]),
    ("appearance", "Windows (advanced)", "tei-windows", ["xfwm4-tweaks-settings"]),
    ("appearance", "Screensaver and Lock", "tei-screensaver", ["xfce4-screensaver-preferences"]),
    ("appearance", "Notifications", "tei-notifications", ["xfce4-notifyd-config"]),
    ("appearance", "Login Screen", "tei-login-settings", ["lightdm-gtk-greeter-settings-pkexec"]),
    ("appearance", "Menu Editor", "tei-start", ["menulibre"]),
    ("network", "Network Connections", "tei-network-settings", ["nm-connection-editor"]),
    ("network", "Bluetooth", "tei-bluetooth", ["blueman-manager"]),
    ("network", "Firewall", "tei-firewall", ["gufw"]),
    ("network", "Remote Desktop", "tei-remote-desktop", ["remmina"]),
    ("hardware", "Sound", "tei-sound", ["pavucontrol"]),
    ("hardware", "Printers", "tei-printer", ["system-config-printer"]),
    ("hardware", "Scanner", "tei-scanner", ["simple-scan"]),
    ("hardware", "Keyboard", "tei-keyboard", ["xfce4-keyboard-settings"]),
    ("hardware", "Mouse and Touchpad", "tei-mouse", ["xfce4-mouse-settings"]),
    ("hardware", "Power Options", "tei-power", ["xfce4-power-manager-settings"]),
    ("hardware", "Disks", "tei-disks", ["gnome-disks"]),
    ("hardware", "Partition Editor", "tei-disks", ["gparted"]),
    ("hardware", "Removable Drives", "tei-drive-removable", ["thunar-volman-settings"]),
    ("hardware", "Additional Drivers", "tei-programs", ["software-properties-gtk", "--open-tab=4"]),
    ("hardware", "Event Sounds", "tei-sound", ["xfce4-appearance-settings"]),
    ("users", "User Accounts ", "tei-users", ["tei-users"]),
    ("users", "Domain and Computer Name", "tei-domain", ["tei-system-properties", "--computer-name"]),
    ("programs", "Add or Remove Programs", "tei-programs", ["synaptic-pkexec"]),
    ("programs", "Software Updates", "tei-updates", ["update-manager"]),
    ("programs", "Software Sources", "tei-updates", ["software-properties-gtk"]),
    ("programs", "Default Applications", "tei-default-apps", ["xfce4-mime-settings"]),
    ("programs", "Startup Applications", "tei-startup", ["xfce4-session-settings"]),
    ("programs", "Windows Programs (Wine)", "tei-wine", ["winecfg"]),
    ("system", "System", "tei-system-info", ["tei-system-properties"]),
    ("system", "Hardware Information", "tei-system-info", ["hardinfo2"]),
    ("system", "Task Manager", "tei-task-manager", ["xfce4-taskmanager"]),
    ("system", "System Restore", "tei-restore", ["timeshift-launcher"]),
    ("system", "Disk Cleanup", "tei-cleanup", ["bleachbit"]),
    ("system", "Firewall", "tei-firewall", ["gufw"]),
    ("system", "Settings Editor", "tei-settings-editor", ["xfce4-settings-editor"]),
    ("clock", "Date and Time", "tei-datetime", ["tei-datetime"]),
    ("clock", "Language and Region", "tei-language", ["gnome-language-selector"]),
    ("clock", "Keyboard Layout", "tei-keyboard", ["xfce4-keyboard-settings"]),
    ("access", "Accessibility Options", "tei-accessibility", ["xfce4-accessibility-settings"]),
    ("access", "On-Screen Keyboard", "tei-keyboard", ["onboard"]),
]


class ControlPanel(Gtk.Window):
    def __init__(self):
        super().__init__(title=T("Control Panel"))
        self.set_icon_name("tei-control-panel")
        self.set_default_size(880, 600)
        self.set_position(Gtk.WindowPosition.CENTER)
        install_css()
        outer = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.add(outer)
        outer.pack_start(banner("tei-control-panel", T("Control Panel"), T("Adjust your computer's settings")), False, False, 0)

        bar = Gtk.Box(spacing=8, margin=10)
        self.back_btn = Gtk.Button.new_from_icon_name("go-previous", Gtk.IconSize.BUTTON)
        self.back_btn.set_tooltip_text(T("Back"))
        self.back_btn.connect("clicked", lambda *_: self.show_categories())
        bar.pack_start(self.back_btn, False, False, 0)
        self.crumb = Gtk.Label(xalign=0)
        self.crumb.get_style_context().add_class("tei-section")
        bar.pack_start(self.crumb, True, True, 0)
        self.view_cat = Gtk.RadioButton.new_with_label(None, T("Categories"))
        self.view_all = Gtk.RadioButton.new_with_label_from_widget(self.view_cat, T("All items"))
        for rb in (self.view_cat, self.view_all):
            rb.set_mode(False)
        self.view_cat.connect("toggled", self.on_view)
        hb = Gtk.Box()
        hb.get_style_context().add_class("linked")
        hb.pack_start(self.view_cat, False, False, 0)
        hb.pack_start(self.view_all, False, False, 0)
        bar.pack_start(hb, False, False, 0)
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text(T("Search settings"))
        self.search.set_width_chars(22)
        self.search.connect("search-changed", self.on_search)
        bar.pack_start(self.search, False, False, 0)
        outer.pack_start(bar, False, False, 0)
        outer.pack_start(Gtk.Separator(), False, False, 0)

        sw = Gtk.ScrolledWindow()
        sw.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        sw.get_style_context().add_class("tei-body")
        self.flow = Gtk.FlowBox()
        self.flow.set_selection_mode(Gtk.SelectionMode.NONE)
        self.flow.set_homogeneous(True)
        self.flow.set_valign(Gtk.Align.START)
        self.flow.set_row_spacing(6)
        self.flow.set_column_spacing(6)
        self.flow.set_margin_top(12)
        self.flow.set_margin_bottom(12)
        self.flow.set_margin_start(12)
        self.flow.set_margin_end(12)
        sw.add(self.flow)
        outer.pack_start(sw, True, True, 0)
        self.connect("destroy", Gtk.main_quit)
        self.show_all()
        self.show_categories()

    # ---------------------------------------------------------------- views
    def clear(self):
        for c in self.flow.get_children():
            self.flow.remove(c)

    def show_categories(self):
        self.search.set_text("")
        self.clear()
        self.back_btn.set_sensitive(False)
        self.crumb.set_text(T("Pick a category"))
        self.flow.set_max_children_per_line(2)
        self.flow.set_min_children_per_line(1)
        for key, name, desc, icon in CATEGORIES:
            self.flow.add(self.category_tile(key, name, desc, icon))
        self.flow.show_all()

    def show_items(self, items, title):
        self.clear()
        self.crumb.set_text(title)
        self.flow.set_max_children_per_line(6)
        self.flow.set_min_children_per_line(2)
        for (_cat, name, icon, cmd) in items:
            self.flow.add(self.item_tile(name, icon, cmd))
        self.flow.show_all()

    def category_tile(self, key, name, desc, icon):
        btn = Gtk.Button()
        btn.get_style_context().add_class("tei-tile")
        btn.set_relief(Gtk.ReliefStyle.NONE)
        box = Gtk.Box(spacing=12)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        box.pack_start(img, False, False, 0)
        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
        t = Gtk.Label(label=T(name), xalign=0)
        t.get_style_context().add_class("tei-tile-title")
        d = Gtk.Label(label=T(desc), xalign=0)
        d.set_line_wrap(True)
        d.set_max_width_chars(40)
        d.get_style_context().add_class("tei-tile-desc")
        v.pack_start(t, False, False, 0)
        v.pack_start(d, False, False, 0)
        box.pack_start(v, True, True, 0)
        btn.add(box)
        btn.connect("clicked", lambda *_: self.open_category(key, name))
        return btn

    def item_tile(self, name, icon, cmd):
        btn = Gtk.Button()
        btn.get_style_context().add_class("tei-tile")
        btn.set_relief(Gtk.ReliefStyle.NONE)
        v = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        img = Gtk.Image.new_from_icon_name(icon, Gtk.IconSize.DIALOG)
        img.set_pixel_size(48)
        v.pack_start(img, False, False, 0)
        lbl = Gtk.Label(label=T(name).strip())
        lbl.set_line_wrap(True)
        lbl.set_justify(Gtk.Justification.CENTER)
        lbl.set_max_width_chars(16)
        v.pack_start(lbl, False, False, 0)
        btn.add(v)
        ok = which(cmd) is not None
        btn.set_sensitive(ok)
        btn.set_tooltip_text(T(name).strip() if ok else T("This component is not installed."))
        btn.connect("clicked", lambda *_: launch(cmd))
        return btn

    # ---------------------------------------------------------------- handlers
    def open_category(self, key, name):
        self.back_btn.set_sensitive(True)
        self.show_items([i for i in ITEMS if i[0] == key], T(name))

    def on_view(self, rb):
        if self.view_cat.get_active():
            self.show_categories()
        else:
            self.back_btn.set_sensitive(False)
            seen, items = set(), []
            for it in sorted(ITEMS, key=lambda i: T(i[1]).strip().lower()):
                k = T(it[1]).strip()
                if k not in seen:
                    seen.add(k)
                    items.append(it)
            self.show_items(items, T("All items"))

    def on_search(self, entry):
        q = entry.get_text().strip().lower()
        if not q:
            self.on_view(None)
            return
        self.back_btn.set_sensitive(True)
        res = [i for i in ITEMS if q in T(i[1]).lower() or q in i[1].lower()]
        seen, items = set(), []
        for it in res:
            if T(it[1]).strip() not in seen:
                seen.add(T(it[1]).strip())
                items.append(it)
        self.show_items(items, T("Search") + ": " + entry.get_text())


if __name__ == "__main__":
    ControlPanel()
    Gtk.main()
