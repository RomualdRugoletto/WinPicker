#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
# Removes everything install.sh set up. Keeps ~/.local/share/winpicker (pinned, recent items)
# unless --purge is given.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DATA_DIR="${XDG_DATA_HOME:-$HOME/.local/share}/winpicker"

"$ROOT/bin/winpicker" quit || true
rm -f "$HOME/.local/bin/winpicker" "$HOME/.config/autostart/winpicker.desktop"

python3 - <<'EOF'
from gi.repository import Gio

schema, base_path = "org.cinnamon.desktop.keybindings", "/org/cinnamon/desktop/keybindings/custom-keybindings"
keys = ["winpicker-emoji", "winpicker-clipboard"]
settings = Gio.Settings.new(schema)
settings.set_strv("custom-list", [k for k in settings.get_strv("custom-list") if k not in keys])
for key in keys:
    entry = Gio.Settings.new_with_path(f"{schema}.custom-keybinding", f"{base_path}/{key}/")
    for name in ("name", "command", "binding"):
        entry.reset(name)
Gio.Settings.sync()
EOF

if [[ -f "$DATA_DIR/ibus-emoji-hotkey.bak" ]]; then
  gsettings set org.freedesktop.ibus.panel.emoji hotkey "$(cat "$DATA_DIR/ibus-emoji-hotkey.bak")"
  rm "$DATA_DIR/ibus-emoji-hotkey.bak"
  echo "IBus emoji shortcut restored."
fi

[[ "${1:-}" == "--purge" ]] && rm -rf "$DATA_DIR"
echo "WinPicker uninstalled."
