#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
DESKTOP_FILE="$HOME/.local/share/applications/nutripuncture-desk.desktop"

mkdir -p "$(dirname "$DESKTOP_FILE")"

cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=Nutripuncture Desk
Comment=Memoire therapeutique locale
Exec=bash "$ROOT_DIR/scripts/start_app.sh"
Path=$ROOT_DIR
Icon=$ROOT_DIR/src-tauri/icons/icon.png
Terminal=false
Categories=Office;MedicalSoftware;
EOF

chmod +x "$DESKTOP_FILE"
echo "Lanceur installe: $DESKTOP_FILE"
