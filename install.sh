#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
# Installs WinPicker for the current user (no sudo):
#  - compiled translations
#  - ~/.local/bin/winpicker command
#  - autostart at login
#  - Cinnamon shortcuts Super+. / Super+; (emoji) and Super+V (clipboard)
#  - disables the IBus emoji shortcut, which already grabs Super+. and Super+;
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LAUNCHER="$ROOT/bin/winpicker"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/winpicker"

if [[ "${XDG_SESSION_TYPE:-x11}" != "x11" ]]; then
  echo "Warning: WinPicker needs an X11 session (current session: $XDG_SESSION_TYPE)." >&2
fi

"$ROOT/po/compile.sh"

chmod +x "$LAUNCHER"
mkdir -p "$HOME/.local/bin" "$HOME/.config/autostart" "$DATA_DIR"
ln -sf "$LAUNCHER" "$HOME/.local/bin/winpicker"

cat > "$HOME/.config/autostart/winpicker.desktop" <<EOF
[Desktop Entry]
Type=Application
Name=WinPicker
Comment=Emoji picker and clipboard history (Super+. / Super+V)
Exec=$LAUNCHER daemon
Icon=face-smile
X-GNOME-Autostart-enabled=true
EOF

python3 - "$LAUNCHER" <<'EOF'
import sys
from gi.repository import Gio

launcher = sys.argv[1]
schema, base_path = "org.cinnamon.desktop.keybindings", "/org/cinnamon/desktop/keybindings/custom-keybindings"
bindings = [
    ("winpicker-emoji", "WinPicker: emoji", f"{launcher} emoji", ["<Super>period", "<Super>semicolon"]),
    ("winpicker-clipboard", "WinPicker: clipboard", f"{launcher} clipboard", ["<Super>v"]),
]
settings = Gio.Settings.new(schema)
custom = list(settings.get_strv("custom-list"))
for key, name, command, keys in bindings:
    entry = Gio.Settings.new_with_path(f"{schema}.custom-keybinding", f"{base_path}/{key}/")
    entry.set_string("name", name)
    entry.set_string("command", command)
    entry.set_strv("binding", keys)
    if key not in custom:
        custom.append(key)
settings.set_strv("custom-list", custom)
Gio.Settings.sync()
EOF

# IBus grabs Super+. and Super+; for its own picker: back up the value, then free them
IBUS_SCHEMA=org.freedesktop.ibus.panel.emoji
if gsettings list-keys "$IBUS_SCHEMA" &>/dev/null; then
  current="$(gsettings get "$IBUS_SCHEMA" hotkey)"
  if [[ "$current" != "@as []" && "$current" != "[]" ]]; then
    echo "$current" > "$DATA_DIR/ibus-emoji-hotkey.bak"
    gsettings set "$IBUS_SCHEMA" hotkey "[]"
    echo "IBus emoji shortcut disabled (previous value: $current)."
  fi
fi

# (Re)start the daemon right away, detached from the terminal
"$LAUNCHER" quit || true
sleep 0.5
setsid nohup "$LAUNCHER" daemon >/dev/null 2>&1 &

echo "WinPicker installed: Super+. (or Super+;) for emoji, Super+V for the clipboard history."
