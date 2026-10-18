#!/bin/bash
# Developer helper: after stage 40, build a variant of the ISO whose squashfs uses fast zstd compression.
# Same files, same boot setup — only quicker to unpack, which makes installer tests in slow
# emulated VMs (QEMU without KVM) practical. Not for release.
source "$(dirname "$0")/lib.sh"
TEST_DIR="$BUILD_DIR/iso-test"
NAME="${1:-teios-test-zstd.iso}"
[ -f "$ISO_DIR/casper/filesystem.squashfs" ] || { echo "run stage 40 first"; exit 1; }
rm -rf "$TEST_DIR"
cp -al "$ISO_DIR" "$TEST_DIR"           # hard links: no extra space for the unchanged files
rm -f "$TEST_DIR/casper/filesystem.squashfs"
mksquashfs "$CHROOT" "$TEST_DIR/casper/filesystem.squashfs" -noappend -no-progress -comp zstd -Xcompression-level 3 -b 1M \
    -e boot/grub/grub.cfg -wildcards -e 'proc/*' -e 'sys/*' -e 'dev/*' -e 'run/*' -e 'tmp/*' -e 'mnt/*' -e 'media/*' \
    -e 'var/cache/apt/archives/*.deb' -e 'lost+found'
xorriso -as mkisofs -r -V "TEIOS_TEST" -J -joliet-long -l -iso-level 3 -o "$OUT_DIR/$NAME" \
    --grub2-mbr "$BUILD_DIR/boot_hybrid.img" -partition_offset 16 --mbr-force-bootable \
    -append_partition 2 28732ac11ff8d211ba4b00a0c93ec93b "$BUILD_DIR/efi.img" -appended_part_as_gpt \
    -iso_mbr_part_type a2a0d0ebe5b9334487c068b6b72699c7 -c '/boot.catalog' \
    -b '/boot/grub/i386-pc/eltorito.img' -no-emul-boot -boot-load-size 4 -boot-info-table --grub2-boot-info \
    -eltorito-alt-boot -e '--interval:appended_partition_2:::' -no-emul-boot "$TEST_DIR"
rm -rf "$TEST_DIR"
ls -la "$OUT_DIR/$NAME"
