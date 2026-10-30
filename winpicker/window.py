# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Windows 11-style floating window: tabs on top, search, content."""
import gi

gi.require_version("GdkX11", "3.0")
from gi.repository import Gdk, GdkX11, GLib, Gtk  # noqa: E402

from .emoji_data import normalize  # noqa: E402
from .i18n import _  # noqa: E402

# (id, tab label, tooltip, search placeholder)
TABS = [
    ("emoji", "😀", _("Emoji"), _("Search emoji")),
    ("kaomoji", ";-)", _("Kaomoji"), _("Search kaomoji")),
    ("symbols", "Ω", _("Symbols"), _("Search symbols")),
    ("clipboard", "📋", _("Clipboard history"), _("Search clipboard history")),
]
WIDTH, HEIGHT = 380, 470
SEARCH_DEBOUNCE_MS = 70


class PickerWindow(Gtk.ApplicationWindow):
    def __init__(self, app, tabs: dict):
        super().__init__(application=app, title="WinPicker")
        self.tabs = tabs
        self.set_decorated(False)
        self.set_resizable(False)
        self.set_skip_taskbar_hint(True)
        self.set_skip_pager_hint(True)
        self.set_keep_above(True)
        self.get_style_context().add_class("winpicker")
        visual = self.get_screen().get_rgba_visual()
        if visual:  # rounded corners and shadow: needs a compositor (Cinnamon has one)
            self.set_visual(visual)
            self.set_app_paintable(True)

        frame = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        frame.get_style_context().add_class("picker-frame")
        frame.set_size_request(WIDTH, HEIGHT)
        self.add(frame)

        tab_bar = Gtk.Box(spacing=2)
        self.tab_buttons = {}
        group = None
        for tab_id, label, tooltip, _placeholder in TABS:
            button = Gtk.RadioButton(label=label, group=group, draw_indicator=False, can_focus=False)
            group = group or button
            button.set_tooltip_text(tooltip)
            button.get_style_context().add_class("tab")
            button.connect("toggled", self._on_tab_toggled, tab_id)
            tab_bar.pack_start(button, False, False, 0)
            self.tab_buttons[tab_id] = button
        frame.pack_start(tab_bar, False, False, 0)

        self.search = Gtk.SearchEntry()
        self.search.connect("search-changed", self._on_search_changed)
        frame.pack_start(self.search, False, False, 0)

        self.stack = Gtk.Stack(transition_type=Gtk.StackTransitionType.NONE, vexpand=True)
        for tab_id, *_ in TABS:
            self.stack.add_named(tabs[tab_id], tab_id)
        frame.pack_start(self.stack, True, True, 0)

        self._debounce_id = 0
        self.connect("key-press-event", self._on_key)
        self.connect("set-focus", lambda _w, widget: widget and self.current_tab.ensure_visible(widget))
        self.connect("notify::is-active", self._on_active_changed)
        self.connect("delete-event", lambda *_: self.hide() or True)
        frame.show_all()

    @property
    def current_tab_id(self) -> str:
        return self.stack.get_visible_child_name()

    @property
    def current_tab(self):
        return self.stack.get_visible_child()

    def xid(self) -> int | None:
        window = self.get_window()
        return window.get_xid() if window else None

    # --- display ---------------------------------------------------------
    def warm_up(self):
        """Invisible first show at startup: GTK lays out the ~1900 emoji there (≈ 0.6 s).
        Without it, the first Win+. would lose the first keystrokes."""
        self._set_invisible(True)
        self.move(-10000, -10000)
        self.show()
        GLib.timeout_add(800, self._end_warm_up)

    def _end_warm_up(self):
        if self.get_visible() and not self.is_active():  # unless a real popup happened meanwhile
            self.hide()
        return False

    def _set_invisible(self, invisible: bool):
        self.set_opacity(0 if invisible else 1)
        self.set_accept_focus(not invisible)
        self.set_focus_on_map(not invisible)

    def popup(self, tab_id: str):
        self._set_invisible(False)
        self.search.set_text("")
        self.select_tab(tab_id)
        for tab in self.tabs.values():
            tab.on_show()
        self._place_near_pointer()
        self.realize()
        self.show()
        # Server timestamp: lets the window manager grant us focus
        self.present_with_time(GdkX11.x11_get_server_time(self.get_window()))
        self.search.grab_focus()

    def select_tab(self, tab_id: str):
        self.tab_buttons[tab_id].set_active(True)
        self._apply_tab(tab_id)

    def _place_near_pointer(self):
        display = Gdk.Display.get_default()
        _screen, x, y = display.get_default_seat().get_pointer().get_position()
        area = display.get_monitor_at_point(x, y).get_workarea()
        width, height = self.get_preferred_size()[1].width, self.get_preferred_size()[1].height
        if y + height > area.y + area.height:
            y -= height  # no room below the pointer: open above it
        x = min(max(area.x, x - 24), area.x + area.width - width)
        y = min(max(area.y, y), area.y + area.height - height)
        self.move(x, y)

    def _on_active_changed(self, *_):
        if not self.is_active() and self.get_visible():
            self.hide()  # losing focus closes the window, like a menu

    # --- tabs and search -------------------------------------------------
    def _on_tab_toggled(self, button, tab_id):
        if button.get_active():
            self._apply_tab(tab_id)

    def _apply_tab(self, tab_id):
        self.stack.set_visible_child_name(tab_id)
        placeholder = next(t[3] for t in TABS if t[0] == tab_id)
        self.search.set_placeholder_text(placeholder)
        self.current_tab.filter(normalize(self.search.get_text().strip()))
        self.search.grab_focus_without_selecting()

    def _on_search_changed(self, _entry):
        if self._debounce_id:
            GLib.source_remove(self._debounce_id)
        self._debounce_id = GLib.timeout_add(SEARCH_DEBOUNCE_MS, self._run_search)

    def _run_search(self):
        self._debounce_id = 0
        self.current_tab.filter(normalize(self.search.get_text().strip()))
        return False

    def _cycle_tab(self, step):
        ids = [t[0] for t in TABS]
        self.select_tab(ids[(ids.index(self.current_tab_id) + step) % len(ids)])

    # --- keyboard --------------------------------------------------------
    def _on_key(self, _window, event):
        key = event.keyval
        ctrl = event.state & Gdk.ModifierType.CONTROL_MASK

        if key == Gdk.KEY_Escape:
            if self.search.get_text():
                self.search.set_text("")
            else:
                self.hide()
            return True
        if ctrl and key in (Gdk.KEY_Tab, Gdk.KEY_Page_Down):
            self._cycle_tab(1)
            return True
        if ctrl and key in (Gdk.KEY_ISO_Left_Tab, Gdk.KEY_Page_Up):
            self._cycle_tab(-1)
            return True

        if self.search.has_focus():
            if key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter):
                if self._debounce_id:  # search not applied yet: apply it first
                    GLib.source_remove(self._debounce_id)
                    self._run_search()
                self.current_tab.activate_first()
                return True
            if key == Gdk.KEY_Down:
                self.current_tab.focus_content()
                return True
            return False

        # Focus in the grid/list: any "text" keystroke goes to the search entry
        printable = (not ctrl and Gdk.keyval_to_unicode(key) > 0x20) or key == Gdk.KEY_BackSpace
        if printable and self.search.handle_event(event):
            self.search.grab_focus_without_selecting()
            return True
        return False
