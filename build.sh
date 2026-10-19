#!/bin/bash
# WinLow XP — build the installable live ISO from scratch.
#
# Requirements: an Ubuntu 24.04 or 26.04 machine/VM (e.g. a Hyper-V VM), ~40 GB free disk,
# internet access, root.  Usage:   sudo ./build.sh            (all stages)
#                                  sudo ./build.sh 30 40      (only some stages)
# Output: build/out/teios-<version>-amd64.iso
set -euo pipefail
cd "$(dirname "$0")"
export TEI_ROOT="$PWD"
export BUILD_DIR="${BUILD_DIR:-$PWD/build}"
export CHROOT="$BUILD_DIR/chroot" ISO_DIR="$BUILD_DIR/iso" OUT_DIR="$BUILD_DIR/out"
# Use https mirrors while building (works behind most proxies); the image keeps plain Ubuntu mirrors.
export BUILD_MIRROR="${BUILD_MIRROR:-https://archive.ubuntu.com/ubuntu}"

[ "$(id -u)" = 0 ] || { echo "Rulați cu sudo / run as root"; exit 1; }

need=(debootstrap mksquashfs xorriso mkfs.msdos mcopy rsvg-convert oggenc python3 convert strip)
missing=()
for b in "${need[@]}"; do command -v "$b" >/dev/null || missing+=("$b"); done
if [ ${#missing[@]} -gt 0 ]; then
    apt-get update
    apt-get install -y --no-install-recommends debootstrap squashfs-tools xorriso dosfstools mtools \
        librsvg2-bin vorbis-tools python3 python3-pil python3-numpy imagemagick fonts-noto-core rsync zstd binutils
fi
[ -e /usr/share/debootstrap/scripts/resolute ] || ln -sf gutsy /usr/share/debootstrap/scripts/resolute

stages=("$@")
[ ${#stages[@]} -gt 0 ] || stages=(10 20 30 40)
mkdir -p "$BUILD_DIR"
for s in "${stages[@]}"; do
    script=$(ls scripts/${s}-*.sh)
    echo "=================== $script ==================="
    bash "$script" 2>&1 | tee "$BUILD_DIR/stage-$s.log"
done
echo
echo "ISO: $(ls "$OUT_DIR"/*.iso)"
