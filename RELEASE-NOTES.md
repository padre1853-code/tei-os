# WinLow XP 1.0 „Miere”

Sistem de operare liber cu **desktop clasic**: butonul Start, bara de activități, Panou de control,
dosare și ferestre ca pe vremuri — pe o bază modernă, **Ubuntu 26.04 LTS** (actualizări de securitate până în 2031).
Aspectul și iconițele sunt originale.

## Descărcare

* `winlow-xp-1.0-amd64.iso` — imaginea de instalare (calculatoare pe 64 de biți, BIOS sau UEFI, cu sau fără Secure Boot)
* `winlow-xp-1.0-amd64.iso.sha256` — suma de control

## Instalare

1. Scrieți ISO-ul pe un stick USB de minimum 4 GB, de exemplu cu **Rufus** (alegeți „DD Image” când întreabă)
   sau **balenaEtcher**. Într-o mașină virtuală, atașați direct fișierul ISO.
2. Porniți calculatorul de pe stick și alegeți **Pornește WinLow XP**. Sistemul pornește fără parolă, ca să-l puteți încerca.
3. Dublu clic pe **Instalează WinLow XP** (pe desktop) și urmați pașii: limbă, fus orar, tastatură, disc, utilizator.
   Instalarea durează 10–20 de minute.

**Cerințe:** procesor pe 64 de biți, 2 GB RAM (recomandat 4 GB), 15 GB spațiu pe disc.

**Hyper-V:** mașină virtuală de Generația 2 → Security → șablonul *Microsoft UEFI Certificate Authority*.

## Ce găsiți în sistem

* Meniu Start pe două coloane, căutare, „Locuri” (Documente, Imagini, Computer, Rețea); tasta Windows deschide meniul
* Panou de control pe categorii, Proprietăți sistem (nume calculator, domeniu Active Directory), Conturi utilizator, Dată și oră
* LibreOffice (salvează implicit în formatele Word/Excel/PowerPoint), navigator Falkon (Firefox se instalează dintr-un clic),
  VLC, cititor PDF, arhivator, calculator, desen, desktop la distanță (RDP/VNC), jocuri de cărți
* Programe Windows (`.exe`, `.msi`) prin Wine 10, partajări de rețea Windows, imprimante, firewall activ
* Restaurare sistem (Timeshift), actualizări automate de securitate

---
WinLow XP este un proiect independent, bazat pe Ubuntu, neafiliat cu Microsoft sau Canonical.
Windows și Windows XP sunt mărci comerciale ale Microsoft Corporation.
