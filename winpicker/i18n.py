# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Translations (gettext) following the system language."""
import gettext
import locale
import os
from pathlib import Path

DOMAIN = "winpicker"
# Compiled catalogs (.mo), built from po/*.po by po/compile.sh
LOCALE_DIR = Path(__file__).resolve().parent.parent / "locale"

try:
    locale.setlocale(locale.LC_ALL, "")
except locale.Error:
    pass

_ = gettext.translation(DOMAIN, LOCALE_DIR, fallback=True).gettext


def system_languages() -> list[str]:
    """Preferred languages, most specific first (e.g. ["fr_CA", "fr"]), using the same
    environment variables as gettext."""
    value = next((os.environ[v] for v in ("LANGUAGE", "LC_ALL", "LC_MESSAGES", "LANG") if os.environ.get(v)), "")
    languages = []
    for entry in value.split(":"):
        code = entry.split(".")[0].split("@")[0]
        if code in ("", "C", "POSIX"):
            continue
        for candidate in (code, code.split("_")[0]):
            if candidate not in languages:
                languages.append(candidate)
    return languages
