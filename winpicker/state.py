# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Persisted preferences: recently used items per tab and skin tone."""
import json

from .clipboard_history import DATA_DIR

STATE_FILE = DATA_DIR / "state.json"
MAX_RECENT = 24


class UserState:
    def __init__(self):
        try:
            data = json.loads(STATE_FILE.read_text())
        except (OSError, ValueError):
            data = {}
        self._recent: dict[str, list[str]] = data.get("recent", {})
        self._tone: str = data.get("tone", "")

    def recent(self, tab: str) -> list[str]:
        return self._recent.get(tab, [])

    def add_recent(self, tab: str, text: str):
        self._recent[tab] = ([text] + [t for t in self.recent(tab) if t != text])[:MAX_RECENT]
        self._save()

    @property
    def tone(self) -> str:
        return self._tone

    @tone.setter
    def tone(self, value: str):
        self._tone = value
        self._save()

    def _save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        STATE_FILE.write_text(json.dumps({"recent": self._recent, "tone": self._tone}, ensure_ascii=False))
