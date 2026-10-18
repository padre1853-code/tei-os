#!/bin/bash
# Stage 30: Tei OS look & feel, tools and system defaults.
source "$(dirname "$0")/lib.sh"

ART="$TEI_ROOT/artwork"
OUT="$ART/out"

log "generating artwork"
python3 "$ART/src/logo.py" "$OUT" >/dev/null
python3 "$ART/src/wallpaper.py" "$OUT/backgrounds" 3840 2160
python3 "$ART/src/gtk_theme.py" "$CHROOT/usr/share/themes/Greybird" "$OUT/themes/Tei" "$ART/src/tei.css"
python3 "$ART/src/xfwm4_theme.py" "$OUT/themes/Tei/xfwm4" 1
python3 "$ART/src/xfwm4_theme.py" "$OUT/themes/Tei-hdpi/xfwm4" 2
python3 "$ART/src/icons.py" "$OUT/icons/Tei"
python3 "$ART/src/sounds.py" "$OUT/sounds/tei/stereo"
python3 "$ART/src/boot_art.py" "$OUT/boot"

mount_chroot
trap umount_chroot EXIT
prepare_build_proxy
policy_rc_on
set_build_sources

log "installing artwork"
rm -rf "$CHROOT/usr/share/themes/Tei" "$CHROOT/usr/share/themes/Tei-hdpi" "$CHROOT/usr/share/icons/Tei"
cp -a "$OUT/themes/Tei" "$OUT/themes/Tei-hdpi" "$CHROOT/usr/share/themes/"
cp -a "$OUT/icons/Tei" "$CHROOT/usr/share/icons/"
mkdir -p "$CHROOT/usr/share/sounds" "$CHROOT/usr/share/backgrounds/teios" "$CHROOT/usr/share/teios" "$CHROOT/usr/share/pixmaps"
rm -rf "$CHROOT/usr/share/sounds/tei" && cp -a "$OUT/sounds/tei" "$CHROOT/usr/share/sounds/"
cp "$OUT/backgrounds/"*.jpg "$CHROOT/usr/share/backgrounds/teios/"
cp "$OUT/boot/backgrounds/grub.png" "$CHROOT/usr/share/backgrounds/teios/grub.png"
cp "$OUT/tei-logo.svg" "$CHROOT/usr/share/teios/logo.svg"
cp "$OUT/tei-wordmark.svg" "$CHROOT/usr/share/teios/wordmark.svg"
rsvg-convert -w 256 "$OUT/tei-logo.svg" -o "$CHROOT/usr/share/pixmaps/teios-logo.png"
rm -rf "$CHROOT/usr/share/plymouth/themes/teios"
cp -a "$OUT/boot/plymouth/teios" "$CHROOT/usr/share/plymouth/themes/"
mkdir -p "$CHROOT/usr/share/grub/themes"
rm -rf "$CHROOT/usr/share/grub/themes/teios" && cp -a "$OUT/boot/grub/teios" "$CHROOT/usr/share/grub/themes/"
# wallpapers also listed in the Xfce background chooser
for w in tei miere noapte clasic; do ln -sf ../teios/$w.jpg "$CHROOT/usr/share/backgrounds/xfce/tei-$w.jpg"; done

log "overlay files"
cp -a "$TEI_ROOT/overlay/." "$CHROOT/"
chmod 755 "$CHROOT"/usr/bin/tei-* "$CHROOT"/usr/lib/tei/*.py "$CHROOT"/usr/lib/tei/tei-*
cp "$OUT/boot/calamares/"* "$CHROOT/etc/calamares/branding/teios/"

log "BIOS GRUB flavour in the image, EFI flavour kept on the ISO for EFI installs"
echo "grub-pc grub-pc/install_devices multiselect" | in_chroot debconf-set-selections
echo "grub-pc grub-pc/install_devices_empty boolean true" | in_chroot debconf-set-selections
apt_in_chroot install --no-install-recommends grub-pc
mkdir -p "$BUILD_DIR/pool/teios" "$CHROOT/tmp/teios-pool/partial"
rm -f "$BUILD_DIR/pool/teios/"*.deb
apt_in_chroot install --download-only --no-install-recommends -o Dir::Cache::archives=/tmp/teios-pool grub-efi-amd64
cp "$CHROOT"/tmp/teios-pool/grub-efi-amd64_*.deb "$BUILD_DIR/pool/teios/"
rm -rf "$CHROOT/tmp/teios-pool"
ls -la "$BUILD_DIR/pool/teios/"

log "branding: os-release, lsb-release, issue, casper"
if [ ! -e "$CHROOT/usr/lib/os-release.ubuntu" ]; then
    in_chroot dpkg-divert --local --rename --divert /usr/lib/os-release.ubuntu --add /usr/lib/os-release
fi
. "$CHROOT/usr/lib/os-release.ubuntu"
cat > "$CHROOT/usr/lib/os-release" <<EOF
PRETTY_NAME="$DISTRO_NAME $DISTRO_VERSION „Miere” (bazat pe Ubuntu $VERSION_ID LTS)"
NAME="$DISTRO_NAME"
VERSION_ID="$VERSION_ID"
VERSION="$DISTRO_VERSION ($VERSION)"
VERSION_CODENAME=$VERSION_CODENAME
ID=ubuntu
ID_LIKE=debian
HOME_URL="file:///usr/share/teios/help/index.html"
SUPPORT_URL="file:///usr/share/teios/help/index.html"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=$UBUNTU_CODENAME
LOGO=tei-start
TEIOS_VERSION="$DISTRO_VERSION"
EOF
sed -i "s/^DISTRIB_DESCRIPTION=.*/DISTRIB_DESCRIPTION=\"$DISTRO_NAME $DISTRO_VERSION (Ubuntu $VERSION_ID LTS)\"/" "$CHROOT/etc/lsb-release"
printf '%s %s \\n \\l\n\n' "$DISTRO_NAME" "$DISTRO_VERSION" > "$CHROOT/etc/issue"
printf '%s %s\n' "$DISTRO_NAME" "$DISTRO_VERSION" > "$CHROOT/etc/issue.net"
cat > "$CHROOT/etc/casper.conf" <<EOF
export USERNAME="$LIVE_USER"
export USERFULLNAME="Utilizator Tei"
export HOST="tei-live"
export BUILD_SYSTEM="Ubuntu"
export FLAVOUR="Tei OS"
EOF

# live session shutdown prompt (casper has no translations for it)
if [ -f "$CHROOT/usr/sbin/casper-stop" ]; then
    sed -i 's|^\(\s*MSG=\)"Please remove the installation medium, then press ENTER: "|\1"Scoateți stick-ul / DVD-ul de instalare, apoi apăsați ENTER  ·  Remove the installation medium, then press ENTER "|;
            s|^\(\s*MSG_FALLBACK=\)"Please remove the installation medium, then reboot."|\1"Scoateți stick-ul / DVD-ul de instalare, apoi reporniți. (Remove the installation medium, then reboot.)"|' \
        "$CHROOT/usr/sbin/casper-stop"
fi

log "keyboard, environment, GTK/Qt defaults"
cat > "$CHROOT/etc/default/keyboard" <<'EOF'
XKBMODEL="pc105"
XKBLAYOUT="ro"
XKBVARIANT=""
XKBOPTIONS=""
BACKSPACE="guess"
EOF
grep -q '^GTK_OVERLAY_SCROLLING' "$CHROOT/etc/environment" || echo 'GTK_OVERLAY_SCROLLING=0' >> "$CHROOT/etc/environment"
grep -q '^QT_QPA_PLATFORMTHEME' "$CHROOT/etc/environment" || echo 'QT_QPA_PLATFORMTHEME=gtk3' >> "$CHROOT/etc/environment"
mkdir -p "$CHROOT/etc/gtk-3.0"
cat > "$CHROOT/etc/gtk-3.0/settings.ini" <<'EOF'
[Settings]
gtk-theme-name=Tei
gtk-icon-theme-name=Tei
gtk-font-name=Noto Sans 10
gtk-cursor-theme-name=DMZ-White
gtk-cursor-theme-size=24
gtk-menu-images=true
gtk-button-images=true
gtk-sound-theme-name=tei
gtk-enable-event-sounds=true
gtk-decoration-layout=menu:minimize,maximize,close
EOF
mkdir -p "$CHROOT/usr/share/icons/default"
printf '[Icon Theme]\nInherits=DMZ-White\n' > "$CHROOT/usr/share/icons/default/index.theme"
in_chroot update-alternatives --set x-cursor-theme /usr/share/icons/DMZ-White/cursor.theme 2>/dev/null || true
in_chroot update-alternatives --set x-www-browser /usr/bin/falkon 2>/dev/null || true
in_chroot update-alternatives --set x-terminal-emulator /usr/bin/xfce4-terminal.wrapper 2>/dev/null || true

log "remove packages we replace with Tei tools"
apt_in_chroot purge gnome-system-tools system-tools-backends || true
apt_in_chroot autoremove --purge

log "slimming the image"
# Debian ships Wine's Windows-side DLLs with full debug info (dh_strip skips PE files): ~1 GB.
# Strip it the way upstream 'make install' does; the 'Wine builtin DLL' marker is preserved.
for d in "$CHROOT"/usr/lib/x86_64-linux-gnu/wine/*-windows "$CHROOT"/usr/lib/i386-linux-gnu/wine/*-windows; do
    [ -d "$d" ] || continue
    find "$d" -type f -print0 | xargs -0 -r -n 64 strip --strip-debug 2>/dev/null || true
done
# Firmware for hardware that never appears in a PC: Qualcomm Arm SoCs (PCIe 5G modems and AI100 kept),
# network-switch ASICs and Arm/DPU network processors.
FW="$CHROOT/usr/lib/firmware"
if [ -d "$FW/qcom" ]; then
    find "$FW/qcom" -mindepth 1 -maxdepth 1 ! -name 'sdx*' ! -name 'aic100' -exec rm -rf {} +
fi
rm -rf "$FW/mellanox" "$FW/mrvl/prestera" "$FW/dpaa2" "$FW/netronome" "$FW/liquidio"
find "$FW" -xtype l -delete
du -sh "$CHROOT/usr/lib/firmware" "$CHROOT/usr/lib/x86_64-linux-gnu/wine" "$CHROOT/usr/lib/i386-linux-gnu/wine" 2>/dev/null || true

log "boot splash"
in_chroot update-alternatives --install /usr/share/plymouth/themes/default.plymouth default.plymouth \
    /usr/share/plymouth/themes/teios/teios.plymouth 300
in_chroot update-alternatives --set default.plymouth /usr/share/plymouth/themes/teios/teios.plymouth

log "services"
in_chroot systemctl set-default graphical.target
for s in NetworkManager lightdm cups bluetooth ufw avahi-daemon; do in_chroot systemctl enable $s 2>/dev/null || true; done
echo /usr/sbin/lightdm > "$CHROOT/etc/X11/default-display-manager"
ln -sf /usr/lib/systemd/system/lightdm.service "$CHROOT/etc/systemd/system/display-manager.service"
sed -i 's/^ENABLED=.*/ENABLED=yes/' "$CHROOT/etc/ufw/ufw.conf" 2>/dev/null || true

log "caches"
in_chroot gtk-update-icon-cache -f /usr/share/icons/Tei
in_chroot glib-compile-schemas /usr/share/glib-2.0/schemas
in_chroot update-desktop-database -q /usr/share/applications || true
in_chroot fc-cache -f >/dev/null

log "final apt sources"
set_final_sources
in_chroot apt-get clean
rm -rf "$CHROOT"/var/lib/apt/lists/*

policy_rc_off
cleanup_build_proxy
log "stage 30 done"
