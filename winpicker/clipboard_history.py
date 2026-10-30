# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Clipboard history: monitoring, deduplication, pinning and persistence.

Same as Windows: 25 items max (pinned ones excluded), and only pinned items survive
a daemon restart.
"""
import hashlib
import json
import os
import time
from dataclasses import dataclass
from pathlib import Path

from gi.repository import Gdk, GdkPixbuf, Gtk

MAX_ITEMS = 25
MAX_TEXT_LENGTH = 1_000_000
DATA_DIR = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "winpicker"
PINNED_FILE = DATA_DIR / "pinned.json"

# Targets set by password managers (KeePassXC, etc.): such copies are not recorded
SENSITIVE_TARGETS = {"x-kde-passwordManagerHint"}


@dataclass
class ClipItem:
    kind: str  # "text" | "image"
    key: str  # fingerprint used for deduplication
    text: str | None = None
    pixbuf: GdkPixbuf.Pixbuf | None = None
    pinned: bool = False
    ts: float = 0.0


def _text_key(text: str) -> str:
    return "t:" + hashlib.sha1(text.encode()).hexdigest()


def _image_key(pixbuf: GdkPixbuf.Pixbuf) -> str:
    h = hashlib.sha1(pixbuf.get_pixels())
    h.update(f"{pixbuf.get_width()}x{pixbuf.get_height()}".encode())
    return "i:" + h.hexdigest()


class ClipboardHistory:
    def __init__(self):
        self.items: list[ClipItem] = []
        self.current: ClipItem | None = None  # item matching the current clipboard content
        self.listeners = []
        self.clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        self._ignored_text: str | None = None
        self._load_pinned()
        self.clipboard.connect("owner-change", self._on_owner_change)

    # --- subscription -----------------------------------------------------
    def subscribe(self, callback):
        self.listeners.append(callback)

    def _notify(self):
        for callback in self.listeners:
            callback()

    # --- reading the clipboard -------------------------------------------
    def _on_owner_change(self, clipboard, _event):
        clipboard.request_targets(self._on_targets)

    def _on_targets(self, clipboard, targets, _n):
        if not targets or {t.name() for t in targets} & SENSITIVE_TARGETS:
            self.current = None
            return
        if Gtk.targets_include_text(targets):
            clipboard.request_text(self._on_text)
        elif Gtk.targets_include_image(targets, False):
            clipboard.request_image(self._on_image)

    def _on_text(self, _clipboard, text):
        if text is None or not text.strip() or len(text) > MAX_TEXT_LENGTH:
            return
        if self._ignored_text is not None and text == self._ignored_text:
            self._ignored_text = None
            return
        self._add(ClipItem("text", _text_key(text), text=text))

    def _on_image(self, _clipboard, pixbuf):
        if pixbuf is not None:
            self._add(ClipItem("image", _image_key(pixbuf), pixbuf=pixbuf))

    def _add(self, item: ClipItem):
        existing = next((i for i in self.items if i.key == item.key), None)
        if existing:
            self.items.remove(existing)
            item.pinned = existing.pinned
        item.ts = time.time()
        self.items.insert(0, item)
        self.current = item
        self._trim()
        self._notify()

    def _trim(self):
        unpinned = [i for i in self.items if not i.pinned]
        for item in unpinned[MAX_ITEMS:]:
            self.items.remove(item)

    # --- writing to the clipboard ----------------------------------------
    def set_text_untracked(self, text: str):
        """Put a text (emoji, symbol…) on the clipboard without adding it to the history."""
        self._ignored_text = text
        self.current = None
        self.clipboard.set_text(text, -1)

    def copy(self, item: ClipItem):
        if item.kind == "text":
            self.clipboard.set_text(item.text, -1)
        else:
            self.clipboard.set_image(item.pixbuf)

    # --- user actions ----------------------------------------------------
    def toggle_pin(self, item: ClipItem):
        item.pinned = not item.pinned
        self._trim()
        self._save_pinned()
        self._notify()

    def remove(self, item: ClipItem):
        self.items.remove(item)
        if item.pinned:
            self._save_pinned()
        self._notify()

    def clear(self):
        self.items = [i for i in self.items if i.pinned]
        self._notify()

    # --- persistence of pinned items -------------------------------------
    def _save_pinned(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True, mode=0o700)
        entries, kept_images = [], set()
        for item in self.items:
            if not item.pinned:
                continue
            entry = {"kind": item.kind, "ts": item.ts}
            if item.kind == "text":
                entry["text"] = item.text
            else:
                filename = item.key[2:] + ".png"
                if not (DATA_DIR / filename).exists():
                    item.pixbuf.savev(str(DATA_DIR / filename), "png", [], [])
                entry["file"] = filename
                kept_images.add(filename)
            entries.append(entry)
        for png in DATA_DIR.glob("*.png"):
            if png.name not in kept_images:
                png.unlink()
        tmp = PINNED_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(entries, ensure_ascii=False, indent=1))
        tmp.chmod(0o600)
        tmp.replace(PINNED_FILE)

    def _load_pinned(self):
        try:
            entries = json.loads(PINNED_FILE.read_text())
        except (OSError, ValueError):
            return
        for entry in entries:
            try:
                if entry["kind"] == "text":
                    item = ClipItem("text", _text_key(entry["text"]), text=entry["text"])
                else:
                    pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(DATA_DIR / entry["file"]))
                    item = ClipItem("image", _image_key(pixbuf), pixbuf=pixbuf)
            except Exception:
                continue
            item.pinned, item.ts = True, entry.get("ts", 0.0)
            self.items.append(item)
