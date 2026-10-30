# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Loads emoji from the IBus dictionaries (names in the system language + English keywords)."""
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import gi

gi.require_version("IBus", "1.0")
from gi.repository import IBus  # noqa: E402

from .i18n import _, system_languages  # noqa: E402

DICT_DIR = Path("/usr/share/ibus/dicts")

# (IBus category, displayed label, navigation bar icon)
CATEGORIES = [
    ("Smileys & Emotion", _("Smileys & emotion"), "😀"),
    ("People & Body", _("People & body"), "👋"),
    ("Animals & Nature", _("Animals & nature"), "🐻"),
    ("Food & Drink", _("Food & drink"), "🍔"),
    ("Travel & Places", _("Travel & places"), "🚗"),
    ("Activities", _("Activities"), "⚽"),
    ("Objects", _("Objects"), "💡"),
    ("Symbols", _("Symbols"), "💟"),
    ("Flags", _("Flags"), "🏁"),
]

SKIN_TONES = ["\U0001F3FB", "\U0001F3FC", "\U0001F3FD", "\U0001F3FE", "\U0001F3FF"]
VS16 = "\ufe0f"


def normalize(text: str) -> str:
    """Lowercase without accents or ligatures, for a forgiving search ("coeur" finds "cœur")."""
    decomposed = unicodedata.normalize("NFD", text.lower().replace("œ", "oe").replace("æ", "ae"))
    return "".join(c for c in decomposed if unicodedata.category(c) != "Mn")


@dataclass
class Emoji:
    char: str
    name: str
    category: str
    search: str
    tones: dict = field(default_factory=dict)  # skin tone modifier -> variant

    def with_tone(self, tone: str) -> str:
        return self.tones.get(tone, self.char) if tone else self.char


def _load(lang: str):
    path = DICT_DIR / f"emoji-{lang}.dict"
    if not path.exists():
        return []
    try:
        return IBus.EmojiData.load(str(path)) or []
    except Exception:
        return []


def load_emojis() -> list[Emoji]:
    """Emoji named in the first system language that has an IBus dictionary (English otherwise)."""
    lang = next((lang for lang in system_languages() if (DICT_DIR / f"emoji-{lang}.dict").exists()), "en")
    english = {e.get_emoji().replace(VS16, ""): e for e in _load("en")}
    by_key: dict[str, Emoji] = {}
    variants: list[tuple[str, str, str]] = []  # (base key, tone, emoji)

    for entry in _load(lang):
        char = entry.get_emoji()
        category = entry.get_category()
        if category not in dict((c[0], c) for c in CATEGORIES):
            continue  # "Component" (bare modifiers) and uncategorized entries
        key = char.replace(VS16, "")

        tones = {t for t in SKIN_TONES if t in key}
        if tones:
            # Keep only single-tone variants, attached to their base emoji
            if len(tones) == 1:
                tone = tones.pop()
                variants.append((key.replace(tone, ""), tone, char))
            continue

        if key in by_key:
            # Same emoji with/without variation selector: keep the fully-qualified form
            if char.count(VS16) > by_key[key].char.count(VS16):
                by_key[key].char = char
            continue

        words = [entry.get_description(), *entry.get_annotations()]
        if key in english:
            en = english[key]
            words += [en.get_description(), *en.get_annotations()]
        by_key[key] = Emoji(char, entry.get_description(), category, normalize(" ".join(words)))

    for base_key, tone, char in variants:
        base = by_key.get(base_key)
        if base and (tone not in base.tones or char.count(VS16) > base.tones[tone].count(VS16)):
            base.tones[tone] = char

    return list(by_key.values())
