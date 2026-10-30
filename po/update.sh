#!/usr/bin/env bash
# SPDX-License-Identifier: GPL-3.0-or-later
# Maintainers: re-extract translatable strings into po/winpicker.pot and merge them into every po/*.po.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/.."

xgettext --language=Python --keyword=_ --from-code=UTF-8 --add-comments=Translators \
  --package-name=WinPicker --msgid-bugs-address=https://github.com/RomualdRugoletto/WinPicker/issues \
  --output=po/winpicker.pot winpicker/*.py
for po in po/*.po; do
  [[ -e "$po" ]] || continue
  msgmerge --quiet --update --backup=none "$po" po/winpicker.pot
done
