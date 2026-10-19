# WinLow XP 1.0 „Miere”

Sistem de operare liber, cu **desktop clasic** (buton Start, bară de activități, meniu Start pe două coloane,
fișiere tip Explorer, Panou de control grafic), construit pe **Ubuntu 26.04 LTS** (suport până în 2031).
Aspectul este original — temă închisă cu accente portocalii, logo propriu (sferă portocalie cu „W”),
iconițe desenate de la zero în stilul anilor 2000 — și nu folosește nimic din grafica Microsoft.

## Ce conține

| Zonă | Ce primiți |
|---|---|
| Desktop | Xfce 4.20 configurat clasic: bara jos, **Start** stânga-jos, lansare rapidă, ferestre, tavă, ceas; tasta Windows deschide meniul Start |
| Aspect | Tema „Tei” (bare de titlu și bară de activități închise, portocaliu ca accent), ~95 de iconițe originale, 4 fundaluri, sunete de sistem originale, ecran de pornire („created by Mihai”) și meniu de boot proprii |
| Setări (GUI) | **Panou de control** pe categorii, **Proprietăți sistem** (nume calculator, alăturare la domeniu AD), **Conturi utilizator**, **Dată și oră**, fereastra **Bun venit** |
| Programe | Navigator Falkon (Firefox se instalează dintr-un clic), LibreOffice (ro, salvează implicit .docx/.xlsx/.pptx), VLC, cititor PDF, arhivator, calculator, desen, capturi de ecran, Remmina (RDP/VNC), jocuri de cărți și Minesweeper |
| Windows | Programele `.exe`/`.msi` pornesc cu dublu clic prin Wine 10 (32 și 64 de biți) |
| Firmă | Alăturare la domeniu Active Directory din GUI (realmd/sssd), partajări SMB în „Rețea”, imprimante și scanere, firewall activ (ufw + gufw), restaurare sistem (Timeshift) |
| Securitate | Actualizări automate de securitate, Secure Boot (shim semnat Microsoft → GRUB semnat Canonical), criptare disc opțională la instalare |
| Mașini virtuale | Hyper-V (inclusiv Gen 2 cu Secure Boot, șablonul „Microsoft UEFI Certificate Authority”), VMware, VirtualBox, KVM/QEMU |
| Instalare | Installer grafic (Calamares) în română: BIOS și UEFI, ștergere disc sau partiționare manuală, ext4/btrfs/xfs |

## Instalare

1. Scrieți ISO-ul pe un stick USB (Rufus în mod „DD Image”, balenaEtcher sau `dd`) sau atașați-l unei mașini virtuale.
2. Porniți de pe el → „Pornește WinLow XP” (sau „WinLow XP (English)”). Sesiunea live pornește fără parolă (utilizator `winlow`).
3. Dublu clic pe **Instalează WinLow XP** de pe desktop și urmați pașii.

Cerințe: procesor pe 64 de biți, 2 GB RAM (recomandat 4 GB), 15 GB pe disc.

**Hyper-V:** VM Generația 2 → Securitate → șablon *Microsoft UEFI Certificate Authority* (sau dezactivați Secure Boot).
Rezoluția se schimbă din Panou de control → Ecran și rezoluție.

## Construirea ISO-ului din surse

Pe un Ubuntu 24.04/26.04 (de ex. o mașină virtuală cu ~40 GB liberi), ca root:

```bash
sudo ./build.sh            # toate etapele: 10 bază, 20 desktop, 30 configurare, 40 ISO
sudo ./build.sh 30 40      # doar reconfigurare + ISO, după modificări de temă/setări
```

Rezultatul: `build/out/winlow-xp-1.0-amd64.iso` (+ `.sha256`).

### Structura

| Cale | Ce este |
|---|---|
| `scripts/10-base.sh` … `40-iso.sh` | etapele de construire (debootstrap, pachete, configurare, imagine live + ISO hibrid BIOS/UEFI) |
| `config/packages.list` | lista de programe |
| `artwork/src/` | generatoarele graficii: logo, fundaluri, tema GTK și a ferestrelor, iconițe, sunete, ecran de pornire |
| `overlay/` | fișierele copiate peste sistem: setările implicite ale desktopului, instrumentele Tei, configurarea installerului |
| `overlay/usr/lib/tei/` | Panoul de control, Proprietăți sistem, Conturi, Dată și oră, Bun venit (Python + GTK) |
| `i18n/` | traducerea în română a installerului (completează traducerea Calamares) |
| `scripts/vmtest.py` | test automat în QEMU (pornire, clicuri, capturi de ecran) |

### Personalizare rapidă

* **Numele sistemului:** variabilele `DISTRO_NAME`, `DISTRO_ID` din `scripts/lib.sh`.
* **Programe:** `config/packages.list`.
* **Culori / temă:** `artwork/src/palette.py`, `artwork/src/tei.css`, `artwork/src/xfwm4_theme.py`.
* **Logo:** `artwork/src/logo.py` (`orb_svg`).
* **Iconițe:** `artwork/src/icons.py` (fiecare iconiță e desenată din cod).
* **Setări implicite desktop:** `overlay/etc/xdg/teios/`.

## Licențe

Codul și grafica WinLow XP: GPL-3.0-or-later. Tema GTK pornește de la Greybird (Shimmer Project,
GPL-2.0+/CC-BY-SA-3.0), recolorată și extinsă. Traducerile installerului completează catalogul Calamares (GPL-3.0).
Pachetele provin din arhiva Ubuntu, cu licențele lor. WinLow XP este un proiect independent și nu este afiliat cu Canonical sau Microsoft.
Windows și Windows XP sunt mărci comerciale ale Microsoft Corporation; Ubuntu este marcă comercială a Canonical Ltd.
