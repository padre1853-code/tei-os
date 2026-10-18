#!/usr/bin/env python3
"""Build Romanian translations for the Calamares installer used by Tei OS.

Usage: build-calamares-ro.py <calamares-source-dir> <overlay-dir>
  calamares-source-dir: a checkout of https://github.com/calamares/calamares at the tag matching the
                        packaged version (v3.3.14 for Ubuntu 26.04).
Writes:
  <overlay>/usr/share/calamares/lang/calamares_ro.qm    (Calamares loads this before its built-in copy)
  <overlay>/usr/share/locale/ro/LC_MESSAGES/calamares-python.mo
Needs: lrelease (qt6-l10n-tools), msgfmt (gettext), python3-polib.
"""
import os
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET

import polib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ro_calamares import PY, QT, TZ  # noqa: E402

src, overlay = sys.argv[1], sys.argv[2]
LRELEASE = next((p for p in ("/usr/lib/qt6/bin/lrelease", "/usr/bin/lrelease") if os.path.exists(p)), "lrelease")

# --- Qt catalogue -------------------------------------------------------------------------------
tree = ET.parse(os.path.join(src, "lang", "calamares_ro.ts"))
used = set()
for ctx in tree.getroot().findall("context"):
    name = ctx.find("name").text
    for m in ctx.findall("message"):
        key = (name, m.find("source").text)
        if key not in QT:
            continue
        tr = m.find("translation")
        if tr is None:
            tr = ET.SubElement(m, "translation")
        if tr.get("type") in ("vanished", "obsolete"):
            continue
        val = QT[key]
        for child in list(tr):
            tr.remove(child)
        if m.get("numerus") == "yes":
            forms = val if isinstance(val, list) else [val] * 3
            tr.text = None
            for f in forms:
                ET.SubElement(tr, "numerusform").text = f
        else:
            tr.text = val if isinstance(val, str) else val[0]
        tr.attrib.pop("type", None)
        used.add(key)
missing = sorted(set(QT) - used)
if missing:
    print("warning: not found in catalogue:", *missing, sep="\n  ")

qm_dir = os.path.join(overlay, "usr/share/calamares/lang")
os.makedirs(qm_dir, exist_ok=True)
with tempfile.TemporaryDirectory() as tmp:
    ts = os.path.join(tmp, "calamares_ro.ts")
    tree.write(ts, encoding="utf-8", xml_declaration=True)
    subprocess.run([LRELEASE, "-silent", ts, "-qm", os.path.join(qm_dir, "calamares_ro.qm")], check=True)

# --- time zone names ----------------------------------------------------------------------------
tz = ET.parse(os.path.join(src, "lang", "tz_en.ts"))
tz.getroot().set("language", "ro")
for m in tz.getroot().iter("message"):
    s_ = m.find("source").text
    tr = m.find("translation")
    if s_ in TZ:
        tr.text = TZ[s_]
        tr.attrib.pop("type", None)
with tempfile.TemporaryDirectory() as tmp:
    ts = os.path.join(tmp, "tz_ro.ts")
    tz.write(ts, encoding="utf-8", xml_declaration=True)
    subprocess.run([LRELEASE, "-silent", ts, "-qm", os.path.join(qm_dir, "tz_ro.qm")], check=True)

# --- Python job catalogue -----------------------------------------------------------------------
po = polib.pofile(os.path.join(src, "lang", "python", "ro", "LC_MESSAGES", "python.po"))
n = 0
for e in po:
    if e.msgid in PY and not e.msgid_plural:
        e.msgstr = PY[e.msgid]
        if "fuzzy" in e.flags:
            e.flags.remove("fuzzy")
        n += 1
mo_dir = os.path.join(overlay, "usr/share/locale/ro/LC_MESSAGES")
os.makedirs(mo_dir, exist_ok=True)
po.save_as_mofile(os.path.join(mo_dir, "calamares-python.mo"))
print(f"Qt strings: {len(used)}/{len(QT)}, Python strings: {n}/{len(PY)}")
