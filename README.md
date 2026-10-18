# Tei OS 1.0 „Miere”

Sistem de operare liber, cu **desktop clasic** (buton Start, bară de activități, meniu Start pe două coloane,
fișiere tip Explorer, Panou de control grafic), construit pe **Ubuntu 26.04 LTS** (suport până în 2031).
Aspectul este original — temă „teal & miere”, iconițe desenate de la zero în stilul anilor 2000 —
și nu folosește nimic din grafica Microsoft.

## Ce conține

| Zonă | Ce primiți |
|---|---|
| Desktop | Xfce 4.20 configurat clasic: bara jos, **Start** stânga-jos, lansare rapidă, ferestre, tavă, ceas; tasta Windows deschide meniul Start |
| Aspect | Tema „Tei” (ferestre, bară, meniu), set de ~95 iconițe originale, 4 fundaluri, sunete de sistem originale, ecran de pornire și meniu de boot proprii |
| Setări (GUI) | **Panou de control** pe categorii, **Proprietăți sistem** (nume computer, alăturare la domeniu AD), **Conturi utilizator**, **Dată și oră**, fereastra **Bun venit** |
| Programe | Navigator Falkon (Firefox se instalează dintr-un clic), LibreOffice (ro), VLC, cititor PDF, arhivator, calculator, desen, capturi de ecran, Remmina (RDP/VNC), jocuri de cărți și Minesweeper |
| Windows | Programele `.exe`/`.msi` pornesc cu dublu clic prin Wine 10 (32 și 64 de biți) |
| Firmă | Alăturare la domeniu Active Directory din GUI (realmd/sssd), partajări SMB în „Rețea”, imprimante, firewall activ (ufw + gufw), restaurare sistem (Timeshift) |
| Mașini virtuale | Hyper-V (inclusiv Gen 2 cu Secure Boot, șablonul „Microsoft UEFI Certificate Authority”), VMware, VirtualBox, KVM |
| Instalare | Installer grafic (Calamares) în română: BIOS și UEFI, Secure Boot, criptare disc opțională |

## Instalare

1. Scrieți ISO-ul pe un stick USB (Rufus în mod „DD”, balenaEtcher sau `dd`) sau atașați-l unei mașini virtuale.
2. Porniți de pe el → „Pornește Tei OS”. Sesiunea live pornește fără parolă (utilizator `tei`).
3. Dublu clic pe **Instalează Tei OS** de pe desktop și urmați pașii.

**Hyper-V:** VM Generația 2 → Securitate → șablon *Microsoft UEFI Certificate Authority* (sau dezactivați Secure Boot).
Rezoluția se schimbă din Panou de control → Ecran și rezoluție.

## Construirea ISO-ului din surse

Pe un Ubuntu 24.04/26.04 (de ex. o mașină virtuală Hyper-V cu ~40 GB liberi):

```bash
sudo ./build.sh            # toate etapele: 10 bază, 20 desktop, 30 configurare, 40 ISO
sudo ./build.sh 30 40      # doar reconfigurare + ISO, după modificări de temă/setări
```

Rezultatul: `build/out/teios-1.0-amd64.iso`.

### Personalizare rapidă

* **Numele sistemului:** variabilele `DISTRO_NAME`, `DISTRO_ID` din `scripts/lib.sh`.
* **Programe:** `config/packages.list`.
* **Culori / temă:** `artwork/src/palette.py`, `artwork/src/tei.css`.
* **Iconițe:** `artwork/src/icons.py` (fiecare iconiță e desenată din cod).
* **Setări implicite desktop:** `overlay/etc/xdg/teios/`.
* **Instrumentele Tei (Panou de control etc.):** `overlay/usr/lib/tei/`.

## Licențe

Codul și grafica Tei OS: GPL-3.0-or-later. Tema GTK pornește de la Greybird (Shimmer Project,
GPL-2.0+/CC-BY-SA-3.0), recolorată și extinsă. Pachetele provin din arhiva Ubuntu, cu licențele lor.
Tei OS nu este afiliat cu Canonical sau Microsoft.
