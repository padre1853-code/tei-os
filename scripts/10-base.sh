#!/bin/bash
# Stage 10: base system — apt sources, locales, kernel, live-boot (casper).
source "$(dirname "$0")/lib.sh"

if [ ! -x "$CHROOT/usr/bin/apt-get" ]; then
    log "debootstrap $SUITE"
    [ -e /usr/share/debootstrap/scripts/$SUITE ] || ln -sf gutsy /usr/share/debootstrap/scripts/$SUITE
    debootstrap --arch=amd64 --components=main,restricted,universe,multiverse "$SUITE" "$CHROOT" "$BUILD_MIRROR"
fi

mount_chroot
trap umount_chroot EXIT
prepare_build_proxy
policy_rc_on

log "apt sources"
SEC_MIRROR="${BUILD_MIRROR/archive.ubuntu.com/security.ubuntu.com}"
rm -f "$CHROOT/etc/apt/sources.list"
cat > "$CHROOT/etc/apt/sources.list.d/ubuntu.sources" <<EOF
Types: deb
URIs: $BUILD_MIRROR
Suites: $SUITE $SUITE-updates $SUITE-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: $SEC_MIRROR
Suites: $SUITE-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF

in_chroot dpkg --add-architecture i386
apt_in_chroot update
apt_in_chroot full-upgrade

log "locales, timezone, hostname"
apt_in_chroot install locales tzdata language-pack-ro language-pack-ro-base language-pack-en language-pack-en-base
sed -i 's/^# *\(ro_RO.UTF-8\)/\1/; s/^# *\(en_US.UTF-8\)/\1/; s/^# *\(en_GB.UTF-8\)/\1/' "$CHROOT/etc/locale.gen"
grep -q '^ro_RO.UTF-8' "$CHROOT/etc/locale.gen" || echo 'ro_RO.UTF-8 UTF-8' >> "$CHROOT/etc/locale.gen"
grep -q '^en_US.UTF-8' "$CHROOT/etc/locale.gen" || echo 'en_US.UTF-8 UTF-8' >> "$CHROOT/etc/locale.gen"
in_chroot locale-gen
printf 'LANG=ro_RO.UTF-8\nLANGUAGE=ro:en\n' > "$CHROOT/etc/default/locale"
ln -sf /usr/share/zoneinfo/Europe/Bucharest "$CHROOT/etc/localtime"
echo "Europe/Bucharest" > "$CHROOT/etc/timezone"
echo "$DISTRO_ID" > "$CHROOT/etc/hostname"
cat > "$CHROOT/etc/hosts" <<EOF
127.0.0.1 localhost
127.0.1.1 $DISTRO_ID
::1 localhost ip6-localhost ip6-loopback
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
EOF

log "kernel, initramfs, live boot"
apt_in_chroot install --no-install-recommends \
    linux-generic casper initramfs-tools plymouth plymouth-label \
    grub-pc-bin grub-efi-amd64-bin grub-efi-amd64-signed shim-signed grub2-common grub-common \
    efibootmgr os-prober memtest86+ \
    systemd-sysv dbus-user-session sudo polkitd pkexec ca-certificates

policy_rc_off
cleanup_build_proxy
log "stage 10 done"
