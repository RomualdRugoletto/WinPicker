# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Single-instance GTK application (daemon): receives shortcut commands over D-Bus."""
import sys
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gio, GLib, Gtk  # noqa: E402

from . import emoji_data, symbols  # noqa: E402
from .clipboard_history import ClipboardHistory  # noqa: E402
from .i18n import _  # noqa: E402
from .state import UserState  # noqa: E402
from .tabs import ClipboardTab, GridItem, GridTab  # noqa: E402
from .window import TABS, PickerWindow  # noqa: E402
from .x11 import X11  # noqa: E402

APP_ID = "io.github.RomualdRugoletto.WinPicker"  # also used by bin/winpicker
PASTE_DELAY_MS = 120  # gives the target window time to get focus back
RESTORE_DELAY_MS = 600  # after inserting an emoji, the previous clipboard content is restored


class WinPicker(Gtk.Application):
    def __init__(self):
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.HANDLES_COMMAND_LINE)
        self.add_main_option(
            "show", ord("s"), GLib.OptionFlags.NONE, GLib.OptionArg.STRING,
            _("Tab to show:") + " " + "|".join(t[0] for t in TABS), _("TAB"),
        )
        self.add_main_option("quit", ord("q"), GLib.OptionFlags.NONE, GLib.OptionArg.NONE, _("Stop the daemon"), None)
        self.window = None
        self.target = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        self.hold()  # keep the daemon alive even with no visible window

        css = Gtk.CssProvider()
        css.load_from_path(str(Path(__file__).with_name("style.css")))
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), css, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.x11 = X11()
        self.state = UserState()
        self.history = ClipboardHistory()
        self.window = PickerWindow(self, self._build_tabs())
        self.window.warm_up()

        show = Gio.SimpleAction.new("show", GLib.VariantType.new("s"))
        show.connect("activate", lambda _a, param: self.show(param.get_string()))
        self.add_action(show)
        quit_action = Gio.SimpleAction.new("quit", None)
        quit_action.connect("activate", lambda *_: self.quit())
        self.add_action(quit_action)

    def _build_tabs(self):
        emojis = emoji_data.load_emojis()
        emoji_sections = []
        for category, label, _icon in emoji_data.CATEGORIES:
            items = [GridItem(e.char, e.search, e.name, emoji=e) for e in emojis if e.category == category]
            if items:
                emoji_sections.append((label, items))

        def grid(sections):
            return [(title, [GridItem(text, search) for text, search in items]) for title, items in sections]

        common = {"on_pick": self.pick_text, "clear_search": self._clear_search, "state": self.state}
        return {
            "emoji": GridTab("emoji", emoji_sections, per_line=8, css_class="emoji", nav=True, tones=True, **common),
            "kaomoji": GridTab("kaomoji", grid(symbols.kaomoji_sections()), per_line=2, css_class="kaomoji", **common),
            "symbols": GridTab("symbols", grid(symbols.symbol_sections()), per_line=8, css_class="symbol", **common),
            "clipboard": ClipboardTab(self.history, on_pick=self.pick_clip),
        }

    def _clear_search(self):
        self.window.search.set_text("")

    def do_command_line(self, command_line):
        options = command_line.get_options_dict().end().unpack()
        if options.get("quit"):
            self.quit()
        elif "show" in options:
            self.show(options["show"])
        return 0

    def do_activate(self):
        pass  # launched without arguments: just start the daemon

    # --- display ---------------------------------------------------------
    def show(self, tab_id: str):
        if tab_id not in self.window.tabs:
            print(_("Unknown tab: {tab}").format(tab=tab_id), file=sys.stderr)
            return
        if self.window.is_active():
            if self.window.current_tab_id == tab_id:
                self.window.hide()  # same shortcut pressed again = close
            else:
                self.window.select_tab(tab_id)
            return
        self.target = self.x11.active_window()
        self.window.popup(tab_id)

    # --- insertion -------------------------------------------------------
    def pick_text(self, tab_id: str, text: str):
        """Emoji / kaomoji / symbol: pasted without polluting the history, then the clipboard is restored."""
        self.state.add_recent(tab_id, text)
        previous = self.history.current
        self.history.set_text_untracked(text)
        self._paste(restore=previous)

    def pick_clip(self, item):
        self.history.copy(item)
        self._paste()

    def _paste(self, restore=None):
        target = self.target
        self.window.hide()
        if not target or target == self.window.xid():
            return  # no target window: the content simply stays on the clipboard

        def send_paste():
            self.x11.send_paste(target)
            if restore:
                GLib.timeout_add(RESTORE_DELAY_MS, restore_clipboard)
            return False

        def restore_clipboard():
            self.history.copy(restore)
            return False

        def refocus_target():
            if self.x11.active_window() != target:
                self.x11.activate(target)
                GLib.timeout_add(PASTE_DELAY_MS, send_paste)
            else:
                send_paste()
            return False

        GLib.timeout_add(PASTE_DELAY_MS, refocus_target)


def main():
    GLib.set_prgname("winpicker")
    return WinPicker().run(sys.argv)
