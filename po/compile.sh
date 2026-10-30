#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Compiles po/*.po into locale/<lang>/LC_MESSAGES/winpicker.mo (run by install.sh).
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

if ! command -v msgfmt >/dev/null; then
  echo "msgfmt not found (package 'gettext'): the interface will be in English." >&2
  exit 0
fi
for po in po/*.po; do
  [[ -e "$po" ]] || continue
  lang="$(basename "$po" .po)"
  mkdir -p "locale/$lang/LC_MESSAGES"
  msgfmt --check --output-file="locale/$lang/LC_MESSAGES/winpicker.mo" "$po"
done
