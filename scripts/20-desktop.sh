#!/bin/bash
# Stage 20: desktop, applications and system tools.
source "$(dirname "$0")/lib.sh"

mount_chroot
trap umount_chroot EXIT
prepare_build_proxy
policy_rc_on
set_build_sources

# Never pull these in (snap-only transitional packages, cloud tooling, Xubuntu branding).
cat > "$CHROOT/etc/apt/preferences.d/teios-no" <<'EOF'
Package: firefox thunderbird chromium-browser cloud-init xubuntu-default-settings xubuntu-artwork ubuntu-pro-client ubuntu-advantage-tools
Pin: release *
Pin-Priority: -1
EOF

# krb5-user asks for a default realm — leave empty, realmd configures it on join.
echo "krb5-config krb5-config/default_realm string" | in_chroot debconf-set-selections
echo "krb5-config krb5-config/add_servers_realm string" | in_chroot debconf-set-selections
echo "krb5-config krb5-config/kerberos_servers string" | in_chroot debconf-set-selections
echo "krb5-config krb5-config/admin_server string" | in_chroot debconf-set-selections

# falkon's postinst links into /usr/share/qt5 (packaging bug with the Qt6 build)
mkdir -p "$CHROOT/usr/share/qt5"

PKGS=$(grep -v '^\s*#' "$TEI_ROOT/config/packages.list" | tr '\n' ' ')
log "installing desktop packages"
in_chroot dpkg --configure -a || true
apt_in_chroot install --no-install-recommends $PKGS

# 32-bit Windows programs: Wine's 32-bit loader (multiarch i386).
log "Wine 32-bit support"
apt_in_chroot install --no-install-recommends wine32:i386 || echo "WARN: wine32 not installed"

apt_in_chroot autoremove --purge
apt_in_chroot clean

policy_rc_off
cleanup_build_proxy
log "stage 20 done"
