#!/bin/bash
# Developer helper: start the desktop from the chroot in a virtual screen and capture the five
# screenshots used by the installer slideshow (artwork/screens/1-start.png … 5-welcome.png).
# Needs: Xvfb, xdotool, ImageMagick (import). Run after stage 30, before stage 40.
set -uo pipefail
HERE="$(cd "$(dirname "$0")" && pwd)"
source "$HERE/lib.sh"
set +e
OUT="$TEI_ROOT/artwork/screens"
SHOW_NAME="${SHOW_NAME:-Ana Pop}"
export DISPLAY=:5
X() { xdotool "$@"; }
shot() { import -window root "$OUT/$1"; echo "captured $1"; }
wait_win() { # wait_win <name regex> [timeout s]
    local t=0
    until xdotool search --onlyvisible --name "$1" >/dev/null 2>&1; do sleep 1; t=$((t + 1)); [ $t -ge "${2:-60}" ] && return 1; done
    sleep 2
}
close_active() { X key --clearmodifiers alt+F4; sleep 2; }

mkdir -p "$OUT"
# show a friendly name in the Start menu instead of "root" (restored at the end)
OLD_GECOS=$(chroot "$CHROOT" getent passwd root | cut -d: -f5)
chroot "$CHROOT" usermod -c "$SHOW_NAME" root

"$HERE/test-session.sh" start >/dev/null
for i in $(seq 1 90); do pgrep -x xfce4-panel >/dev/null && break; sleep 1; done
wait_win "Bun venit" 90
sleep 6
shot 5-welcome.png
close_active

# Start menu
X mousemove 30 755 click 1; sleep 4
shot 1-start.png
X key Escape; sleep 2

# Control Panel
"$HERE/test-session.sh" run tei-control-panel
wait_win "Panou de control" 60 && shot 2-control-panel.png
close_active

# System Properties → Computer Name tab
"$HERE/test-session.sh" run tei-system-properties --computer-name
wait_win "Proprietăți sistem" 60 && shot 4-system.png
close_active

# Word processor with a short text
"$HERE/test-session.sh" run libreoffice --writer --norestore --nologo
if wait_win "LibreOffice Writer" 120; then
    sleep 6
    X key --clearmodifiers Escape; sleep 1
    X type --delay 30 "Raport trimestrial"; X key Return
    X type --delay 20 "Vanzarile au crescut cu 12% fata de anul trecut. Documentul se salveaza implicit ca .docx."
    sleep 3
    shot 3-apps.png
    X key --clearmodifiers ctrl+q; sleep 2
    X key --clearmodifiers alt+n 2>/dev/null; sleep 2   # "Don't Save"
fi

"$HERE/test-session.sh" stop >/dev/null
pkill -x soffice.bin 2>/dev/null || true
chroot "$CHROOT" usermod -c "${OLD_GECOS:-root}" root
rm -rf "$CHROOT/tmp/tei-test"
ls -la "$OUT"
