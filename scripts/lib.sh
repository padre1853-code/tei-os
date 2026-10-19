#!/bin/bash
# WinLow XP build — shared helpers. Sourced by the stage scripts.
set -euo pipefail

: "${TEI_ROOT:=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)}"
: "${BUILD_DIR:=$TEI_ROOT/build}"
: "${CHROOT:=$BUILD_DIR/chroot}"
: "${ISO_DIR:=$BUILD_DIR/iso}"
: "${OUT_DIR:=$BUILD_DIR/out}"
: "${SUITE:=resolute}"                       # Ubuntu 26.04 LTS
: "${MIRROR:=http://archive.ubuntu.com/ubuntu}" # mirror written into the final system
: "${BUILD_MIRROR:=$MIRROR}"                 # mirror used while building
: "${DISTRO_NAME:=WinLow XP}"
: "${DISTRO_ID:=teios}"
: "${DISTRO_VERSION:=1.0}"
: "${DISTRO_CODENAME:=miere}"
: "${LIVE_USER:=winlow}"
# Optional build proxy (only needed in sandboxed build hosts). Never shipped in the image.
: "${BUILD_HTTPS_PROXY:=}"
: "${BUILD_PROXY_CA:=}"

export DEBIAN_FRONTEND=noninteractive
export LC_ALL=C.UTF-8

log() { printf '\n\033[1;36m==> %s\033[0m\n' "$*"; }

mount_chroot() {
    mountpoint -q "$CHROOT/proc" || mount -t proc proc "$CHROOT/proc"
    mountpoint -q "$CHROOT/sys" || mount -t sysfs sysfs "$CHROOT/sys"
    mountpoint -q "$CHROOT/dev" || mount --bind /dev "$CHROOT/dev"
    mountpoint -q "$CHROOT/dev/pts" || mount -t devpts devpts "$CHROOT/dev/pts"
    mountpoint -q "$CHROOT/run" || mount -t tmpfs tmpfs "$CHROOT/run"
    mkdir -p "$CHROOT/run/systemd/resolve"
    cp -L /etc/resolv.conf "$CHROOT/run/systemd/resolve/stub-resolv.conf" 2>/dev/null || true
    cp -L /etc/resolv.conf "$CHROOT/run/systemd/resolve/resolv.conf" 2>/dev/null || true
}

umount_chroot() {
    for m in run dev/pts dev sys proc; do
        mountpoint -q "$CHROOT/$m" && umount -lf "$CHROOT/$m" || true
    done
}

# Run a command inside the chroot with the (optional) build proxy configured for apt.
in_chroot() {
    local envs=(DEBIAN_FRONTEND=noninteractive LC_ALL=C.UTF-8 HOME=/root PATH=/usr/sbin:/usr/bin:/sbin:/bin)
    if [ -n "$BUILD_HTTPS_PROXY" ]; then
        envs+=(https_proxy="$BUILD_HTTPS_PROXY" HTTPS_PROXY="$BUILD_HTTPS_PROXY")
    fi
    chroot "$CHROOT" /usr/bin/env -i "${envs[@]}" "$@"
}

apt_in_chroot() {
    local opts=(-y -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)
    if [ -n "$BUILD_HTTPS_PROXY" ]; then
        opts+=(-o "Acquire::https::Proxy=$BUILD_HTTPS_PROXY")
        [ -n "$BUILD_PROXY_CA" ] && opts+=(-o "Acquire::https::CaInfo=/etc/ssl/build-proxy-ca.crt")
    fi
    in_chroot apt-get "${opts[@]}" "$@"
}

prepare_build_proxy() {
    if [ -n "$BUILD_PROXY_CA" ]; then
        cp "$BUILD_PROXY_CA" "$CHROOT/etc/ssl/build-proxy-ca.crt"
    fi
}

cleanup_build_proxy() {
    rm -f "$CHROOT/etc/ssl/build-proxy-ca.crt"
}

# Prevent services from starting inside the chroot while packages install.
policy_rc_on() {
    printf '#!/bin/sh\nexit 101\n' > "$CHROOT/usr/sbin/policy-rc.d"
    chmod +x "$CHROOT/usr/sbin/policy-rc.d"
}
policy_rc_off() { rm -f "$CHROOT/usr/sbin/policy-rc.d"; }

write_sources() { # $1 = main mirror URL
    local main="$1" sec="${1/archive.ubuntu.com/security.ubuntu.com}"
    rm -f "$CHROOT/etc/apt/sources.list"
    cat > "$CHROOT/etc/apt/sources.list.d/ubuntu.sources" <<EOF2
Types: deb
URIs: $main
Suites: $SUITE $SUITE-updates $SUITE-backports
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg

Types: deb
URIs: $sec
Suites: $SUITE-security
Components: main restricted universe multiverse
Signed-By: /usr/share/keyrings/ubuntu-archive-keyring.gpg
EOF2
}
set_build_sources() {
    write_sources "$BUILD_MIRROR"
    apt_in_chroot update
}
set_final_sources() { write_sources "$MIRROR"; }
