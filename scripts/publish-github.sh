#!/bin/bash
# Publish the WinLow XP ISO (and its checksum) as a GitHub release (run only with the repository owner's consent).
# Usage: publish-github.sh <owner/repo> <iso> [tag]
# GitHub release assets must be under 2 GiB each; a larger ISO is split into parts.
set -euo pipefail
REPO="$1"; ISO="$2"; TAG="${3:-v1.0}"
NAME=$(basename "$ISO")
WORK=$(mktemp -d)
trap 'rm -rf "$WORK"' EXIT

gh repo view "$REPO" >/dev/null 2>&1 || \
    gh repo create "$REPO" --private --description "WinLow XP — sistem de operare cu desktop clasic (Ubuntu 26.04 LTS)"

( cd "$(dirname "$ISO")" && sha256sum "$NAME" ) > "$WORK/$NAME.sha256"
LIMIT=$((2 * 1024 * 1024 * 1024 - 64 * 1024 * 1024))
ASSETS=("$WORK/$NAME.sha256")
if [ "$(stat -c %s "$ISO")" -lt "$LIMIT" ]; then
    ASSETS+=("$ISO")
else
    ( cd "$WORK" && split -b 1900M -d -a 3 --numeric-suffixes=1 "$ISO" "$NAME." )
    cat > "$WORK/CUM-SE-UNESC.txt" <<EOF
Fișierul ISO este împărțit în părți (limita GitHub este de 2 GB pe fișier).
Windows:      copy /b $NAME.001 + $NAME.002 $NAME     (în Command Prompt, în dosarul cu părțile)
Linux/macOS:  cat $NAME.0* > $NAME
Verificare:   suma SHA-256 trebuie să fie cea din $NAME.sha256
EOF
    ASSETS+=("$WORK/$NAME".0* "$WORK/CUM-SE-UNESC.txt")
fi

NOTES="$(dirname "$0")/../RELEASE-NOTES.md"
[ -f "$NOTES" ] || NOTES="$(dirname "$0")/../README.md"
gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1 || \
    gh release create "$TAG" --repo "$REPO" --title "WinLow XP ${TAG#v}" --notes-file "$NOTES"
gh release upload "$TAG" --repo "$REPO" --clobber "${ASSETS[@]}"
gh release view "$TAG" --repo "$REPO" --json url,assets --jq '.url, (.assets[] | .name + "  " + .url)'
