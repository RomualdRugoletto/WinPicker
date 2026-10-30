# SPDX-License-Identifier: GPL-3.0-or-later
# Copyright (C) 2026 Romuald Rugoletto
"""Tab contents: grids (emoji, kaomoji, symbols) and clipboard history.

Every tab exposes the same small interface, used by the window:
filter(query), activate_first(), focus_content(), on_show(), ensure_visible(widget).
"""
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk, Pango

from .emoji_data import SKIN_TONES, normalize
from .i18n import _


def _matches(query: str, haystack: str) -> bool:
    """Every query word appears anywhere in the text (clipboard search)."""
    return all(word in haystack for word in query.split())


def _matches_word_start(query: str, keywords: str) -> bool:
    """Every query word starts a keyword: "cat" finds 🐱 but not "avocat" (grid search)."""
    return all(" " + word in keywords for word in query.split())


def _scroll_into_view(scroller: Gtk.ScrolledWindow, content: Gtk.Widget, widget: Gtk.Widget):
    coords = widget.translate_coordinates(content, 0, 0)
    if coords is None:
        return
    y, height = coords[1], widget.get_allocated_height()
    adj = scroller.get_vadjustment()
    if y < adj.get_value():
        adj.set_value(max(0, y - 4))
    elif y + height > adj.get_value() + adj.get_page_size():
        adj.set_value(y + height - adj.get_page_size() + 4)


class GridItem:
    def __init__(self, text: str, search: str = "", tooltip: str | None = None, emoji=None):
        self.text, self.search, self.tooltip, self.emoji = text, " " + normalize(search), tooltip, emoji

    def display(self, tone: str) -> str:
        return self.emoji.with_tone(tone) if self.emoji else self.text


class GridTab(Gtk.Box):
    """Sectioned grid, with a "recently used" section and an optional navigation bar."""

    def __init__(self, tab_id, sections, *, per_line, css_class, on_pick, clear_search, state, nav=False, tones=False):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.tab_id, self.on_pick, self.clear_search, self.state = tab_id, on_pick, clear_search, state
        self.per_line = per_line
        self.query = ""
        self.get_style_context().add_class(css_class)

        self.scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
        self.content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.scroller.add(self.content)
        self.pack_start(self.scroller, True, True, 0)

        self.recent_header, self.recent_box = self._add_section(_("Recently used"))
        self.sections = []  # (header, flowbox, items)
        for title, items in sections:
            header, box = self._add_section(title)
            for item in items:
                self._add_child(box, item)
            self.sections.append((header, box, items))

        self.no_result = Gtk.Label(label=_("No results"), margin=24)
        self.no_result.get_style_context().add_class("dim-label")
        self.content.pack_start(self.no_result, False, False, 0)
        self.no_result.set_no_show_all(True)

        if nav or tones:
            self.pack_start(self._build_bottom_bar(nav, tones), False, False, 0)

    # --- building ----------------------------------------------------------
    def _add_section(self, title):
        header = Gtk.Label(label=title, xalign=0)
        header.get_style_context().add_class("section-title")
        box = Gtk.FlowBox(
            homogeneous=True,
            selection_mode=Gtk.SelectionMode.NONE,
            activate_on_single_click=True,
            min_children_per_line=self.per_line,
            max_children_per_line=self.per_line,
            valign=Gtk.Align.START,
        )
        box.set_filter_func(self._filter_child)
        box.connect("child-activated", lambda _b, child: self.on_pick(self.tab_id, child.item.display(self.state.tone)))
        self.content.pack_start(header, False, False, 0)
        self.content.pack_start(box, False, False, 0)
        return header, box

    def _add_child(self, box, item: GridItem):
        child = Gtk.FlowBoxChild()
        child.item = item
        child.add(Gtk.Label(label=item.display(self.state.tone)))
        if item.tooltip:
            child.set_tooltip_text(item.tooltip)
        box.add(child)
        return child

    def _build_bottom_bar(self, nav, tones):
        bar = Gtk.Box(spacing=2)
        bar.get_style_context().add_class("navbar")
        if nav:
            for header, _box, items in self.sections:
                button = Gtk.Button(label=items[0].text, relief=Gtk.ReliefStyle.NONE, can_focus=False)
                button.set_tooltip_text(header.get_label())
                button.connect("clicked", lambda _b, h=header: self._jump_to(h))
                bar.pack_start(button, True, True, 0)
        if tones:
            bar.pack_end(self._build_tone_button(), False, False, 0)
        return bar

    def _build_tone_button(self):
        self.tone_button = Gtk.MenuButton(relief=Gtk.ReliefStyle.NONE, can_focus=False)
        self.tone_button.set_tooltip_text(_("Skin tone"))
        self.tone_button.add(Gtk.Label(label="✋" + self.state.tone))
        popover = Gtk.Popover()
        row = Gtk.Box(spacing=2, margin=4)
        for tone in [""] + SKIN_TONES:
            button = Gtk.Button(label="✋" + tone, relief=Gtk.ReliefStyle.NONE)
            button.connect("clicked", lambda _b, t=tone: (self._set_tone(t), popover.popdown()))
            row.pack_start(button, False, False, 0)
        row.show_all()
        popover.add(row)
        self.tone_button.set_popover(popover)
        return self.tone_button

    def _set_tone(self, tone):
        self.state.tone = tone
        self.tone_button.get_child().set_text("✋" + tone)
        for _h, box, _items in self.sections:
            for child in box.get_children():
                if child.item.emoji and child.item.emoji.tones:
                    child.get_child().set_text(child.item.display(tone))

    def _jump_to(self, header):
        def scroll():
            coords = header.translate_coordinates(self.content, 0, 0)
            if coords:
                self.scroller.get_vadjustment().set_value(coords[1])
            return False

        if self.query:
            self.clear_search()  # the window re-filters; wait for the new layout before scrolling
            GLib.timeout_add(80, scroll)
        else:
            scroll()

    # --- common tab interface --------------------------------------------
    def on_show(self):
        for child in self.recent_box.get_children():
            child.destroy()
        recent = self.state.recent(self.tab_id)
        for text in recent:
            self._add_child(self.recent_box, GridItem(text))
        self.recent_box.show_all()
        self._update_visibility()
        self.scroller.get_vadjustment().set_value(0)

    def filter(self, query: str):
        self.query = query
        for _h, box, _items in self.sections:
            box.invalidate_filter()
        self._update_visibility()
        self.scroller.get_vadjustment().set_value(0)

    def _filter_child(self, child):
        return not self.query or _matches_word_start(self.query, child.item.search)

    def _update_visibility(self):
        show_recent = not self.query and bool(self.state.recent(self.tab_id))
        self.recent_header.set_visible(show_recent)
        self.recent_box.set_visible(show_recent)
        any_visible = show_recent
        for header, box, items in self.sections:
            visible = not self.query or any(_matches_word_start(self.query, i.search) for i in items)
            header.set_visible(visible)
            box.set_visible(visible)
            any_visible |= visible
        self.no_result.set_visible(not any_visible)

    def _first_visible_child(self):
        boxes = [self.recent_box] if self.recent_box.get_visible() else []
        boxes += [box for _h, box, _i in self.sections if box.get_visible()]
        for box in boxes:
            for child in box.get_children():
                if self._filter_child(child) or box is self.recent_box:
                    return child
        return None

    def activate_first(self):
        child = self._first_visible_child()
        if child:
            child.emit("activate")

    def focus_content(self):
        child = self._first_visible_child()
        if child:
            child.grab_focus()

    def ensure_visible(self, widget):
        _scroll_into_view(self.scroller, self.content, widget)


class ClipboardTab(Gtk.Box):
    THUMB_WIDTH, THUMB_HEIGHT = 300, 110

    def __init__(self, history, on_pick):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        self.history, self.on_pick = history, on_pick
        self.query = ""

        header = Gtk.Box()
        title = Gtk.Label(label=_("Clipboard history"), xalign=0)
        title.get_style_context().add_class("section-title")
        clear = Gtk.Button(label=_("Clear all"), relief=Gtk.ReliefStyle.NONE, can_focus=False)
        clear.set_tooltip_text(_("Removes everything except pinned items"))
        clear.connect("clicked", lambda _b: history.clear())
        header.pack_start(title, True, True, 0)
        header.pack_end(clear, False, False, 0)
        self.pack_start(header, False, False, 0)

        self.listbox = Gtk.ListBox(selection_mode=Gtk.SelectionMode.NONE)
        self.listbox.set_filter_func(self._filter_row)
        self.listbox.connect("row-activated", lambda _l, row: self.on_pick(row.item))
        self.listbox.connect("key-press-event", self._on_key)
        self.scroller = Gtk.ScrolledWindow(hscrollbar_policy=Gtk.PolicyType.NEVER, vexpand=True)
        self.scroller.add(self.listbox)

        empty = Gtk.Label(
            label=_("Nothing here yet.\n\nCopy some text or an image\nand it will show up here."),
            justify=Gtk.Justification.CENTER,
        )
        empty.get_style_context().add_class("dim-label")
        self.stack = Gtk.Stack(vexpand=True)
        self.stack.add_named(self.scroller, "list")
        self.stack.add_named(empty, "empty")
        self.pack_start(self.stack, True, True, 0)

        history.subscribe(self.rebuild)
        self.rebuild()

    def rebuild(self):
        for row in self.listbox.get_children():
            row.destroy()
        for item in self.history.items:
            self.listbox.add(self._make_row(item))
        self.listbox.show_all()
        self.stack.set_visible_child_name("list" if self.history.items else "empty")

    def _make_row(self, item):
        row = Gtk.ListBoxRow()
        row.item = item
        card = Gtk.Box(spacing=6)
        card.get_style_context().add_class("clip-card")

        if item.kind == "text":
            preview = item.text.strip().replace("\t", "    ")[:600]
            content = Gtk.Label(
                label=preview, xalign=0, hexpand=True, wrap=True, lines=3,
                max_width_chars=36, wrap_mode=Pango.WrapMode.WORD_CHAR, ellipsize=Pango.EllipsizeMode.END,
            )
        else:
            content = Gtk.Image.new_from_pixbuf(self._thumbnail(item.pixbuf))
            content.set_halign(Gtk.Align.START)
            content.set_hexpand(True)
        card.pack_start(content, True, True, 0)

        actions = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, valign=Gtk.Align.START)
        pin = Gtk.Button.new_from_icon_name("view-pin-symbolic", Gtk.IconSize.BUTTON)
        pin.set_tooltip_text(_("Unpin") if item.pinned else _("Pin"))
        pin.get_style_context().add_class("pin")
        if item.pinned:
            card.get_style_context().add_class("pinned")
        delete = Gtk.Button.new_from_icon_name("user-trash-symbolic", Gtk.IconSize.BUTTON)
        delete.set_tooltip_text(_("Delete (Del)"))
        for button, action in ((pin, self.history.toggle_pin), (delete, self.history.remove)):
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_can_focus(False)
            button.connect("clicked", lambda _b, a=action: a(item))
            actions.pack_start(button, False, False, 0)
        card.pack_end(actions, False, False, 0)

        row.add(card)
        return row

    def _thumbnail(self, pixbuf):
        w, h = pixbuf.get_width(), pixbuf.get_height()
        scale = min(self.THUMB_WIDTH / w, self.THUMB_HEIGHT / h, 1)
        return pixbuf.scale_simple(max(1, int(w * scale)), max(1, int(h * scale)), GdkPixbuf.InterpType.BILINEAR)

    def _on_key(self, _listbox, event):
        row = self.get_toplevel().get_focus()
        if event.keyval == Gdk.KEY_Delete and isinstance(row, Gtk.ListBoxRow):
            index = row.get_index()
            self.history.remove(row.item)
            neighbour = self.listbox.get_row_at_index(min(index, len(self.history.items) - 1))
            if neighbour:
                neighbour.grab_focus()
            return True
        return False

    def _filter_row(self, row):
        if not self.query:
            return True
        return row.item.kind == "text" and _matches(self.query, normalize(row.item.text))

    # --- common tab interface --------------------------------------------
    def on_show(self):
        self.scroller.get_vadjustment().set_value(0)

    def filter(self, query: str):
        self.query = query
        self.listbox.invalidate_filter()

    def _first_visible_row(self):
        return next((r for r in self.listbox.get_children() if self._filter_row(r)), None)

    def activate_first(self):
        row = self._first_visible_row()
        if row:
            self.on_pick(row.item)

    def focus_content(self):
        row = self._first_visible_row()
        if row:
            row.grab_focus()

    def ensure_visible(self, widget):
        _scroll_into_view(self.scroller, self.listbox, widget)
