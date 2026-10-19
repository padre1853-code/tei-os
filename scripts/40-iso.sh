#!/bin/bash
# Stage 40: live image (casper) + hybrid BIOS/UEFI ISO with Secure Boot (Ubuntu-signed shim & GRUB).
source "$(dirname "$0")/lib.sh"

DATE=$(date +%Y%m%d)
ISO_NAME="${ISO_NAME:-winlow-xp-$DISTRO_VERSION-amd64.iso}"
VOLID="WINLOW_XP_${DISTRO_VERSION//./_}"
COMP="${COMP:-xz}"

mount_chroot
trap 'umount_chroot' EXIT

log "initramfs with casper + boot splash"
in_chroot env CASPER_GENERATE_UUID=1 update-initramfs -u -k all

log "cleaning the image"
rm -rf "$CHROOT"/tmp/* "$CHROOT"/tmp/.[!.]* "$CHROOT"/var/tmp/* 2>/dev/null || true
rm -rf "$CHROOT"/root/.cache "$CHROOT"/root/.bash_history "$CHROOT"/root/.config "$CHROOT"/root/.local
rm -rf "$CHROOT"/var/crash/* "$CHROOT"/var/lib/apport/coredump/* 2>/dev/null || true
rm -f "$CHROOT"/etc/ssl/build-proxy-ca.crt "$CHROOT"/usr/sbin/policy-rc.d
rm -rf "$CHROOT"/var/lib/apt/lists/* "$CHROOT"/var/cache/apt/*.bin "$CHROOT"/var/cache/apt/archives/*.deb
find "$CHROOT/var/log" -type f -exec truncate -s 0 {} \;
: > "$CHROOT/etc/machine-id"
rm -f "$CHROOT/var/lib/dbus/machine-id"
rm -f "$CHROOT"/etc/ssh/ssh_host_* 2>/dev/null || true
echo "$DISTRO_ID" > "$CHROOT/etc/hostname"

log "ISO tree"
rm -rf "$ISO_DIR" && mkdir -p "$ISO_DIR"/{casper,.disk,boot/grub,EFI/boot,pool/teios}
KVER=$(ls "$CHROOT"/boot/vmlinuz-* | sed 's#.*/vmlinuz-##' | sort -V | tail -1)
cp "$CHROOT/boot/vmlinuz-$KVER" "$ISO_DIR/casper/vmlinuz"
cp "$CHROOT/boot/initrd.img-$KVER" "$ISO_DIR/casper/initrd"
cp "$CHROOT/boot/mt86+x64" "$ISO_DIR/boot/mt86+x64" 2>/dev/null || true
cp "$BUILD_DIR"/pool/teios/*.deb "$ISO_DIR/pool/teios/"

# casper matches the medium against the UUID baked into the initrd
rm -rf "$CHROOT/tmp/teios-initrd"
in_chroot unmkinitramfs "/boot/initrd.img-$KVER" /tmp/teios-initrd >/dev/null 2>&1 || true
UUID=$(cat $(find "$CHROOT/tmp/teios-initrd" -name uuid.conf | head -1) 2>/dev/null || true)
rm -rf "$CHROOT/tmp/teios-initrd"
[ -n "$UUID" ] || { echo "ERROR: could not read casper uuid from initrd"; exit 1; }
echo "$UUID" > "$ISO_DIR/.disk/casper-uuid-generic"
echo "$DISTRO_NAME $DISTRO_VERSION \"Miere\" - amd64 ($DATE)" > "$ISO_DIR/.disk/info"
echo "full_cd/single" > "$ISO_DIR/.disk/cd_type"
touch "$ISO_DIR/.disk/base_installable"
echo "file:///usr/share/teios/help/index.html" > "$ISO_DIR/.disk/release_notes_url"

in_chroot dpkg-query -W --showformat='${Package} ${Version}\n' > "$ISO_DIR/casper/filesystem.manifest"
umount_chroot
trap - EXIT

log "squashfs ($COMP)"
du -sx --block-size=1 "$CHROOT" | cut -f1 > "$ISO_DIR/casper/filesystem.size"
if [ "$COMP" = "xz" ]; then CARGS=(-comp xz -Xbcj x86 -b 1M -Xdict-size 100%); else CARGS=(-comp zstd -Xcompression-level 15 -b 1M); fi
mksquashfs "$CHROOT" "$ISO_DIR/casper/filesystem.squashfs" -noappend -no-progress "${CARGS[@]}" \
    -e boot/grub/grub.cfg -wildcards -e 'proc/*' -e 'sys/*' -e 'dev/*' -e 'run/*' -e 'tmp/*' -e 'mnt/*' -e 'media/*' -e 'var/cache/apt/archives/*.deb' -e 'lost+found'
ls -la "$ISO_DIR/casper/"

log "GRUB (BIOS + UEFI/Secure Boot)"
GD="$ISO_DIR/boot/grub"
mkdir -p "$GD/fonts" "$GD/themes" "$GD/i386-pc" "$GD/x86_64-efi"
cp "$CHROOT/usr/share/grub/unicode.pf2" "$GD/fonts/"
for s in 12 14 16; do
    chroot "$CHROOT" grub-mkfont -s $s -o /tmp/dejavu_$s.pf2 /usr/share/fonts/truetype/dejavu/DejaVuSans.ttf
    chroot "$CHROOT" grub-mkfont -s $s -o /tmp/dejavu_bold_$s.pf2 /usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
done
mv "$CHROOT"/tmp/dejavu_*.pf2 "$GD/fonts/"
cp -a "$CHROOT/usr/share/grub/themes/teios" "$GD/themes/"
cp "$CHROOT"/usr/lib/grub/i386-pc/*.mod "$CHROOT"/usr/lib/grub/i386-pc/*.lst "$GD/i386-pc/"
cp "$CHROOT"/usr/lib/grub/x86_64-efi/*.mod "$CHROOT"/usr/lib/grub/x86_64-efi/*.lst "$GD/x86_64-efi/"

cat > "$GD/grub.cfg" <<'EOF'
# WinLow XP live boot menu
set default=0
set timeout=10
set timeout_style=menu
insmod all_video
insmod gfxterm
insmod gfxmenu
insmod jpeg
insmod png
insmod part_gpt
insmod part_msdos
insmod iso9660
loadfont /boot/grub/fonts/unicode.pf2
loadfont /boot/grub/fonts/dejavu_12.pf2
loadfont /boot/grub/fonts/dejavu_14.pf2
loadfont /boot/grub/fonts/dejavu_16.pf2
loadfont /boot/grub/fonts/dejavu_bold_16.pf2
set gfxmode=auto
terminal_output gfxterm
set theme=/boot/grub/themes/teios/theme.txt
export theme
set menu_color_normal=white/black
set menu_color_highlight=black/light-cyan

menuentry "Pornește WinLow XP" --class teios {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper quiet splash ---
    initrd /casper/initrd
}
menuentry "WinLow XP (English)" --class teios {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper locale=en_US.UTF-8 keyboard-configuration/layoutcode=us quiet splash ---
    initrd /casper/initrd
}
menuentry "Mod grafic sigur" --class teios {
    set gfxpayload=keep
    linux /casper/vmlinuz boot=casper nomodeset quiet splash ---
    initrd /casper/initrd
}
if [ "$grub_platform" = "efi" ]; then
menuentry "Setări UEFI (firmware)" --class settings {
    fwsetup
}
menuentry "Pornește de pe disc" --class disk {
    exit 1
}
else
menuentry "Test memorie RAM" --class memtest {
    linux /boot/mt86+x64
}
fi
EOF
# the signed EFI image looks for its config under /boot/grub; provide redirects too
printf 'search --no-floppy --set=root --file /.disk/info\nset prefix=($root)/boot/grub\nconfigfile $prefix/grub.cfg\n' > "$GD/x86_64-efi/grub.cfg"
cp "$GD/x86_64-efi/grub.cfg" "$ISO_DIR/EFI/boot/grub.cfg"
cp "$GD/x86_64-efi/grub.cfg" "$GD/i386-pc/grub.cfg"

# BIOS El Torito image
chroot "$CHROOT" grub-mkimage -O i386-pc-eltorito -d /usr/lib/grub/i386-pc -p /boot/grub -o /tmp/eltorito.img \
    biosdisk iso9660 part_msdos part_gpt normal configfile search search_fs_file linux echo test ls cat \
    all_video gfxterm gfxmenu font jpeg png reboot halt chain
mv "$CHROOT/tmp/eltorito.img" "$GD/i386-pc/eltorito.img"
cp "$CHROOT/usr/lib/grub/i386-pc/boot_hybrid.img" "$BUILD_DIR/boot_hybrid.img"

# UEFI: Microsoft-signed shim -> Canonical-signed GRUB (works with Secure Boot on)
cp "$CHROOT/usr/lib/shim/shimx64.efi.signed.latest" "$ISO_DIR/EFI/boot/bootx64.efi" 2>/dev/null || \
    cp "$CHROOT/usr/lib/shim/shimx64.efi.signed" "$ISO_DIR/EFI/boot/bootx64.efi"
cp "$CHROOT/usr/lib/shim/mmx64.efi" "$ISO_DIR/EFI/boot/mmx64.efi"
cp "$CHROOT/usr/lib/grub/x86_64-efi-signed/gcdx64.efi.signed" "$ISO_DIR/EFI/boot/grubx64.efi"
EFIIMG="$BUILD_DIR/efi.img"
rm -f "$EFIIMG"
mkfs.msdos -C "$EFIIMG" 10240 >/dev/null
mmd -i "$EFIIMG" ::/EFI ::/EFI/boot ::/boot ::/boot/grub
mcopy -i "$EFIIMG" "$ISO_DIR/EFI/boot/bootx64.efi" "$ISO_DIR/EFI/boot/mmx64.efi" "$ISO_DIR/EFI/boot/grubx64.efi" "$ISO_DIR/EFI/boot/grub.cfg" ::/EFI/boot/
mcopy -i "$EFIIMG" "$ISO_DIR/EFI/boot/grub.cfg" ::/boot/grub/grub.cfg

log "xorriso"
mkdir -p "$OUT_DIR"
rm -f "$OUT_DIR/$ISO_NAME"
xorriso -as mkisofs -r -V "$VOLID" -J -joliet-long -l -iso-level 3 \
    -o "$OUT_DIR/$ISO_NAME" \
    --grub2-mbr "$BUILD_DIR/boot_hybrid.img" \
    -partition_offset 16 \
    --mbr-force-bootable \
    -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b "$EFIIMG" \
    -appended_part_as_gpt \
    -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 \
    -c '/boot.catalog' \
    -b '/boot/grub/i386-pc/eltorito.img' -no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
    -eltorito-alt-boot \
    -e '--interval:appended_partition_2:::' -no-emul-boot \
    "$ISO_DIR"
( cd "$OUT_DIR" && sha256sum "$ISO_NAME" > "$ISO_NAME.sha256" )
ls -la "$OUT_DIR"
log "stage 40 done: $OUT_DIR/$ISO_NAME"
