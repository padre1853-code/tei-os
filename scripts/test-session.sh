#!/bin/bash
# Developer helper: run the Tei desktop from the chroot inside a virtual X server and take screenshots.
source "$(dirname "$0")/lib.sh"
ACTION="${1:-start}"
DISP=":5"
RES="${RES:-1366x768}"
case "$ACTION" in
start)
    mount_chroot
    pgrep -f "Xvfb $DISP" >/dev/null || (Xvfb $DISP -screen 0 ${RES}x24 -nolisten tcp >/tmp/xvfb.log 2>&1 &)
    sleep 2
    mkdir -p "$CHROOT/tmp/.X11-unix"
    mountpoint -q "$CHROOT/tmp/.X11-unix" || mount --bind /tmp/.X11-unix "$CHROOT/tmp/.X11-unix"
    rm -rf "$CHROOT/tmp/tei-test"; mkdir -p "$CHROOT/tmp/tei-test"
    chroot "$CHROOT" /usr/bin/env -i HOME=/tmp/tei-test USER=root DISPLAY=$DISP LANG=${TLANG:-ro_RO.UTF-8} LANGUAGE=${TLANGUAGE:-ro:en} \
        PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin XDG_RUNTIME_DIR=/tmp/tei-test/run \
        sh -c 'mkdir -p /tmp/tei-test/run; chmod 700 /tmp/tei-test/run; exec dbus-run-session -- /usr/bin/tei-session' >/tmp/tei-session.log 2>&1 &
    echo started
    ;;
run) # run a command inside the session
    shift
    chroot "$CHROOT" /usr/bin/env -i HOME=/tmp/tei-test DISPLAY=$DISP LANG=${TLANG:-ro_RO.UTF-8} LANGUAGE=${TLANGUAGE:-ro:en} \
        PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin XDG_RUNTIME_DIR=/tmp/tei-test/run \
        XDG_CONFIG_DIRS=/etc/xdg/teios:/etc/xdg XDG_DATA_DIRS=/usr/share/teios:/usr/local/share:/usr/share \
        GTK_OVERLAY_SCROLLING=0 QT_QPA_PLATFORMTHEME=gtk3 \
        DBUS_SESSION_BUS_ADDRESS="$(tr '\0' '\n' < /proc/$(pgrep -x xfce4-session | head -1)/environ | sed -n 's/^DBUS_SESSION_BUS_ADDRESS=//p')" "$@" >>/tmp/tei-run.log 2>&1 &
    ;;
shot)
    out="${2:-/tmp/claude-0/shot.png}"
    DISPLAY=$DISP import -window root "$out" && echo "$out"
    ;;
stop)
    pkill -f "dbus-run-session -- /usr/bin/tei-session" || true
    for p in xfce4-session xfwm4 xfce4-panel xfdesktop xfconfd Thunar thunar xfsettingsd xfce4-notifyd xfce4-power-manager nm-applet blueman-applet; do pkill -x "$p" 2>/dev/null || true; done
    pkill -f "Xvfb $DISP" || true
    for p in xdg-document-po xdg-permission- xdg-desktop-por gvfsd gvfsd-fuse gvfsd-metadata gvfsd-trash gvfsd-computer gvfs-udisks2-vo gvfs-goa-volume gvfs-gphoto2-vo gvfs-mtp-volume gvfs-afc-volume at-spi-bus-laun at-spi2-registr pipewire wireplumber pipewire-pulse; do pkill -x "$p" 2>/dev/null || true; done
    sleep 1
    grep "$CHROOT/tmp/tei-test" /proc/mounts | awk '{print $2}' | sort -r | while read m; do umount -l "$m" 2>/dev/null || fusermount -uz "$m" 2>/dev/null; done || true
    umount -lf "$CHROOT/tmp/.X11-unix" 2>/dev/null || true
    umount_chroot
    echo stopped
    ;;
esac
