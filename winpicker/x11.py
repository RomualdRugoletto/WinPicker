# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Low-level X11 access: active window, re-activation and simulated Ctrl+V (XTEST)."""
from Xlib import X, XK, display, protocol
from Xlib.ext import xtest

# Applications where pasting is done with Ctrl+Shift+V
TERMINALS = {
    "gnome-terminal-server", "gnome-terminal", "x-terminal-emulator", "xfce4-terminal",
    "mate-terminal", "tilix", "terminator", "konsole", "kitty", "alacritty", "wezterm",
    "org.wezfurlong.wezterm", "guake", "tilda", "sakura", "lxterminal", "qterminal",
    "terminology", "xterm", "urxvt", "st-256color", "foot", "ghostty", "com.mitchellh.ghostty",
}

# Modifiers possibly still held down (e.g. Super) that would corrupt the simulated Ctrl+V
STRAY_MODIFIERS = ["Super_L", "Super_R", "Alt_L", "Alt_R", "ISO_Level3_Shift", "Shift_L", "Shift_R"]


class X11:
    def __init__(self):
        self.d = display.Display()
        self.root = self.d.screen().root
        self.NET_ACTIVE_WINDOW = self.d.intern_atom("_NET_ACTIVE_WINDOW")

    def _keycode(self, name: str) -> int:
        return self.d.keysym_to_keycode(XK.string_to_keysym(name))

    def active_window(self) -> int | None:
        prop = self.root.get_full_property(self.NET_ACTIVE_WINDOW, X.AnyPropertyType)
        return int(prop.value[0]) if prop and prop.value and prop.value[0] else None

    def wm_class(self, wid: int) -> str:
        try:
            cls = self.d.create_resource_object("window", wid).get_wm_class()
            return " ".join(cls).lower() if cls else ""
        except Exception:
            return ""

    def is_terminal(self, wid: int) -> bool:
        return any(part in TERMINALS for part in self.wm_class(wid).split())

    def activate(self, wid: int):
        # source=2 ("pager"): bypasses the window manager's focus-stealing prevention
        event = protocol.event.ClientMessage(
            window=self.d.create_resource_object("window", wid),
            client_type=self.NET_ACTIVE_WINDOW,
            data=(32, [2, X.CurrentTime, 0, 0, 0]),
        )
        self.root.send_event(event, event_mask=X.SubstructureRedirectMask | X.SubstructureNotifyMask)
        self.d.flush()

    def _release_stray_modifiers(self):
        keymap = self.d.query_keymap()
        for name in STRAY_MODIFIERS:
            code = self._keycode(name)
            if code and keymap[code // 8] & (1 << (code % 8)):
                xtest.fake_input(self.d, X.KeyRelease, code)

    def send_paste(self, wid: int):
        keys = ["Control_L", "Shift_L", "v"] if self.is_terminal(wid) else ["Control_L", "v"]
        codes = [self._keycode(k) for k in keys]
        self._release_stray_modifiers()
        for code in codes:
            xtest.fake_input(self.d, X.KeyPress, code)
        for code in reversed(codes):
            xtest.fake_input(self.d, X.KeyRelease, code)
        self.d.sync()
