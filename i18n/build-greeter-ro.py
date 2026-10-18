#!/usr/bin/env python3
"""Complete Romanian translation for lightdm-gtk-greeter (upstream ro.po covers only a few strings).
Usage: build-greeter-ro.py <lightdm-gtk-greeter-source> <overlay>
Writes <overlay>/usr/share/locale-langpack/ro/LC_MESSAGES/lightdm-gtk-greeter.mo — Ubuntu's gettext
looks in locale-langpack first, so no package file is replaced."""
import os
import sys

import polib

src, overlay = sys.argv[1], sys.argv[2]
RO = {
    "Shut Down": "Oprire",
    "Are you sure you want to close all programs and shut down the computer?": "Sigur doriți să închideți toate programele și să opriți calculatorul?",
    "Unlock": "Deblocare",
    "Log In": "Autentificare",
    "Failed to start session": "Sesiunea nu a putut porni",
    "Other": "Altul",
    "Guest Session": "Sesiune pentru oaspeți",
    "Your password is incorrect. Please try again.": "Parola este greșită. Încercați din nou.",
    "Failed to authenticate": "Autentificarea a eșuat",
    "Other...": "Alt utilizator…",
    "Shut Down...": "Oprire…",
    "Large Text": "Text mare",
    "High Contrast": "Contrast ridicat",
    "On Screen Keyboard": "Tastatură pe ecran",
    "Screen Reader": "Cititor de ecran",
    "OK": "OK",
    "Enter your username": "Introduceți numele de utilizator",
    "Enter your password": "Introduceți parola",
}
PLURAL = {
    "Warning: There is still %d user logged in.": ["Atenție: încă %d utilizator este autentificat.",
                                                    "Atenție: încă %d utilizatori sunt autentificați.",
                                                    "Atenție: încă %d de utilizatori sunt autentificați."],
}
pot = polib.pofile(os.path.join(src, "po", "lightdm-gtk-greeter.pot"))
old = {e.msgid: e for e in polib.pofile(os.path.join(src, "po", "ro.po")) if e.translated()}
po = polib.POFile()
po.metadata = {"Content-Type": "text/plain; charset=UTF-8", "Language": "ro",
               "Plural-Forms": "nplurals=3; plural=(n==1 ? 0 : (n==0 || (n%100 > 0 && n%100 < 20)) ? 1 : 2);"}
for e in pot:
    n = polib.POEntry(msgid=e.msgid, msgid_plural=e.msgid_plural, msgctxt=e.msgctxt)
    if e.msgid in PLURAL:
        n.msgstr_plural = {i: s for i, s in enumerate(PLURAL[e.msgid])}
    elif e.msgid in RO:
        n.msgstr = RO[e.msgid]
    elif e.msgid in old:
        n.msgstr, n.msgstr_plural = old[e.msgid].msgstr, old[e.msgid].msgstr_plural
    else:
        continue
    po.append(n)
out = os.path.join(overlay, "usr/share/locale-langpack/ro/LC_MESSAGES")
os.makedirs(out, exist_ok=True)
po.save_as_mofile(os.path.join(out, "lightdm-gtk-greeter.mo"))
print(f"{len(po)}/{len(pot)} strings")
